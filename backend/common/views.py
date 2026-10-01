"""URL → vue → serializer → MongoDB → réponse JSON."""
from datetime import date
from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from common.db import database, get_document

def storage_values(values):
    # Les montants sont stockés en chaînes décimales exactes ; dates ISO.
    return {key: str(value) if isinstance(value, (Decimal, date)) else value for key, value in values.items()}

class DocumentViewSet(viewsets.ViewSet):
    collection = None
    serializer_class = None

    def list(self, request):
        documents = database()[self.collection].find().sort("_id", -1)
        return Response(self.serializer_class(documents, many=True).data)

    def retrieve(self, request, pk=None):
        return Response(self.serializer_class(get_document(self.collection, pk)).data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = storage_values(serializer.validated_data)
        document["created_at"] = timezone.now()
        if self.collection == "delivery_drivers":
            document["updated_at"] = document["created_at"]
        database()[self.collection].insert_one(document)
        return Response(self.serializer_class(document).data, status=201)

    def partial_update(self, request, pk=None):
        return self.update(request, pk, partial=True)

    def update(self, request, pk=None, partial=False):
        document = get_document(self.collection, pk)
        serializer = self.serializer_class(document, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        values = storage_values(serializer.validated_data)
        if values:
            database()[self.collection].update_one({"_id": document["_id"]}, {"$set": values})
        document.update(values)
        return Response(self.serializer_class(document).data)

    def destroy(self, request, pk=None):
        document = get_document(self.collection, pk)
        database()[self.collection].delete_one({"_id": document["_id"]})
        return Response(status=204)
