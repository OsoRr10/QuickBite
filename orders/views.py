from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OrderCreateSerializer, OrderOutputSerializer
from .services import OrderService
from .models import Product


class CreateOrderAPIView(APIView):

    def post(self, request):

        serializer = OrderCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = serializer.validated_data["items"]
        discount = serializer.validated_data.get("discount", 0)

        items = []

        try:
            for item in items_data:
                product = Product.objects.get(id=item["product_id"])
                items.append((product, item["quantity"]))
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            order = OrderService.create_order(
                request.user,
                items,
                discount
            )

            output_serializer = OrderOutputSerializer(order)

            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT
            )