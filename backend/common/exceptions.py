from django.http import JsonResponse
from pymongo.errors import DuplicateKeyError, PyMongoError
from rest_framework.response import Response
from rest_framework.views import exception_handler

def api_exception_handler(exc, context):
    if isinstance(exc, DuplicateKeyError):
        return Response({"detail": "Cette valeur unique existe déjà (email)."}, status=400)
    if isinstance(exc, PyMongoError):
        return Response({"detail": "Base de données indisponible. Réessayez plus tard."}, status=503)
    return exception_handler(exc, context)

def not_found(request, exception):
    return JsonResponse({"detail": "Route introuvable."}, status=404)

def server_error(request):
    return JsonResponse({"detail": "Erreur interne."}, status=500)
