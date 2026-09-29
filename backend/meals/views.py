from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from common.db import database
from common.views import DocumentViewSet
from meals.serializers import MealSerializer

class MealViewSet(DocumentViewSet):
    collection = "meals"
    serializer_class = MealSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    @action(detail=False, methods=["get"])
    def today(self, request):
        meals = database().meals.find({"date": timezone.localdate().isoformat(), "available": True})
        return Response(self.serializer_class(meals, many=True).data)
