#!/bin/bash
set -e

# NOTE: Playwright installation disabled until FCP check is re-enabled
# echo "Installing Playwright browsers..."
# playwright install --with-deps chromium

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
