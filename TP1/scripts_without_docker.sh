#!/bin/bash
git clone https://github.com/Guiimar/LOG8415.git
cd LOG8415/TP1
# Define new AWS credentials
new_aws_access_key="key"
new_aws_secret_key="secret"
new_aws_token_key="token"

# Pour aws_access_key_id
sed -i "s#aws_access_key_id=.*#aws_access_key_id=${new_aws_access_key}#" credentials.ini

# Pour aws_secret_access_key
sed -i "s#aws_secret_access_key=.*#aws_secret_access_key=${new_aws_secret_key}#" credentials.ini

# Pour aws_session_token
sed -i "s#aws_session_token=.*#aws_session_token=${new_aws_token_key}#" credentials.ini

cp credentials.ini docker/

# Install requirements from requirements.txt

pip install boto3

#Execute la création des instances
cd Setup
python3 Setup_main.py

cd ..

cd Docker

pip install -r requirements.txt

python3 Benchemarking_main.py
