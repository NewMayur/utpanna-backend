#!/bin/bash

# Run database migrations
# python -c "from app import db; db.create_all()"

# Start the application using the PORT environment variable
exec gunicorn -b 0.0.0.0:${PORT:-8080} app:app