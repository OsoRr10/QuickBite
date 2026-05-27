FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir psycopg2-binary gunicorn

COPY . .

EXPOSE 8000

# compilemessages compila los .po → .mo para i18n
CMD ["sh", "-c", "python manage.py compilemessages && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py seed && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]
