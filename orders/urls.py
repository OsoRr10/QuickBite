from django.urls import path
from .views import (
    ProductListAPIView,
    RestaurantListAPIView,
    CartAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
    SystemInfoAPIView,
)

urlpatterns = [
    # ── Info del sistema (para el equipo aliado) ───────────────────────────
    path('info/',            SystemInfoAPIView.as_view(),     name='system-info'),

    # ── Fallback restaurants (Nginx lo intercepta en producción) ──────────
    path('restaurants/',     RestaurantListAPIView.as_view(), name='restaurant-list'),

    # ── Endpoints Django ───────────────────────────────────────────────────
    path('products/',        ProductListAPIView.as_view(),    name='product-list'),
    path('cart/',            CartAPIView.as_view(),           name='cart'),
    path('orders/',          OrderListAPIView.as_view(),      name='order-list'),
    path('orders/create/',   CreateOrderAPIView.as_view(),    name='order-create'),
]
