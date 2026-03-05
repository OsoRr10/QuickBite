from orders.models import Order, OrderItem


class OrderBuilder:
    """
    Builder para la construcción de una Order compleja.
    Permite ensamblar paso a paso: usuario, ítems y descuento
    antes de persistir en base de datos.
    """

    def __init__(self):
        self._user = None
        self._items = []   # lista de (product, quantity)
        self._discount = 0

    def for_user(self, user):
        self._user = user
        return self

    def add_item(self, product, quantity):
        self._items.append((product, quantity))
        return self

    def with_discount(self, discount):
        self._discount = discount
        return self

    def build(self):
        if not self._user:
            raise ValueError("Order must have a user")
        if not self._items:
            raise ValueError("Order must contain at least one item")

        order = Order.objects.create(
            user=self._user,
            discount=self._discount,
            status="PENDING"
        )

        for product, quantity in self._items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )

        return order