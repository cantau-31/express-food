from django.http import JsonResponse


class JsonErrorsMiddleware:
    """Uniformise aussi les erreurs Django hors des vues DRF (URL inconnue, hôte invalide)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code >= 400 and "application/json" not in response.get("Content-Type", ""):
            messages = {400: "Requête invalide.", 403: "Accès interdit.", 404: "Route introuvable.", 500: "Erreur interne."}
            return JsonResponse({"detail": messages.get(response.status_code, "Erreur HTTP.")}, status=response.status_code)
        return response
