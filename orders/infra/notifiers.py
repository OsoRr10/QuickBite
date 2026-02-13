class RealEmailNotifier:
    def send_confirmation(self, order):
        print("Sending REAL email confirmation...")


class MockEmailNotifier:
    def send_confirmation(self, order):
        print("Mock: Order confirmed.")
