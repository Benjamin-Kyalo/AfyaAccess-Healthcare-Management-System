#!/usr/bin/env bash
set -e

# Move to project dir
cd /code

# Wait for DB to be ready, then run migrations in a loop until succeed
echo "Waiting for Postgres..."
until python manage.py migrate --noinput 2>/dev/null; do
  echo "Postgres unavailable - sleeping"
  sleep 2
done

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if env provides credentials? (Optional)
# You can add logic here to autogenerate a superuser if needed.

# Start Gunicorn
exec gunicorn afyaaccess.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
