#!/bin/sh
# Startup script for Azure App Service (Linux) - Django
# Performs migrations, collects static files, then starts the server.
# Uses runserver if DJANGO_DEBUG=1 (for diagnostics), otherwise gunicorn.

set -eu

echo "[startup] Working directory: $(pwd)"
ls -1 || true

APP_DIR="django_app"
if [ ! -d "$APP_DIR" ]; then
  echo "[startup][ERROR] No directory '$APP_DIR' found. Adjust APP_DIR in startup.sh" >&2
  exit 1
fi
cd "$APP_DIR"

echo "[startup] Python version: $(python --version 2>&1)"
echo "[startup] DJANGO_DEBUG=${DJANGO_DEBUG:-0} DB_ENGINE=${DB_ENGINE:-sqlite} PORT=${PORT:-8000}"

# Ensure persistent SQLite dir exists if using sqlite
if [ "${DB_ENGINE:-sqlite}" = "sqlite" ]; then
  if [ -n "${HOME:-}" ] && [ -d "${HOME}" ]; then
    DATA_DIR="${HOME}/site/data"
    mkdir -p "$DATA_DIR"
    echo "[startup] Ensured data directory: $DATA_DIR"
  fi
fi

echo "[startup] Running migrations..."
python manage.py migrate --noinput || {
  echo "[startup][WARN] migrate failed (continuing for debugging)" >&2
}

if [ "${DJANGO_SKIP_COLLECTSTATIC:-0}" != "1" ]; then
  echo "[startup] Collecting static files..."
  python manage.py collectstatic --noinput || {
    echo "[startup][WARN] collectstatic failed (static files may be missing)" >&2
  }
else
  echo "[startup] Skipping collectstatic per DJANGO_SKIP_COLLECTSTATIC=1"
fi

PORT="${PORT:-8000}"

if [ "${DJANGO_DEBUG:-0}" = "1" ]; then
  echo "[startup] DEBUG=1 -> starting Django development server on 0.0.0.0:${PORT}"
  exec python manage.py runserver 0.0.0.0:"${PORT}"
else
  echo "[startup] Starting gunicorn on 0.0.0.0:${PORT} (workers=${WORKERS:-3})"
  exec gunicorn ejecutor.wsgi:application \
    --bind=0.0.0.0:"${PORT}" \
    --workers="${WORKERS:-3}" \
    --timeout="${GUNICORN_TIMEOUT:-120}" \
    --log-level="${GUNICORN_LOG_LEVEL:-info}" \
    --access-logfile '-' \
    --error-logfile '-'
fi
