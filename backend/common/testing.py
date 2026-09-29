"""MongoDB en mémoire pour les tests unitaires ; transactions testées séparément sur Atlas."""
from unittest.mock import patch
import mongomock
from django.test import SimpleTestCase
from rest_framework.test import APIClient
from common.db import ensure_indexes

class APITestCase(SimpleTestCase):
    def setUp(self):
        self.mongo = mongomock.MongoClient(tz_aware=True)
        self.db = self.mongo.test
        patcher = patch("common.db.database", return_value=self.db)
        patcher.start()
        self.addCleanup(patcher.stop)
        # Les modules importent database directement : remplacer leurs références aussi.
        for module in ("common.views", "delivery.services", "delivery.views", "meals.views", "orders.services"):
            patcher = patch(f"{module}.database", return_value=self.db)
            patcher.start()
            self.addCleanup(patcher.stop)
        for module in ("delivery.services", "orders.services"):
            patcher = patch(f"{module}.transaction", side_effect=lambda callback: callback(None))
            patcher.start()
            self.addCleanup(patcher.stop)
        ensure_indexes()
        self.api = APIClient()

    def client_data(self):
        return {"first_name": "Julien", "last_name": "Test", "email": "julien@example.com", "phone": "0600000000", "address": "10 rue des Tests, Toulouse"}

    def meal_data(self, **kwargs):
        from django.utils import timezone
        return {"name": "Plat", "description": "Test", "price": "10.00", "type": "dish", "date": timezone.localdate().isoformat(), **kwargs}

    def driver_data(self, **kwargs):
        return {"first_name": "Lucas", "last_name": "Test", "phone": "0600000001", **kwargs}
