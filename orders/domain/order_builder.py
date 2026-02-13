from orders.models import Order, OrderItem


class OrderBuilder:

    def __init__(self):
        self._user = None
        self._items = []
        self._discount = 0

    def for_user(self, user):
        self._user = user
        return self

    def with_items(self, items):
        if not items:
            raise ValueError("Order must contain at least one item")
        self._items = items
        return self

    def with_discount(self, discount):
        self._discount = discount
        return self

    def build(self):

        if not self._user:
            raise ValueError("Order must have a user")

        order = Order.objects.create(
            user=self._user,
            discount=self._discount,
            status="PENDING"
        )

        for item in self._items:
            product = item["product"]
            quantity = item["quantity"]

            product.reduce_stock(quantity)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )

        return order
