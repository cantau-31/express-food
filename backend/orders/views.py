from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from common.db import get_document
from common.views import DocumentViewSet
from orders.serializers import OrderSerializer, OrderCreateSerializer, OrderStatusSerializer
from orders.services import create_order, update_order_status, tracking

class OrderViewSet(viewsets.ViewSet):
    collection = "orders"
    serializer_class = OrderSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    # Les commandes ne peuvent être modifiées que via la route de statut.
    list = DocumentViewSet.list
    retrieve = DocumentViewSet.retrieve

    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(serializer.validated_data)
        return Response(OrderSerializer(order).data, status=201)

    @action(detail=True, methods=["get", "patch"])
    def status(self, request, pk=None):
        if request.method == "GET":
            return Response(tracking(get_document("orders", pk)))
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = update_order_status(pk, serializer.validated_data["status"])
        return Response(OrderSerializer(order).data)
