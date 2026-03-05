from rest_framework import serializers
from .models import Product, Restaurant, Category, Order, OrderItem, CartItem


# ── INPUT ──────────────────────────────────────────
class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)
    discount = serializers.FloatField(required=False, default=0)


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


# ── OUTPUT ─────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'phone', 'rating']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    restaurant = RestaurantSerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'restaurant']


class OrderItemOutputSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']


class OrderOutputSerializer(serializers.ModelSerializer):
    items = OrderItemOutputSerializer(source='orderitem_set', many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'discount', 'total', 'created_at', 'items']

    def get_total(self, obj):
     from decimal import Decimal
     subtotal = sum(i.unit_price * i.quantity for i in obj.orderitem_set.all())
     return float(subtotal - (subtotal * Decimal(str(obj.discount)) / 100))


class CartItemOutputSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    unit_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_name', 'unit_price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return float(obj.product.price * obj.quantity)