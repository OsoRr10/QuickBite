from django.contrib.auth.models import User
from .models import Order, OrderItem
from .domain.order_builder import OrderBuilder
from .infra.notifier_factory import NotificationFactory


class OrderService:

    @staticmethod
    def create_order(user, items, discount=0):

        if not items:
            raise ValueError("La orden debe contener al menos un producto")

        # ======================
        # BUILDER
        # ======================

        builder = OrderBuilder(user)

        for product, quantity in items:
            product.validate_stock(quantity)
            builder.add_item(product, quantity)

        builder.set_discount(discount)

        order = builder.build()

        # ======================
        # UPDATE STOCK
        # ======================

        for product, quantity in items:
            product.reduce_stock(quantity)

        # ======================
        # SEND NOTIFICATION
        # ======================

        notifier = NotificationFactory.get_notifier("email")

        notifier.send(
            user.email,
            f"Order {order.id} created successfully"
        )

        return order