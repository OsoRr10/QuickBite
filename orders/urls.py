from django.urls import path, include
from .views import CreateOrderAPIView

urlpatterns = [
    path("orders/create/", CreateOrderAPIView.as_view()),
    path("api/", include("orders.urls")),
]
