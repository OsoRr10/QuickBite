from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import (
    OrderCreateSerializer, OrderOutputSerializer,
    ProductSerializer, RestaurantSerializer,
    AddToCartSerializer, CartItemOutputSerializer,
)
from .services import OrderService, CartService
from .models import Product, Restaurant, Order, Cart


# ── PRODUCTOS ──────────────────────────────────────
class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.select_related('category', 'restaurant').all()
        return Response(ProductSerializer(products, many=True).data)


# ── RESTAURANTES ───────────────────────────────────
class RestaurantListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        restaurants = Restaurant.objects.all()
        return Response(RestaurantSerializer(restaurants, many=True).data)


# ── CARRITO ────────────────────────────────────────
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        items = cart.cartitem_set.select_related('product').all()
        total = CartService.calculate_cart_total(cart)
        return Response({
            'items': CartItemOutputSerializer(items, many=True).data,
            'total': float(total)
        })

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=serializer.validated_data['product_id'])
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = CartService.add_item_to_cart(
                request.user, product, serializer.validated_data['quantity']
            )
            return Response({'message': f'"{product.name}" agregado al carrito'}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)


# ── ÓRDENES ────────────────────────────────────────
class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__product')
        return Response(OrderOutputSerializer(orders, many=True).data)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = serializer.validated_data['items']
        discount = serializer.validated_data.get('discount', 0)

        items = []
        for item in items_data:
            try:
                product = Product.objects.get(id=item['product_id'])
                items.append((product, item['quantity']))
            except Product.DoesNotExist:
                return Response(
                    {'error': f'Producto con id {item["product_id"]} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

        try:
            order = OrderService.create_order(request.user, items, discount)
            return Response(OrderOutputSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)