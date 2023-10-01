#Install Python Virtualenv

sudo apt-get update
sudo apt-get install python3-venv

#Create directory

mkdir flaskapp && cd flaskapp 

#Create the virtual environment

python3 -m venv venv

#Activate the virtual environment

source venv/bin/activate

#Install Flask

pip install Flask

#Create of a simple Flask app:

sudo vi flask_app.py

#Add the code bellow to flask_app.py

from flask import Flask

app = Flask(__name__)

@app.route("/")
def my_app():
    return 'Cluster 1 Instance 1 responding'

if __name__=='__main__':
    app.run()


python flask_app.py

#Install Gunicorn:

pip install gunicorn

#Run Gunicorn:

gunicorn -b 0.0.0.0:8000 flask_app:app 

#Create a file system containing service instructions:

sudo nano /etc/systemd/system/flaskapp.service

#Add the config instructions into the file:

[Unit]
Description=Gunicorn instance for a simple check of running
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/flaskapp
ExecStart=/home/ubuntu/flaskapp/venv/bin/gunicorn -b localhost:8000 flask_app:app
Restart=always
[Install]
WantedBy=multi-user.target

#Enable the service:

sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp

#Check the app is running using:

curl localhost:8000

#Install nginx:

sudo apt-get install nginx

#Start the Nginx service :

sudo systemctl start nginx
sudo systemctl enable nginx

#Edit /etc/nginx/sites-available/default and add the codes below:

sudo nano /etc/nginx/sites-available/default

#Add the following below the "Default Server Configuration" :

upstream flaskhrunninginstance {
    server 127.0.0.1:8000;
}

#Add a proxy_pass to flaskhrunninginstance at "location" /

location / {
    proxy_pass http://flaskhrunninginstance ;
}

#Restart nginx:

sudo systemctl restart nginx

#Go to the public address of your instance to show the message of the Flask app