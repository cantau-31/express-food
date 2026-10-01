"""Tests de la couche Data & integration : sauvegarde, restauration, controle d'integrite.

Complementaires aux tests de Julien : ceux-ci ciblent les outils data ajoutes ici,
pas le CRUD ni les regles metier (deja couverts par les tests par application).
"""
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from bson import ObjectId
from django.core.management import call_command
from django.core.management.base import CommandError

from common.data_ops import check_integrity, export_collections, import_collections
from common.testing import APITestCase


class DataOpsTests(APITestCase):
    def setUp(self):
        super().setUp()
        patcher = patch("common.data_ops.database", return_value=self.db)
        patcher.start()
        self.addCleanup(patcher.stop)
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        # Un jeu de donnees complet et coherent, cree via l'API publique.
        self.customer = self.api.post("/api/clients/", self.client_data(), format="json").data
        self.meal = self.api.post("/api/meals/", self.meal_data(), format="json").data
        self.api.post("/api/delivery-drivers/", self.driver_data(), format="json")
        self.order = self.api.post(
            "/api/orders/",
            {"client_id": self.customer["id"], "items": [{"meal_id": self.meal["id"], "quantity": 2}]},
            format="json",
        ).data

    def test_backup_then_restore_round_trip(self):
        path = self.tmp / "dump.json"
        counts = export_collections(str(path))
        self.assertTrue(path.exists())
        self.assertEqual(counts, {"clients": 1, "meals": 1, "delivery_drivers": 1, "orders": 1})
        # Simuler une perte de donnees, puis restaurer.
        for name in ("clients", "meals", "delivery_drivers", "orders"):
            self.db[name].drop()
        self.assertEqual(self.db.clients.count_documents({}), 0)
        restored = import_collections(str(path))
        self.assertEqual(restored, counts)
        self.assertEqual(self.db.clients.find_one()["email"], self.customer["email"])
        self.assertEqual(self.db.orders.find_one()["total"], self.order["total"])
        self.assertIsInstance(self.db.orders.find_one()["_id"], ObjectId)

    def test_backup_and_restore_commands(self):
        path = self.tmp / "cli.json"
        call_command("backup_data", output=str(path), stdout=StringIO())
        self.db.clients.drop()
        call_command("restore_data", input=str(path), stdout=StringIO())
        self.assertEqual(self.db.clients.count_documents({}), 1)

    def test_restore_missing_file_raises(self):
        with self.assertRaises(CommandError):
            call_command("restore_data", input=str(self.tmp / "absent.json"), stdout=StringIO())

    def test_integrity_passes_on_consistent_data(self):
        self.assertEqual(check_integrity(), [])

    def test_integrity_detects_dangling_client_reference(self):
        order_id = self.db.orders.find_one()["_id"]
        self.db.orders.update_one({"_id": order_id}, {"$set": {"client_id": str(ObjectId())}})
        self.assertTrue(any("client_id introuvable" in item for item in check_integrity()))

    def test_integrity_detects_wrong_total(self):
        order_id = self.db.orders.find_one()["_id"]
        self.db.orders.update_one({"_id": order_id}, {"$set": {"total": "0.00"}})
        self.assertTrue(any("total" in item for item in check_integrity()))
