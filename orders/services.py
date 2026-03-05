from orders.domain.order_builder import OrderBuilder
from orders.infra.notifier_factory import NotifierFactory
<<<<<<< HEAD
=======
from orders.models import Payment
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)


class OrderService:

<<<<<<< HEAD
    def __init__(self):
        self.notifier = NotifierFactory.create()

    def create_order(self, user, items_data, discount=0):

        builder = (
            OrderBuilder()
            .for_user(user)
            .with_items(items_data)
            .with_discount(discount)
        )

        order = builder.build()

        self.notifier.send_confirmation(order)

        return order
=======
    @staticmethod
    def create_order(user, items, discount=0):
        builder = OrderBuilder(user)

        for product, quantity in items:
            builder.add_item(product, quantity)

        builder.set_discount(discount)

        order = builder.build()

        notifier = NotifierFactory.get_notifier("email")
        notifier.send_confirmation(order)

        return order

    @staticmethod
    def confirm_order(order):
        order.change_status("CONFIRMED")

    @staticmethod
    def cancel_order(order):
        order.change_status("CANCELLED")


class PaymentService:

    @staticmethod
    def process_payment(order, amount, method):
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            method=method
        )
        payment.validate_payment()
        payment.confirm()

        return payment

    @staticmethod
    def validate_payment(payment):
        payment.validate_payment()
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
