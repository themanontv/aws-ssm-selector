#!/bin/bash


INSTALLED_FILE=/usr/local/bin/aws-connect
if test -f "$INSTALLED_FILE"; then
    echo "Found installed script at $INSTALLED_FILE... removing it"
    rm $INSTALLED_FILE
fi

REPO_FILE=src/aws-connect.py 
echo "Copying script to /usr/local/bin"
cp $REPO_FILE $INSTALLED_FILE

echo "Introducing the script to you"
sed -i '' "s|<user>|${USER//&/\\&}|" $INSTALLED_FILE

echo "Encouraging the script to be itself"
chmod +x $INSTALLED_FILE

if test -f "$INSTALLED_FILE"; then
    echo "Installed! 🚀"
fi
