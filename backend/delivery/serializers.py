from rest_framework import serializers
from common.serializers import DocumentSerializer

STATUSES = ["available", "delivering", "offline"]

class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)

    def validate(self, attrs):
        import math
        if any(not math.isfinite(v) for v in attrs.values()):
            raise serializers.ValidationError("Coordonnées non finies interdites.")
        return attrs

class DriverStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=STATUSES)

class DeliveryDriverSerializer(DocumentSerializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.RegexField(r"^\+?[0-9 .()-]{6,25}$")
    status = serializers.ChoiceField(choices=STATUSES, default="available")
    latitude = serializers.FloatField(min_value=-90, max_value=90, allow_null=True, default=None)
    longitude = serializers.FloatField(min_value=-180, max_value=180, allow_null=True, default=None)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, attrs):
        import math
        for field in ("latitude", "longitude"):
            value = attrs.get(field)
            if value is not None and not math.isfinite(value):
                raise serializers.ValidationError({field: "Coordonnée non finie interdite."})
        merged = {**(self.instance or {}), **attrs}
        if (merged.get("latitude") is None) != (merged.get("longitude") is None):
            raise serializers.ValidationError("Latitude et longitude doivent être fournies ensemble.")
        if self.instance is None and attrs.get("status") == "delivering":
            raise serializers.ValidationError("Un livreur devient delivering par attribution d'une commande.")
        return attrs
