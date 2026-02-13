import os
from .notifiers import RealEmailNotifier, MockEmailNotifier


class NotifierFactory:

    @staticmethod
    def create():
        env = os.getenv("ENV_TYPE", "DEV")

        if env == "PROD":
            return RealEmailNotifier()
        return MockEmailNotifier()
