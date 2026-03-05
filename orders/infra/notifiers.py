class BaseNotifier:
    """Interfaz base para todos los notificadores."""

    def send(self, recipient: str, message: str):
        raise NotImplementedError("Subclasses must implement send()")


class RealEmailNotifier(BaseNotifier):
    def send(self, recipient: str, message: str):
        # En producción aquí iría la integración con SendGrid, SES, etc.
        print(f"[EMAIL] To: {recipient} | Message: {message}")


class MockEmailNotifier(BaseNotifier):
    def send(self, recipient: str, message: str):
        print(f"[MOCK EMAIL] To: {recipient} | Message: {message}")


class SMSNotifier(BaseNotifier):
    def send(self, recipient: str, message: str):
        # En producción aquí iría Twilio, etc.
        print(f"[SMS] To: {recipient} | Message: {message}")