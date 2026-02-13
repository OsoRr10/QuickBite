import json
from django.views import View
from django.http import JsonResponse
from .services import OrderService
from .models import Product


class CreateOrderView(View):

    def post(self, request):

        data = json.loads(request.body)
        service = OrderService()

        items = []
        for item in data["items"]:
            product = Product.objects.get(id=item["product_id"])
            items.append({
                "product": product,
                "quantity": item["quantity"]
            })

        order = service.create_order(request.user, items)

        return JsonResponse({"order_id": order.id})
