from rest_framework import serializers


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)
    discount = serializers.FloatField(required=False, default=0)


class OrderItemOutputSerializer(serializers.Serializer):
    product = serializers.CharField(source="product.name")
    quantity = serializers.IntegerField()
    unit_price = serializers.FloatField()


class OrderOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    discount = serializers.FloatField()
    created_at = serializers.DateTimeField()
    items = OrderItemOutputSerializer(source="orderitem_set", many=True)