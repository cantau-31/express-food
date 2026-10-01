from bson import ObjectId
from django.core.management.base import BaseCommand, CommandError

from common.db import database

ORDER_STATUSES = {
    "pending", "accepted", "preparing", "out_for_delivery", "delivered", "cancelled"
}
DRIVER_STATUSES = {"available", "delivering", "offline"}


class Command(BaseCommand):
    help = "Vérifie l'intégrité logique des principales collections MongoDB sans modifier les données."

    def handle(self, *args, **options):
        db = database()
        errors = []

        for driver in db.delivery_drivers.find():
            status = driver.get("status")
            if status not in DRIVER_STATUSES:
                errors.append(f"delivery_drivers/{driver.get('_id')}: statut invalide")

            lat = driver.get("latitude")
            lon = driver.get("longitude")
            if (lat is None) != (lon is None):
                errors.append(f"delivery_drivers/{driver.get('_id')}: coordonnées incomplètes")

            active_order_id = driver.get("active_order_id")
            if active_order_id:
                if not ObjectId.is_valid(active_order_id):
                    errors.append(f"delivery_drivers/{driver.get('_id')}: active_order_id invalide")
                else:
                    order = db.orders.find_one({"_id": ObjectId(active_order_id)})
                    if order is None:
                        errors.append(f"delivery_drivers/{driver.get('_id')}: commande active absente")
                    elif str(driver["_id"]) != order.get("delivery_driver_id"):
                        errors.append(f"delivery_drivers/{driver.get('_id')}: incohérence avec la commande active")

        for order in db.orders.find():
            status = order.get("status")
            if status not in ORDER_STATUSES:
                errors.append(f"orders/{order.get('_id')}: statut invalide")

            client_id = order.get("client_id")
            if not ObjectId.is_valid(client_id or "") or db.clients.find_one({"_id": ObjectId(client_id)}) is None:
                errors.append(f"orders/{order.get('_id')}: client introuvable")

            driver_id = order.get("delivery_driver_id")
            if driver_id:
                if not ObjectId.is_valid(driver_id):
                    errors.append(f"orders/{order.get('_id')}: delivery_driver_id invalide")
                elif db.delivery_drivers.find_one({"_id": ObjectId(driver_id)}) is None:
                    errors.append(f"orders/{order.get('_id')}: livreur introuvable")

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(f"- {error}"))
            raise CommandError(f"{len(errors)} anomalie(s) détectée(s).")

        self.stdout.write(self.style.SUCCESS("Intégrité des données : OK"))
