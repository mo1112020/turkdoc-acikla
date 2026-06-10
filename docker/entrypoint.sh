#!/bin/sh
set -e

mkdir -p /app/data/uploads

if [ "$#" -eq 0 ]; then
  exec uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
fi

exec "$@"
