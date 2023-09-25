# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11.4-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Install requirements
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./api ./api
COPY requirements.txt .

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
EXPOSE $PORT
# CMD exec gunicorn --bind :$PORT --workers 4 --threads 8 --timeout 0 --log-level 'debug' --preload api.run:app
CMD exec uvicorn api.run:app --host 0.0.0.0 --port $PORT --log-level 'debug'
