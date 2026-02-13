from orders.domain.order_builder import OrderBuilder
from orders.infra.notifier_factory import NotifierFactory


class OrderService:

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
