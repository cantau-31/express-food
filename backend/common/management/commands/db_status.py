from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import PyMongoError

from common.db import database, mongo_client

EXPECTED_COLLECTIONS = ("clients", "meals", "delivery_drivers", "orders")


class Command(BaseCommand):
    help = "Affiche un diagnostic non sensible de la base MongoDB Express Food."

    def handle(self, *args, **options):
        if not settings.MONGODB_URI:
            raise CommandError("MONGODB_URI n'est pas défini.")

        try:
            mongo_client().admin.command("ping")
            db = database()
            existing = set(db.list_collection_names())
        except PyMongoError as exc:
            raise CommandError("Diagnostic MongoDB impossible.") from exc

        self.stdout.write(self.style.SUCCESS(
            f"Connexion MongoDB : OK | base : {settings.MONGODB_DATABASE}"
        ))

        for name in EXPECTED_COLLECTIONS:
            if name not in existing:
                self.stdout.write(self.style.WARNING(
                    f"- {name}: absente (lancer init_db / seed_data)"
                ))
                continue

            count = db[name].count_documents({})
            index_names = sorted(db[name].index_information().keys())
            self.stdout.write(
                f"- {name}: {count} document(s) | index: {', '.join(index_names)}"
            )
