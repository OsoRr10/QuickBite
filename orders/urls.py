from django.urls import path
from .views import (
    ProductListAPIView,
    RestaurantListAPIView,
    CartAPIView,
    OrderListAPIView,
    CreateOrderAPIView,
)

urlpatterns = [
    path('products/',        ProductListAPIView.as_view(),    name='product-list'),
    path('restaurants/',     RestaurantListAPIView.as_view(), name='restaurant-list'),
    path('cart/',            CartAPIView.as_view(),           name='cart'),
    path('orders/',          OrderListAPIView.as_view(),      name='order-list'),
    path('orders/create/',   CreateOrderAPIView.as_view(),    name='order-create'),
]