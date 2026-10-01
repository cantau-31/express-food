from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Vérifie les principaux paramètres de sécurité avant un déploiement."

    def handle(self, *args, **options):
        errors = []
        warnings = []

        if settings.DEBUG:
            errors.append("DEBUG doit être False en production.")

        if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
            errors.append("DJANGO_SECRET_KEY doit être défini avec une valeur suffisamment longue.")

        hosts = [host.strip() for host in settings.ALLOWED_HOSTS if host.strip()]
        if not hosts:
            errors.append("ALLOWED_HOSTS ne doit pas être vide.")
        if "*" in hosts:
            errors.append("ALLOWED_HOSTS ne doit pas contenir '*' en production.")

        origins = [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS if origin.strip()]
        if not origins:
            errors.append("CORS_ALLOWED_ORIGINS ne doit pas être vide.")

        if not settings.MONGODB_URI:
            errors.append("MONGODB_URI doit être défini.")

        if not settings.MONGODB_DATABASE:
            errors.append("MONGODB_DATABASE doit être défini.")

        if any(origin.startswith("http://") and "localhost" not in origin and "127.0.0.1" not in origin for origin in origins):
            warnings.append("Une origine CORS de production utilise HTTP au lieu de HTTPS.")

        for warning in warnings:
            self.stdout.write(self.style.WARNING(f"- {warning}"))

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(f"- {error}"))
            raise CommandError("Configuration de déploiement invalide.")

        self.stdout.write(self.style.SUCCESS("Configuration de déploiement : OK"))
