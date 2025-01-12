# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy everything from your project folder to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app will run on
EXPOSE 8080

# Define the command to start your app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]