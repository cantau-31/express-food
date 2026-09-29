from rest_framework import serializers
from common.serializers import DocumentSerializer, ObjectIdField

STATUSES = ["pending", "accepted", "preparing", "out_for_delivery", "delivered", "cancelled"]

class OrderItemInputSerializer(serializers.Serializer):
    meal_id = ObjectIdField()
    quantity = serializers.IntegerField(min_value=1, max_value=100)

class OrderCreateSerializer(serializers.Serializer):
    client_id = ObjectIdField()
    items = OrderItemInputSerializer(many=True, allow_empty=False, max_length=100)

    def validate_items(self, items):
        ids = [item["meal_id"] for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Regroupez les quantités d'un même repas sur une seule ligne.")
        return items

class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=STATUSES)

class OrderItemSerializer(serializers.Serializer):
    meal_id = serializers.CharField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2)

class OrderSerializer(DocumentSerializer):
    client_id = serializers.CharField()
    items = OrderItemSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2)
    delivery_fee = serializers.DecimalField(max_digits=14, decimal_places=2)
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    status = serializers.ChoiceField(choices=STATUSES)
    delivery_driver_id = serializers.CharField(allow_null=True)
    estimated_delivery_minutes = serializers.IntegerField(allow_null=True)
    updated_at = serializers.DateTimeField()
