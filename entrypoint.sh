#!/bin/sh

# Apply database migrations
python -c "from app import db; db.create_all()"

# Start the application
exec "$@"