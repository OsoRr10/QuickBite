from django.test import TestCase
<<<<<<< HEAD

# Create your tests here.
=======
from orders.models import Product, Restaurant, Category, Order, OrderItem
from django.contrib.auth.models import User

class ProductTestCase(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            email="test@example.com",
            phone="1234567890",
            address="123 Test St",
            rating=5.0
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.0,
            stock=100,
            restaurant=self.restaurant,
            category=self.category
        )

    def test_product_stock_validation(self):
        with self.assertRaises(ValueError):
            self.product.validate_stock(200)

    def test_product_reduce_stock(self):
        self.product.reduce_stock(10)
        self.assertEqual(self.product.stock, 90)

class OrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            email="test@example.com",
            phone="1234567890",
            address="123 Test St",
            rating=5.0
        )
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            price=10.0,
            stock=100,
            restaurant=self.restaurant,
            category=self.category
        )
        self.order = Order.objects.create(user=self.user, discount=10)

    def test_order_total(self):
        OrderItem.objects.create(order=self.order, product=self.product, quantity=2, unit_price=10.0)
        self.assertEqual(self.order.calculate_total(), 18.0)  # 20 - 10% discount
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
