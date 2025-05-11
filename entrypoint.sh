#!/bin/sh

python manage.py migrate
echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting server..."
daphne -b 0.0.0.0 -p 8000 EasyChatProject.asgi:application



