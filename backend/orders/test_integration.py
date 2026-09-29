"""Tests optionnels sur une base temporaire unique ; jamais sur les collections métier."""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from common.db import database, mongo_client, ensure_indexes
from orders.services import create_order, update_order_status

@skipUnless(os.getenv("RUN_MONGODB_INTEGRATION") == "1", "Nécessite une connexion MongoDB et RUN_MONGODB_INTEGRATION=1")
class MongoIntegrationTests(SimpleTestCase):
    def setUp(self):
        self.name = "express_food_test_" + uuid.uuid4().hex
        override = override_settings(MONGODB_DATABASE=self.name)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(lambda: mongo_client().drop_database(self.name))
        ensure_indexes()
        self.db = database()
        client = self.db.clients.insert_one({"email": "integration@example.com"}).inserted_id
        meal = self.db.meals.insert_one({"name": "Repas test", "price": "19.99", "available": True,
                                        "date": timezone.localdate().isoformat()}).inserted_id
        self.driver = self.db.delivery_drivers.insert_one({"status": "available", "first_name": "Test"}).inserted_id
        self.data = {"client_id": str(client), "items": [{"meal_id": str(meal), "quantity": 1}]}

    def test_concurrent_assignment_and_release(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            orders = list(pool.map(lambda _: create_order(self.data), range(2)))
        assigned = [order for order in orders if order["delivery_driver_id"]]
        self.assertEqual(len(assigned), 1)
        self.assertEqual(self.db.orders.count_documents({}), 2)
        update_order_status(str(assigned[0]["_id"]), "delivered")
        self.assertEqual(self.db.delivery_drivers.find_one({"_id": self.driver})["status"], "available")

    def test_transaction_rolls_back_driver_on_insert_failure(self):
        from pymongo.synchronous.collection import Collection
        original = Collection.insert_one
        def fail_orders(collection, *args, **kwargs):
            if collection.name == "orders":
                raise RuntimeError("Échec simulé après réservation du livreur")
            return original(collection, *args, **kwargs)
        with patch.object(Collection, "insert_one", fail_orders):
            with self.assertRaises(RuntimeError):
                create_order(self.data)
        self.assertEqual(self.db.orders.count_documents({}), 0)
        self.assertEqual(self.db.delivery_drivers.find_one({"_id": self.driver})["status"], "available")
