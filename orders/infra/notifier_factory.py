import os
from .notifiers import RealEmailNotifier, MockEmailNotifier, SMSNotifier


class NotificationFactory:
    """
    Factory para instanciar el notificador correcto según
    el entorno (ENV_TYPE) o el canal requerido.
    Desacopla el servicio de la implementación concreta.
    """

    @staticmethod
    def get_notifier(channel: str = "email"):
        env = os.getenv("ENV_TYPE", "DEV")

        if channel == "email":
            if env == "PROD":
                return RealEmailNotifier()
            return MockEmailNotifier()

        if channel == "sms":
            return SMSNotifier()

        raise ValueError(f"Unsupported notification channel: '{channel}'")