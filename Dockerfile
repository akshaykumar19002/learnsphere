# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code
COPY . /code/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the command to start uWSGI
CMD ["uwsgi", "--http", ":8000", "--wsgi-file", "learnsphere/wsgi.py", "--static-map", "/static=/static", "--master", "--processes", "4", "--threads", "2"]
