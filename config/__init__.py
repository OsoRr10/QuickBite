# Cargar Celery al iniciar Django para que las tareas se registren correctamente
from .celery import app as celery_app

__all__ = ('celery_app',)
