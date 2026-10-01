from django.core.management.base import BaseCommand, CommandError

from common.db import database

EXPECTED_INDEXES = {
    "clients": {
        "email_1": {"unique": True},
    },
    "meals": {
        "date_1_available_1": {},
    },
    "delivery_drivers": {
        "status_1": {},
        "active_order_id_1": {},
    },
    "orders": {
        "client_id_1": {},
        "status_1": {},
        "delivery_driver_id_1": {},
        "created_at_1": {},
    },
}


class Command(BaseCommand):
    help = "Vérifie que les index MongoDB attendus sont présents."

    def handle(self, *args, **options):
        db = database()
        missing = []
        invalid = []

        for collection_name, expected in EXPECTED_INDEXES.items():
            existing = db[collection_name].index_information()
            for index_name, requirements in expected.items():
                index = existing.get(index_name)
                if index is None:
                    missing.append(f"{collection_name}.{index_name}")
                    continue

                if requirements.get("unique") and not index.get("unique", False):
                    invalid.append(f"{collection_name}.{index_name} (unique attendu)")

        if missing or invalid:
            for item in missing:
                self.stderr.write(self.style.ERROR(f"- index manquant : {item}"))
            for item in invalid:
                self.stderr.write(self.style.ERROR(f"- index invalide : {item}"))
            raise CommandError("Configuration des index MongoDB incorrecte.")

        self.stdout.write(self.style.SUCCESS("Index MongoDB : OK"))
