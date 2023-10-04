# Create a Dockerfile to containerize your Flask application:

# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /flask_app
WORKDIR /flask_app

# Copy the current directory contents into the container at /flask_app
COPY . /flask_app

# Install any needed packages specified in requirements.txt
# requirements.txt is a text file commonly used in Python projects to specify the dependencies (i.e., libraries or packages) that are required for the project to run. 
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "flask_app.py"]