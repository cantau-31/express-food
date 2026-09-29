from rest_framework.decorators import action
from rest_framework.response import Response
from common.db import database, get_document
from common.views import DocumentViewSet
from delivery.serializers import DeliveryDriverSerializer, DriverStatusSerializer, LocationSerializer
from delivery.services import update_driver

class DeliveryDriverViewSet(DocumentViewSet):
    collection = "delivery_drivers"
    serializer_class = DeliveryDriverSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def partial_update(self, request, pk=None):
        serializer = self.serializer_class(get_document(self.collection, pk), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(self.serializer_class(update_driver(pk, serializer.validated_data)).data)

    @action(detail=False, methods=["get"])
    def available(self, request):
        drivers = database()[self.collection].find({"status": "available"})
        return Response(self.serializer_class(drivers, many=True).data)

    @action(detail=True, methods=["patch"])
    def status(self, request, pk=None):
        serializer = DriverStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(self.serializer_class(update_driver(pk, serializer.validated_data)).data)

    @action(detail=True, methods=["patch"])
    def location(self, request, pk=None):
        serializer = LocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(self.serializer_class(update_driver(pk, serializer.validated_data)).data)
