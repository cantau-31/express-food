from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import PyMongoError

from common.db import mongo_client


class Command(BaseCommand):
    help = "Vérifie la connexion MongoDB configurée dans MONGODB_URI."

    def handle(self, *args, **options):
        if not settings.MONGODB_URI:
            raise CommandError("MONGODB_URI n'est pas défini.")

        try:
            result = mongo_client().admin.command("ping")
        except PyMongoError as exc:
            raise CommandError("Connexion MongoDB impossible.") from exc

        if result.get("ok") != 1.0:
            raise CommandError("MongoDB n'a pas répondu correctement au ping.")

        self.stdout.write(
            self.style.SUCCESS(
                f"MongoDB accessible — base configurée : {settings.MONGODB_DATABASE}"
            )
        )
