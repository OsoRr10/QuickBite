"""
views.py — Monolito Django (QuickBite)
---------------------------------------
PATRÓN ESTRANGULADOR aplicado:
  - /api/restaurants/  → migrado al microservicio Flask (services/restaurants/)
                         Nginx redirige ese path ANTES de llegar aquí.
                         La vista RestaurantListAPIView se conserva como
                         FALLBACK INTERNO (por si Nginx no está activo en dev).

  Los demás endpoints (productos, carrito, órdenes) siguen aquí
  hasta que sean migrados en iteraciones futuras.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import (
    OrderCreateSerializer,
    OrderOutputSerializer,
    ProductSerializer,
    RestaurantSerializer,
    AddToCartSerializer,
    CartItemOutputSerializer,
)
from .services import OrderService, CartService
from .models import Product, Restaurant, Order, Cart
from .clients.ally_client import get_ally_info


# ── SISTEMA INFO (endpoint propio para el equipo aliado) ───────────────────
class SystemInfoAPIView(APIView):
    """
    GET /api/info/
    Expone metadata del sistema para integración con el equipo aliado.
    Requerimiento 2.3: "Exponga un endpoint JSON con información relevante".
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "service": "QuickBite",
                "version": "2.0.0",
                "description": "Plataforma de pedidos de comida rápida",
                "endpoints": {
                    "restaurants": "/api/restaurants/",  # servido por Flask
                    "products": "/api/products/",
                    "orders": "/api/orders/",
                },
                "team": "QuickBite Team",
            }
        )


class AllyInfoAPIView(APIView):
    """
    GET /api/ally/info/
    Consume el servicio del equipo aliado y reexpone su información.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        res = get_ally_info()
        if not res.get("ok"):
            return Response(
                {
                    "error": "No se pudo contactar al servicio aliado",
                    "detail": res.get("error"),
                },
                status=503,
            )
        return Response(res.get("data", {}))


# ── RESTAURANTES (fallback — en producción Nginx redirige a Flask) ─────────
class RestaurantListAPIView(APIView):
    """
    NOTA: En producción este endpoint nunca se alcanza.
    Nginx intercepta /api/restaurants/ y lo envía al microservicio Flask.
    Esta vista existe sólo como fallback para desarrollo sin Docker.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        restaurants = Restaurant.objects.all()
        return Response(RestaurantSerializer(restaurants, many=True).data)


# ── PRODUCTOS ──────────────────────────────────────────────────────────────
class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.select_related("category", "restaurant").all()
        return Response(ProductSerializer(products, many=True).data)


# ── CARRITO ────────────────────────────────────────────────────────────────
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        items = cart.cartitem_set.select_related("product").all()
        total = CartService.calculate_cart_total(cart)
        return Response(
            {
                "items": CartItemOutputSerializer(items, many=True).data,
                "total": float(total),
            }
        )

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=serializer.validated_data["product_id"])
        except Product.DoesNotExist:
            return Response(
                {"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            CartService.add_item_to_cart(
                request.user, product, serializer.validated_data["quantity"]
            )
            return Response(
                {"message": f'"{product.name}" agregado al carrito'},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)


# ── ÓRDENES ────────────────────────────────────────────────────────────────
class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related(
            "orderitem_set__product"
        )
        return Response(OrderOutputSerializer(orders, many=True).data)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = serializer.validated_data["items"]
        discount = serializer.validated_data.get("discount", 0)

        items = []
        for item in items_data:
            try:
                product = Product.objects.get(id=item["product_id"])
                items.append((product, item["quantity"]))
            except Product.DoesNotExist:
                return Response(
                    {"error": f'Producto con id {item["product_id"]} no encontrado'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            order = OrderService.create_order(request.user, items, discount)
            return Response(
                OrderOutputSerializer(order).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)


# ── RECETAS / API TERCEROS (Patrón Adapter) ────────────────────────────────
import os as _os
from .adapters.meal_adapter import MealAdapterFactory


class MealSuggestionAPIView(APIView):
    """
    GET /api/meals/suggestion/?q=chicken
    Busca una receta en TheMealDB usando el Patrón Adapter.
    El frontend la muestra como "inspiración" para los productos.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "chicken")
        env = _os.getenv("ENV_TYPE", "prod")
        adapter = MealAdapterFactory.get_adapter(env)
        meal = adapter.get_meal_suggestion(query)
        return Response(meal)


class RandomMealAPIView(APIView):
    """
    GET /api/meals/random/
    Retorna una receta aleatoria de TheMealDB.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        env = _os.getenv("ENV_TYPE", "prod")
        adapter = MealAdapterFactory.get_adapter(env)
        meal = adapter.get_random_meal()
        return Response(meal)
