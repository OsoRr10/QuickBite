from django.db import models
from django.contrib.auth.models import User

<<<<<<< HEAD

=======
# =========================
# CATEGORY
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# =========================
# RESTAURANT
# =========================
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.name

# =========================
# PRODUCT
# =========================
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.FloatField()
    stock = models.IntegerField()

<<<<<<< HEAD
    def reduce_stock(self, quantity):
        if self.stock < quantity:
            raise ValueError("Not enough stock")
        self.stock -= quantity
        self.save()

    def __str__(self):
        return self.name


=======
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, default=1)

    def validate_stock(self, quantity):
        if quantity > self.stock:
            raise ValueError("Not enough stock")

    def reduce_stock(self, quantity):
        self.validate_stock(quantity)
        self.stock -= quantity
        self.save()

    def calculate_price_with_discount(self, discount):
        return self.price - (self.price * discount / 100)

    def __str__(self):
        return self.name

# =========================
# CART
# =========================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def calculate_total(self):
        return sum(item.subtotal() for item in self.cartitem_set.all())

    def clear(self):
        self.cartitem_set.all().delete()

# =========================
# CART ITEM
# =========================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def subtotal(self):
        return self.quantity * self.product.price

# =========================
# ORDER
# =========================
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
<<<<<<< HEAD
=======
        ("IN_PREPARATION", "In preparation"),
        ("ON_THE_WAY", "On the way"),
        ("DELIVERED", "Delivered"),
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    discount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

<<<<<<< HEAD
    def __str__(self):
        return f"Order {self.id}"


=======
    def calculate_subtotal(self):
        return sum(item.subtotal() for item in self.orderitem_set.all())

    def calculate_total(self):
        subtotal = self.calculate_subtotal()
        return subtotal - (subtotal * self.discount / 100)

    def change_status(self, new_status):
        self.status = new_status
        self.save()

    def __str__(self):
        return f"Order {self.id}"

# =========================
# ORDER ITEM
# =========================
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.FloatField()

    def subtotal(self):
        return self.quantity * self.unit_price
<<<<<<< HEAD
=======

# =========================
# PAYMENT
# =========================
class Payment(models.Model):

    METHOD_CHOICES = [
        ("CREDIT_CARD", "Credit Card"),
        ("DEBIT_CARD", "Debit Card"),
        ("TRANSFER", "Transfer"),
        ("CASH", "Cash"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.FloatField()
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    reference = models.CharField(max_length=100, blank=True)

    def validate_payment(self):
        if self.amount <= 0:
            raise ValueError("Invalid payment amount")

    def confirm(self):
        self.confirmed = True
        self.save()
>>>>>>> 571b5ab (Implementación de modelos, builder, servicios y factory)
