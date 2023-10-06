#!/bin/bash
git clone https://github.com/Guiimar/LOG8415.git
cd LOG8415/TP1
# Define new AWS credentials
new_aws_access_key="youraccesskey"
new_aws_secret_key="yoursecretkey"
new_aws_token_key="yourtokenkey"
# Replace the old AWS credentials with new values
sed -i "s/aws_access_key_id=.*/aws_access_key_id=${new_aws_access_key}/" credentials.ini
sed -i "s/aws_secret_access_key=.*/aws_secret_access_key=${new_aws_secret_key}/" credentials.ini
sed -i "s/aws_session_token=.*/aws_session_token=${new_aws_token_key}/" credentials.ini
docker build -t log8415 .
docker run -it log8415
