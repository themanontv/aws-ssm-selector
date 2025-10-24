!#/bin/bash

pip3 install -r src/requirements.txt

cp src/aws-connect.py /usr/local/bin/aws-connect
chmod +x /usr/local/bin/aws-connect