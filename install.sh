#!/bin/bash
INSTALLED_FILE=/usr/local/bin/aws-connect
REPO_FILE=src/aws_connect.py 

if test -f "$INSTALLED_FILE"; then
    echo "Found installed script at $INSTALLED_FILE... removing it"
    sudo rm $INSTALLED_FILE
fi

echo "Copying script to /usr/local/bin"
sudo cp $REPO_FILE $INSTALLED_FILE

user=$USER
echo "Introducing the script to you"
sudo sed -i '' "s|<user>|${user//&/\\&}|" $INSTALLED_FILE

echo "Encouraging the script to be itself"
sudo chmod +x $INSTALLED_FILE

if test -f "$INSTALLED_FILE"; then
    echo "Installed! 🚀"
fi
