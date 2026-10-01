from bson import ObjectId
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from common.db import database


class Command(BaseCommand):
    help = "Anonymise un livreur inactif tout en conservant l'historique des commandes."

    def add_arguments(self, parser):
        parser.add_argument("driver_id", help="Identifiant MongoDB du livreur à anonymiser")

    def handle(self, *args, **options):
        driver_id = options["driver_id"]

        if not ObjectId.is_valid(driver_id):
            raise CommandError("Identifiant livreur invalide.")

        db = database()
        oid = ObjectId(driver_id)
        driver = db.delivery_drivers.find_one({"_id": oid})
        if driver is None:
            raise CommandError("Livreur introuvable.")

        if driver.get("active_order_id"):
            raise CommandError("Impossible d'anonymiser un livreur avec une commande active.")

        result = db.delivery_drivers.update_one(
            {"_id": oid},
            {"$set": {
                "first_name": "Deleted",
                "last_name": "Driver",
                "phone": "0000000000",
                "status": "offline",
                "latitude": None,
                "longitude": None,
                "anonymized_at": timezone.now(),
                "updated_at": timezone.now(),
            }}
        )

        if result.modified_count != 1:
            raise CommandError("Aucune donnée n'a été modifiée.")

        order_count = db.orders.count_documents({"delivery_driver_id": driver_id})
        self.stdout.write(self.style.SUCCESS(
            f"Livreur anonymisé. Historique conservé : {order_count} commande(s)."
        ))
