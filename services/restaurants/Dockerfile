# ── Imagen base ────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Evitar archivos .pyc y buffering en logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Dependencias ───────────────────────────────────────────────────────────
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# ── Código fuente ──────────────────────────────────────────────────────────
COPY app.py .

# ── Puerto expuesto ────────────────────────────────────────────────────────
EXPOSE 5001

# ── Arranque con Gunicorn (producción) ─────────────────────────────────────
# 2 workers es suficiente para este microservicio liviano.
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "60", "app:app"]
