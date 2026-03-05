import os
<<<<<<< HEAD
from .notifiers import RealEmailNotifier, MockEmailNotifier
=======
from orders.infra.notifiers import RealEmailNotifier, MockEmailNotifier
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)


class NotifierFactory:

    @staticmethod
<<<<<<< HEAD
    def create():
        env = os.getenv("ENV_TYPE", "DEV")

        if env == "PROD":
            return RealEmailNotifier()
        return MockEmailNotifier()
=======
    def get_notifier(type):
        if type == "email":
            return RealEmailNotifier()
        elif type == "sms":
            return MockEmailNotifier()
        else:
            raise ValueError("Invalid notifier type")
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
