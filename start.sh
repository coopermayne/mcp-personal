#!/bin/sh
set -e

MAX_RETRIES=10
RETRY_INTERVAL=5

echo "Waiting for database to be ready..."

for i in $(seq 1 $MAX_RETRIES); do
    if alembic upgrade head; then
        echo "Migrations completed successfully"
        break
    else
        if [ $i -eq $MAX_RETRIES ]; then
            echo "Failed to run migrations after $MAX_RETRIES attempts"
            exit 1
        fi
        echo "Migration attempt $i failed, retrying in ${RETRY_INTERVAL}s..."
        sleep $RETRY_INTERVAL
    fi
done

echo "Starting server..."
exec uvicorn lifelogger.api.main:app --host 0.0.0.0 --port 8000
