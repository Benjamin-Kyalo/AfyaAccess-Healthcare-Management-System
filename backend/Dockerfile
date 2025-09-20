# Use slim Python base
FROM python:3.11-slim

# install build deps for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy requirements first for docker caching
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy project
COPY . /code

# Make entrypoint executable
RUN chmod +x /code/entrypoint.sh

EXPOSE 8000

# Entrypoint will run migrations and start the server
ENTRYPOINT ["/code/entrypoint.sh"]
