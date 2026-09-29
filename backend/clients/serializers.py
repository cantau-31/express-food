from rest_framework import serializers
from common.serializers import DocumentSerializer

class ClientSerializer(DocumentSerializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=254)
    phone = serializers.RegexField(r"^\+?[0-9 .()-]{6,25}$")
    address = serializers.CharField(max_length=500)

    def validate_email(self, value):
        return value.lower()
