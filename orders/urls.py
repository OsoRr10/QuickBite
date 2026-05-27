from django.urls import path
from .views import (
    ProductListAPIView,
    RestaurantListAPIView,
    CartAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
    SystemInfoAPIView,
    MealSuggestionAPIView,
    RandomMealAPIView,
)

urlpatterns = [
    # ── Info del sistema ───────────────────────────────────────────────────
    path('info/',               SystemInfoAPIView.as_view(),     name='system-info'),

    # ── Restaurantes (fallback) ────────────────────────────────────────────
    path('restaurants/',        RestaurantListAPIView.as_view(), name='restaurant-list'),

    # ── Productos ──────────────────────────────────────────────────────────
    path('products/',           ProductListAPIView.as_view(),    name='product-list'),

    # ── Carrito ────────────────────────────────────────────────────────────
    path('cart/',               CartAPIView.as_view(),           name='cart'),

    # ── Órdenes ────────────────────────────────────────────────────────────
    path('orders/',             OrderListAPIView.as_view(),      name='order-list'),
    path('orders/create/',      CreateOrderAPIView.as_view(),    name='order-create'),

    # ── Recetas API terceros (Patrón Adapter — TheMealDB) ──────────────────
    path('meals/suggestion/',   MealSuggestionAPIView.as_view(), name='meal-suggestion'),
    path('meals/random/',       RandomMealAPIView.as_view(),     name='meal-random'),
]
