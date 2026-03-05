from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User

from orders.models import Product, Restaurant, Category, Order, OrderItem
from orders.services import OrderService, PaymentService


def make_product(name="Burger", price="10.00", stock=100):
    restaurant = Restaurant.objects.create(
        name="Test Restaurant", email="r@test.com",
        phone="123", address="Calle 1", rating=5.0
    )
    category = Category.objects.create(name="Fast Food")
    return Product.objects.create(
        name=name, price=Decimal(price),
        stock=stock, restaurant=restaurant, category=category
    )


class OrderServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.product = make_product()

    def test_validate_stock_raises_when_insufficient(self):
        with self.assertRaises(ValueError):
            OrderService.validate_stock(self.product, 200)

    def test_reduce_stock(self):
        OrderService.reduce_stock(self.product, 10)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 90)

    def test_create_order_success(self):
        order = OrderService.create_order(self.user, [(self.product, 2)])
        self.assertEqual(order.status, "PENDING")
        self.assertEqual(order.orderitem_set.count(), 1)

    def test_create_order_applies_discount(self):
        order = OrderService.create_order(self.user, [(self.product, 2)], discount=10)
        total = OrderService.calculate_order_total(order)
        self.assertEqual(total, Decimal("18.00"))  # 20 - 10%

    def test_create_order_empty_items_raises(self):
        with self.assertRaises(ValueError):
            OrderService.create_order(self.user, [])


class PaymentServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="payer", password="pass")
        self.product = make_product()

    def test_validate_payment_amount_raises_on_zero(self):
        with self.assertRaises(ValueError):
            PaymentService.validate_payment_amount(Decimal("0"))

    def test_calculate_price_with_discount(self):
        result = PaymentService.calculate_price_with_discount(Decimal("100"), Decimal("20"))
        self.assertEqual(result, Decimal("80.00"))