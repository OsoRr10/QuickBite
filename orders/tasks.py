"""
tasks.py — Tareas asíncronas de QuickBite
------------------------------------------
Estas tareas se ejecutan en background por el Celery worker.
Django las encola en Redis y responde al cliente inmediatamente,
sin esperar a que terminen.

Tareas disponibles:
  - send_order_notification  → notifica al usuario cuando se crea una orden
  - send_payment_notification → notifica confirmación de pago
  - generate_order_report    → genera reporte de órdenes del día (simulado)
"""

import logging
from config.celery import app as celery_app
from .infra.notifier_factory import NotificationFactory

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_order_notification(self, order_id: int, user_email: str, total: float):
    """
    Envía notificación de orden creada en background.

    bind=True         → acceso a self para reintentos
    max_retries=3     → reintenta hasta 3 veces si falla
    default_retry_delay=10 → espera 10s entre reintentos
    """
    try:
        logger.info(f"[CELERY] Enviando notificación orden #{order_id} a {user_email}")

        notifier = NotificationFactory.get_notifier("email")
        notifier.send(
            recipient=user_email,
            message=f"Tu orden #{order_id} fue creada exitosamente. Total: ${total:.2f}",
        )

        logger.info(f"[CELERY] Notificación orden #{order_id} enviada OK")
        return {"status": "sent", "order_id": order_id}

    except Exception as exc:
        logger.error(f"[CELERY] Error enviando notificación orden #{order_id}: {exc}")
        # Reintento automático con backoff exponencial
        raise self.retry(exc=exc, countdown=2**self.request.retries * 10)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_payment_notification(self, order_id: int, user_email: str, amount: float):
    """
    Notifica confirmación de pago en background.
    """
    try:
        logger.info(f"[CELERY] Enviando notificación pago orden #{order_id}")

        notifier = NotificationFactory.get_notifier("email")
        notifier.send(
            recipient=user_email,
            message=f"Tu pago de ${amount:.2f} para la orden #{order_id} fue confirmado.",
        )

        logger.info(f"[CELERY] Notificación pago orden #{order_id} enviada OK")
        return {"status": "sent", "order_id": order_id}

    except Exception as exc:
        logger.error(f"[CELERY] Error notificación pago #{order_id}: {exc}")
        raise self.retry(exc=exc, countdown=2**self.request.retries * 10)


@celery_app.task
def generate_order_report():
    """
    Genera reporte diario de órdenes en background.
    En producción exportaría a CSV/PDF y lo enviaría por email.

    Esta tarea puede programarse con Celery Beat (cron jobs).
    """
    from django.utils import timezone
    from .models import Order

    today = timezone.now().date()
    orders = Order.objects.filter(created_at__date=today)

    total_orders = orders.count()
    total_revenue = sum(
        float(item.unit_price * item.quantity)
        for order in orders
        for item in order.orderitem_set.all()
    )

    report = {
        "date": str(today),
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "statuses": {
            status: orders.filter(status=status).count()
            for status, _ in Order.STATUS_CHOICES
        },
    }

    logger.info(f"[CELERY] Reporte generado: {report}")
    return report
