#!/usr/bin/env python3
"""
aws-connect.py
Simple interactive tool to select an AWS profile and an EC2 instance,
then open an SSM session to the selected instance.

Requirements:
    * simple_term_menu
    * click
    * aws-vault (ish)

Usage:
    Run the script and select a profile and instance from the interactive menus.
"""

import os
import sys
import re
import json
import shutil
import subprocess
import click
from simple_term_menu import TerminalMenu

def is_executable(file_path):
    """
    is_executable(file_path)
    Return True if file_path names an executable found by the system (via PATH lookup), otherwise False.
    Parameters
    file_path (str): Command name or path to check.
    Returns
    bool: True when shutil.which(file_path) locates a file and os.access(..., os.X_OK) is true; otherwise False.
    """

    executable_path = shutil.which(file_path)
    
    # Check if the executable path is not None and is executable
    if executable_path and os.access(executable_path, os.X_OK):
        return True
    else:
        return False
   

def preview(selection):
    """
    Build and return a multi-line preview string for a selected instance entry.

    Args:
        selection (str): The menu entry string containing the instance id in parentheses.

    Returns:
        str: Multi-line details about the instance (Id, Type, State, AZ, Launch Time, IP).
        Returns None if the instance is not found in instance_data.
    """

    match = re.search(instance_regex, selection)
    selection = match.group(1)

    preview = []

    for reservation in instance_data:
        for instance in reservation['Instances']:
            # If the instance id matches the current selection then use this item
            if instance["InstanceId"] == selection:
                preview.append("Id: " + instance["InstanceId"])
                preview.append("Type: " + instance["InstanceType"])
                state = instance["State"]["Name"]
                preview.append("State: " + state)
                preview.append("AZ: " + instance["Placement"]["AvailabilityZone"])
                preview.append("Launch Time: " + instance["LaunchTime"])
                if state == "running":
                    ip = instance["PrivateIpAddress"]
                    preview.append("IP: " + ip)
                else:
                    preview.append("IP: NONE")
                return '\n'.join(preview)

# Set this variable to get your user directory, currently set to work with MacOS
user = "<user>"
file_path = '/Users/' + user + '/.aws/config'

# Try to fetch a profile from the environment
os_profile = os.getenv('AWS_PROFILE')

# Regex Variables
instance_regex = re.compile(r'\(([\-a-z0-9]+)\)')
profile_regex = re.compile(r'\[profile ([a-zA-Z0-9\-]+)\]')

# Special environments list
hidden_environments = ['']
scary_environments = ['production']

if not os_profile and is_executable("aws"):
    # Reading from the ~/.aws/config file to get the profiles
    try:
        with open(file_path, encoding='utf-8') as file:
            text = file.read()
        # Set regex to look for things with profile in it

        profiles = []

        # Split based on new lines and get the first group of the match
        for line in text.splitlines():
            match = re.search(profile_regex, line)
            if match:
                if match.group(1) not in hidden_environments:
                    profiles.append(match.group(1))
    except:
        print("No profiles found ")
        sys.exit()
    # Show the terminal menu for the profile list
    terminal_menu = TerminalMenu(
        menu_entries=profiles,
        title="Select the desired profile ",
        show_search_hint=True,
        menu_highlight_style=("bg_green", "fg_black", "bold")
    )
    try:
        profile = profiles[terminal_menu.show()]
    except TypeError:
        # If type is incorrect likely caused by exiting the menu
        print("Ok, Bye. ")
        sys.exit()
else:
    profile = os_profile

# Set the colour of the highlight and present option to enter
if profile in scary_environments:
    try:
        if click.confirm(profile + ' looks scary, do you want to continue?', default=False, abort=True):
            highlight = "bg_red"
    except click.exceptions.Abort:
        print('I understand. ')
        sys.exit()
else:
    highlight = "bg_green"

# Execute the describe instances command
if is_executable("aws-vault"):
        result = subprocess.run(['aws-vault', 'exec', profile, '--', 'aws', 'ec2', 'describe-instances'], stdout=subprocess.PIPE, check=True)
    else:
        result = subprocess.run(['aws', 'ec2', 'describe-instances', '--profile', profile], stdout=subprocess.PIPE, check=True)

# Parse the JSON
try:
    parsed = json.loads(result.stdout)
except json.decoder.JSONDecodeError:
    print("I don't think you're allowed to do that ")
    sys.exit()
instance_data = parsed['Reservations']

items = []

# Get the names and instance IDs from the JSON
for reservation in instance_data:
    for instance in reservation['Instances']:
        name = ""
        # Get the Name tag value and make it the name
        try:
            for tag in instance["Tags"]:
                if tag["Key"] == "Name":
                    name = tag["Value"]
                else:
                    pass
        except:
            name = ""
        if name == "":
            name = "NONAME"
        id = instance["InstanceId"]
        items.append(f'{name:<30s} ({id:<15s})')

# Show the terminal menu for the instance list
terminal_menu = TerminalMenu(
    menu_entries=items,
    title="Select an instance in " + profile + " ",
    show_search_hint=True,
    preview_command=preview,
    preview_title="Details",
    menu_highlight_style=(highlight, "fg_black", "bold")
)
index_2 = terminal_menu.show()

try:
    match = re.search(instance_regex, items[index_2])
except TypeError:
    # If type is incorrect likely caused by exiting the menu
    print("No Instance selected ")
    sys.exit()
id = match.group(1)

# Execute the describe instances command
if is_executable("aws-vault"):
        os.system('aws-vault exec ' + profile + ' -- aws ssm start-session --target ' + id)
    else:
        os.system('aws ssm start-session --target ' + id ' --profile ' + profile)
