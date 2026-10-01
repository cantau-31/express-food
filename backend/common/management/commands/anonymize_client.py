from bson import ObjectId
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from common.db import database


class Command(BaseCommand):
    help = "Anonymise les données personnelles d'un client tout en conservant l'historique des commandes."

    def add_arguments(self, parser):
        parser.add_argument("client_id", help="Identifiant MongoDB du client à anonymiser")

    def handle(self, *args, **options):
        client_id = options["client_id"]

        if not ObjectId.is_valid(client_id):
            raise CommandError("Identifiant client invalide.")

        db = database()
        oid = ObjectId(client_id)
        client = db.clients.find_one({"_id": oid})
        if client is None:
            raise CommandError("Client introuvable.")

        anonymized_email = f"deleted-{client_id}@anonymized.invalid"
        result = db.clients.update_one(
            {"_id": oid},
            {"$set": {
                "first_name": "Deleted",
                "last_name": "User",
                "email": anonymized_email,
                "phone": "0000000000",
                "address": "Anonymized",
                "anonymized_at": timezone.now(),
            }}
        )

        if result.modified_count != 1:
            raise CommandError("Aucune donnée n'a été modifiée.")

        order_count = db.orders.count_documents({"client_id": client_id})
        self.stdout.write(self.style.SUCCESS(
            f"Client anonymisé. Historique conservé : {order_count} commande(s)."
        ))
