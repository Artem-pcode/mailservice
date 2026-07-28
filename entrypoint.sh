#!/bin/sh
set -e

echo "Ждём готовности базы данных..."
until python -c "
import sys
import psycopg2
from urllib.parse import urlparse, urlunparse
import os

url = os.environ['DATABASE_URL_SYNC'].replace('postgresql+psycopg2', 'postgresql')
try:
    conn = psycopg2.connect(url)
    conn.close()
except Exception as e:
    sys.exit(1)
"; do
  echo "БД ещё не готова, ждём 1 секунду..."
  sleep 1
done

echo "БД доступна. Прогоняем миграции Alembic..."
alembic upgrade head

echo "Стартуем uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
