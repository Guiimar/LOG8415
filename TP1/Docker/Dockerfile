# Create a Dockerfile to containerize your the application:

# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

COPY ./LOG8415/TP1/Docker/* ./app/Docker/

COPY ./LOG8415/TP1/Credentials.ini ./app/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "./Docker/Benchemarking_main.py"]
