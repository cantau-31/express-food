from common.views import DocumentViewSet
from clients.serializers import ClientSerializer

class ClientViewSet(DocumentViewSet):
    collection = "clients"
    serializer_class = ClientSerializer
