# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.in /app/

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade pip-tools
RUN pip-compile requirements.in --upgrade
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./BTC/ /app/


# Define the command to run the application
# Replace `app.py` with your script and adjust the command as needed
CMD ["python", "main.py"]
