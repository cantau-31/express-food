from bson import ObjectId
from rest_framework import serializers

class ObjectIdField(serializers.CharField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Identifiant MongoDB invalide.")
        return value

class DocumentSerializer(serializers.Serializer):
    id = serializers.CharField(source="_id", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
