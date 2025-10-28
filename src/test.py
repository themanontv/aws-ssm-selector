"""
Robust filterable two-panel TUI using textual.

Behavior:
- Left: filterable list (press '/')
- Right: preview pane that updates as you move highlight
- Enter:
    * When list has focus -> exits and returns highlighted item (via ListView.Selected)
    * When filter Input has focus -> exits and returns the top filtered item (first hit)
    * App fallback: pressing Enter tries to use the last highlighted text
- Esc: cancel filter or exit
"""
import boto3
import json
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, ListView, ListItem
from textual.containers import Horizontal
from textual.reactive import reactive
from typing import Optional

def get_instances():
    ec2 = boto3.client('ec2', region_name="eu-west-1")
    response = ec2.describe_instances()
    print(response)
    instance_data = response['Reservations']
    items = []
    for item in instance_data:
        for instance in item['Instances']:
            items.append(instance["InstanceId"])
            
    return items, instance_data

class ItemPreview(Static):
    content = reactive("")

    def watch_content(self, content: str) -> None:
        self.update(content)


class FilterableList(App):
    CSS = """
    Horizontal { height: 100%; }
    ListView { width: 40%; border: solid white; padding: 1; }
    ItemPreview { width: 60%; border: solid orange; padding: 1; }
    Input { dock: top; border: solid white; }
    """

    BINDINGS = [
        ("escape", "cancel_filter", "Cancel filter mode / Exit"),
        ("/", "start_filter", "Start filtering"),
        ("enter", "select_item", "Select highlighted item (fallback)"),
    ]

    def __init__(self, items: list[str], previews: list[str]):
        super().__init__()
        self.all_items = items
        self.previews = previews
        self.filtered_items = items.copy()
        self.selected_item: Optional[str] = None
        self.filter_mode = False
        self.current_highlighted: Optional[str] = None

    def compose(self) -> ComposeResult:
        self.input = Input(placeholder="Type to filter, Esc to cancel...")
        self.list_view = ListView(*[ListItem(Static(item)) for item in self.all_items])
        self.preview = ItemPreview("Select an item to see its preview")
        yield self.input
        yield Horizontal(self.list_view, self.preview)

    def on_mount(self) -> None:
        self.input.display = False
        self.set_focus(self.list_view)

    # Key actions
    def action_start_filter(self) -> None:
        self.input.display = True
        self.filter_mode = True
        self.input.value = ""
        self.set_focus(self.input)

    def action_cancel_filter(self) -> None:
        if self.filter_mode:
            self.filter_mode = False
            self.input.display = False
            self.filtered_items = self.all_items.copy()
            self._update_list()
            self.set_focus(self.list_view)
        else:
            self.exit(None)

    def action_select_item(self) -> None:
        """Fallback if app-level enter binding is triggered."""
        if self.current_highlighted:
            self.exit(self.current_highlighted)

    # Filtering
    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.lower()
        self.filtered_items = [item for item in self.all_items if query in item.lower()]
        self._update_list()

    def _update_list(self):
        self.list_view.clear()
        self.list_view.mount_all([ListItem(Static(item)) for item in self.filtered_items])
        # reset highlight state; list_view may highlight first automatically depending on version
        self.current_highlighted = None

    # Helper to extract text from a ListItem robustly
    def _extract_text_from_listitem(self, item_widget: ListItem) -> str:
        try:
            static = item_widget.query_one(Static)
            return str(static.renderable)
        except Exception:
            return str(item_widget)

    # When the list highlight changes (arrow keys / mouse)
    def on_list_view_highlighted(self, event) -> None:
        item_widget = getattr(event, "item", None)
        if item_widget is None:
            idx = getattr(event, "index", None) or getattr(event, "item_index", None)
            if idx is not None and 0 <= idx < len(self.list_view.children):
                item_widget = self.list_view.children[idx]
            else:
                # try list_view index
                idx2 = getattr(self.list_view, "index", None)
                if idx2 is not None and 0 <= idx2 < len(self.list_view.children):
                    item_widget = self.list_view.children[idx2]

        if item_widget is None:
            self.current_highlighted = None
            self.preview.content = "(No preview available)"
            return

        item_text = self._extract_text_from_listitem(item_widget)
        self.current_highlighted = item_text

        # find preview by original index
        try:
            orig_idx = self.all_items.index(item_text)
            self.preview.content = self.previews[orig_idx]
        except ValueError:
            self.preview.content = "(No preview available)"

    # --- New: handle Enter when list has focus (ListView.Selected) ---
    def on_list_view_selected(self, event) -> None:
        """
        This event is typically emitted by ListView when Enter is pressed with list focused.
        We'll robustly extract the item and exit with it.
        """
        item_widget = getattr(event, "item", None)
        if item_widget is None:
            idx = getattr(event, "index", None) or getattr(event, "item_index", None)
            if idx is not None and 0 <= idx < len(self.list_view.children):
                item_widget = self.list_view.children[idx]

        if item_widget is None:
            # Fallback to current_highlighted
            if self.current_highlighted:
                self.exit(self.current_highlighted)
            return

        item_text = self._extract_text_from_listitem(item_widget)
        self.exit(item_text)

    # --- New: handle Enter when Input has focus (Input.Submitted) ---
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        When the filter Input has focus and user presses Enter, accept the top filtered item.
        If there are no filtered items, do nothing (or exit None).
        """
        if not self.filtered_items:
            # nothing matches -> just cancel filter (or exit None). We'll cancel filter here.
            self.action_cancel_filter()
            return

        # Use the first item in the filtered list as the selection
        top = self.filtered_items[0]
        self.exit(top)


# Example usage
if __name__ == "__main__":
    items, instance_data = get_instances()
    print(items)
    # items = [f"Item {i}" for i in range(1, 31)]
    previews = [f"This is preview content for Item {i}.\nIt may be multi-line." for i in range(1, 31)]

    app = FilterableList(items, previews)
    result = app.run()

    if result:
        print(f"\n✅ You selected: {result}")
    else:
        print("\n❌ No item selected.")