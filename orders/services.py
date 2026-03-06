from decimal import Decimal
from django.contrib.auth.models import User

from .models import Order, OrderItem, Cart, CartItem, Payment, Product
from .domain.order_builder import OrderBuilder
from .infra.notifier_factory import NotificationFactory


# ============================================================
# ORDER SERVICE  —  orquesta la creación y gestión de órdenes
# ============================================================
class OrderService:

    @staticmethod
    def calculate_order_total(order: Order) -> Decimal:
        """Calcula el total de la orden aplicando el descuento."""
        subtotal = sum(
            item.unit_price * item.quantity
            for item in order.orderitem_set.all()
        )
        discount_amount = subtotal * (order.discount / 100)
        return subtotal - discount_amount

    @staticmethod
    def change_order_status(order: Order, new_status: str) -> Order:
        """Valida y cambia el estado de una orden."""
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        order.status = new_status
        order.save()
        return order

    @staticmethod
    def validate_stock(product: Product, quantity: int):
        """Lanza ValueError si no hay suficiente stock."""
        if quantity > product.stock:
            raise ValueError(
                f"Not enough stock for '{product.name}'. "
                f"Available: {product.stock}, requested: {quantity}"
            )

    @staticmethod
    def reduce_stock(product: Product, quantity: int):
        """Descuenta el stock del producto tras validarlo."""
        OrderService.validate_stock(product, quantity)
        product.stock -= quantity
        product.save()
    
    @staticmethod
    def create_order(user: User, items: list, discount: Decimal = 0) -> Order:
        """
        Flujo principal de creación de orden:
        1. Valida stock de todos los productos
        2. Construye la Order con el Builder
        3. Descuenta stock
        4. Envía notificación
        """
        if not items:
            raise ValueError("La orden debe contener al menos un producto")

        # Validar stock antes de modificar cualquier cosa
        for product, quantity in items:
            OrderService.validate_stock(product, quantity)

        # Construir la Order con el Builder (patrón creacional)
        order = (
            OrderBuilder()
            .for_user(user)
            .with_discount(discount)
        )
        for product, quantity in items:
            order = order.add_item(product, quantity)

        order = order.build()

        # Descontar stock solo una vez, aquí en el servicio
        for product, quantity in items:
            OrderService.reduce_stock(product, quantity)

        # Notificar al usuario (Factory decide email real vs mock)
        notifier = NotificationFactory.get_notifier("email")
        notifier.send(
            recipient=user.email,
            subject=f"QuickBite - Orden #{order.id} creada",
            message=f"Tu orden #{order.id} fue creada exitosamente."
        )

        return order

# ============================================================
# CART SERVICE  —  gestión del carrito de compras
# ============================================================
class CartService:

    @staticmethod
    def get_or_create_cart(user: User) -> Cart:
        cart, _ = Cart.objects.get_or_create(user=user, active=True)
        return cart

    @staticmethod
    def add_item_to_cart(user: User, product: Product, quantity: int) -> CartItem:
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        OrderService.validate_stock(product, quantity)

        cart = CartService.get_or_create_cart(user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={"quantity": quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item

    @staticmethod
    def calculate_cart_total(cart: Cart) -> Decimal:
        return sum(
            item.product.price * item.quantity
            for item in cart.cartitem_set.select_related("product").all()
        )

    @staticmethod
    def clear_cart(cart: Cart):
        cart.cartitem_set.all().delete()


# ============================================================
# PAYMENT SERVICE  —  gestión de pagos
# ============================================================
class PaymentService:

    @staticmethod
    def validate_payment_amount(amount: Decimal):
        if amount <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0")

    @staticmethod
    def calculate_price_with_discount(price: Decimal, discount_pct: Decimal) -> Decimal:
        return price - (price * discount_pct / 100)

    @staticmethod
    def create_payment(order: Order, amount: Decimal, method: str) -> Payment:
        PaymentService.validate_payment_amount(amount)

        expected_total = OrderService.calculate_order_total(order)
        if amount < expected_total:
            raise ValueError(
                f"Monto insuficiente. Total de la orden: {expected_total}"
            )

        payment = Payment.objects.create(
            order=order,
            amount=amount,
            method=method,
            confirmed=False
        )
        return payment

    @staticmethod
    def confirm_payment(payment: Payment) -> Payment:
        payment.confirmed = True
        payment.save()

        # Notificar confirmación de pago
        notifier = NotificationFactory.get_notifier("email")
        notifier.send(
            recipient=payment.order.user.email,
            message=f"Tu pago para la orden #{payment.order.id} fue confirmado."
        )

        # Avanzar estado de la orden
        OrderService.change_order_status(payment.order, "CONFIRMED")
        return payment