# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy Credentials.ini from the parent directory to /app/
COPY ../Credentials.ini /app/

# Copy files from ./LOG8415/TP1/Docker/ to /app/Docker/
COPY ./LOG8415/TP1/Docker/* /app/Docker/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run Benchemarking_main.py when the container launches
CMD ["python", "./Docker/Benchemarking_main.py"]
