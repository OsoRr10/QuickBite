"""
Configuración de Celery para QuickBite
---------------------------------------
Celery usa Redis como broker (cola de mensajes) y como backend
(almacén de resultados de tareas).

Flujo:
  Django  →  encola tarea en Redis  →  Celery worker la procesa
"""

import os
from celery import Celery

# Indicar a Celery qué settings de Django usar
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("quickbite")

# Leer configuración de Celery desde settings.py (prefijo CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Forzar Redis como broker y backend, incluso si la configuración de settings no quedó cargada.
app.conf.broker_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
app.conf.result_backend = os.environ.get("REDIS_URL", "redis://redis:6379/0")

# Auto-descubrir tareas en todos los INSTALLED_APPS (orders/tasks.py)
app.autodiscover_tasks()
