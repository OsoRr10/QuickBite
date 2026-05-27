from decimal import Decimal
from django.contrib.auth.models import User

from .models import Order, OrderItem, Cart, CartItem, Payment, Product
from .domain.order_builder import OrderBuilder


# ============================================================
# ORDER SERVICE
# ============================================================
class OrderService:

    @staticmethod
    def calculate_order_total(order: Order) -> Decimal:
        subtotal = sum(
            item.unit_price * item.quantity
            for item in order.orderitem_set.all()
        )
        discount_amount = subtotal * (order.discount / 100)
        return subtotal - discount_amount

    @staticmethod
    def change_order_status(order: Order, new_status: str) -> Order:
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        order.status = new_status
        order.save()
        return order

    @staticmethod
    def validate_stock(product: Product, quantity: int):
        if quantity > product.stock:
            raise ValueError(
                f"Not enough stock for '{product.name}'. "
                f"Available: {product.stock}, requested: {quantity}"
            )

    @staticmethod
    def reduce_stock(product: Product, quantity: int):
        OrderService.validate_stock(product, quantity)
        product.stock -= quantity
        product.save()

    @staticmethod
    def create_order(user: User, items: list, discount: Decimal = 0) -> Order:
        """
        Flujo de creación de orden:
        1. Valida stock
        2. Construye la Order con el Builder
        3. Descuenta stock
        4. Encola notificación en Celery (asíncrono — no bloquea)
        """
        if not items:
            raise ValueError("La orden debe contener al menos un producto")

        for product, quantity in items:
            OrderService.validate_stock(product, quantity)

        order = (
            OrderBuilder()
            .for_user(user)
            .with_discount(discount)
        )
        for product, quantity in items:
            order = order.add_item(product, quantity)

        order = order.build()

        for product, quantity in items:
            OrderService.reduce_stock(product, quantity)

        # ── Notificación ASÍNCRONA vía Celery + Redis ──────────────────────
        # .delay() encola la tarea y retorna inmediatamente.
        # El usuario recibe el 201 sin esperar al email.
        total = float(OrderService.calculate_order_total(order))
        try:
            from .tasks import send_order_notification
            send_order_notification.delay(
                order_id=order.id,
                user_email=user.email or f"{user.username}@quickbite.local",
                total=total,
            )
        except Exception:
            # Si Redis no está disponible (ej: dev sin Docker),
            # la orden igual se crea — solo falla la notificación.
            pass

        return order


# ============================================================
# CART SERVICE
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
# PAYMENT SERVICE
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

        # Notificación de pago también asíncrona
        try:
            from .tasks import send_payment_notification
            send_payment_notification.delay(
                order_id=payment.order.id,
                user_email=payment.order.user.email,
                amount=float(payment.amount),
            )
        except Exception:
            pass

        OrderService.change_order_status(payment.order, "CONFIRMED")
        return payment
