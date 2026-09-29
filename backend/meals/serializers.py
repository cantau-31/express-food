from decimal import Decimal
from rest_framework import serializers
from common.serializers import DocumentSerializer

class MealSerializer(DocumentSerializer):
    name = serializers.CharField(max_length=150)
    description = serializers.CharField(max_length=2000, allow_blank=True, default="")
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal("0.01"))
    type = serializers.ChoiceField(choices=["dish", "dessert"])
    date = serializers.DateField()
    image_url = serializers.URLField(allow_blank=True, default="")
    available = serializers.BooleanField(default=True)
