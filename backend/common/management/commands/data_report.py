from collections import Counter

from django.core.management.base import BaseCommand

from common.db import database


class Command(BaseCommand):
    help = "Affiche un résumé Data sans exposer de données personnelles."

    def handle(self, *args, **options):
        db = database()

        client_count = db.clients.count_documents({})
        meal_count = db.meals.count_documents({})
        order_count = db.orders.count_documents({})
        driver_count = db.delivery_drivers.count_documents({})

        order_statuses = Counter(
            doc.get("status", "unknown")
            for doc in db.orders.find({}, {"status": 1})
        )
        driver_statuses = Counter(
            doc.get("status", "unknown")
            for doc in db.delivery_drivers.find({}, {"status": 1})
        )

        self.stdout.write("=== Express Food — Data report ===")
        self.stdout.write(f"Clients : {client_count}")
        self.stdout.write(f"Repas : {meal_count}")
        self.stdout.write(f"Livreurs : {driver_count}")
        self.stdout.write(f"Commandes : {order_count}")

        self.stdout.write("Commandes par statut :")
        if order_statuses:
            for key in sorted(order_statuses):
                self.stdout.write(f"- {key}: {order_statuses[key]}")
        else:
            self.stdout.write("- aucune")

        self.stdout.write("Livreurs par statut :")
        if driver_statuses:
            for key in sorted(driver_statuses):
                self.stdout.write(f"- {key}: {driver_statuses[key]}")
        else:
            self.stdout.write("- aucun")

        self.stdout.write(self.style.SUCCESS("Rapport généré sans données personnelles."))
