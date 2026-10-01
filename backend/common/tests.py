from io import StringIO
from unittest.mock import patch
from django.core.management import call_command
from pymongo.errors import ServerSelectionTimeoutError
from common.testing import APITestCase

class InfrastructureTests(APITestCase):
    def test_seed_is_repeatable(self):
        with patch("common.management.commands.seed_data.database", return_value=self.db):
            for _ in range(2):
                call_command("seed_data", stdout=StringIO())
        self.assertEqual(self.db.clients.count_documents({}), 2)
        self.assertEqual(self.db.meals.count_documents({}), 4)
        self.assertEqual(self.db.delivery_drivers.count_documents({}), 3)

    def test_database_unavailable_returns_json(self):
        with patch("common.views.database", side_effect=ServerSelectionTimeoutError("private connection details")):
            response = self.api.get("/api/clients/")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", str(response.data))

    def test_cors_and_malformed_json(self):
        response = self.api.options("/api/meals/", HTTP_ORIGIN="http://localhost:5173", HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET")
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:5173")
        response = self.api.options("/api/meals/", HTTP_ORIGIN="https://unknown.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET")
        self.assertNotIn("Access-Control-Allow-Origin", response)
        self.assertEqual(self.api.post("/api/clients/", "{broken", content_type="application/json").status_code, 400)

    def test_unknown_route_is_json_in_debug(self):
        with self.settings(DEBUG=True):
            response = self.api.get("/api/unknown/")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Route introuvable."})


    def test_db_status_command(self):
        from unittest.mock import MagicMock
        from django.test import override_settings

        self.db.clients.insert_one({"email": "status@example.com"})
        fake_client = MagicMock()
        fake_client.admin.command.return_value = {"ok": 1.0}

        with override_settings(MONGODB_URI="mongodb://example", MONGODB_DATABASE="test"):
            with patch("common.management.commands.db_status.mongo_client", return_value=fake_client):
                with patch("common.management.commands.db_status.database", return_value=self.db):
                    out = StringIO()
                    call_command("db_status", stdout=out)

        output = out.getvalue()
        self.assertIn("Connexion MongoDB : OK", output)
        self.assertIn("clients: 1 document(s)", output)
        self.assertIn("orders:", output)


    def test_health_endpoint(self):
        from unittest.mock import MagicMock

        fake_client = MagicMock()
        fake_client.admin.command.return_value = {"ok": 1.0}
        with patch("common.views.mongo_client", return_value=fake_client):
            response = self.api.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})

        with patch("common.views.mongo_client") as mocked:
            mocked.return_value.admin.command.side_effect = ServerSelectionTimeoutError("private details")
            response = self.api.get("/api/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "degraded", "database": "unavailable"})
        self.assertNotIn("private", str(response.data))


    def test_verify_data_command(self):
        from bson import ObjectId

        client_id = self.db.clients.insert_one({"email": "audit@example.com"}).inserted_id
        driver_id = self.db.delivery_drivers.insert_one({
            "first_name": "Audit",
            "status": "available",
            "latitude": None,
            "longitude": None,
            "active_order_id": None,
        }).inserted_id
        self.db.orders.insert_one({
            "client_id": str(client_id),
            "status": "accepted",
            "delivery_driver_id": str(driver_id),
        })

        with patch("common.management.commands.verify_data.database", return_value=self.db):
            out = StringIO()
            call_command("verify_data", stdout=out)
        self.assertIn("Intégrité des données : OK", out.getvalue())

        self.db.orders.insert_one({
            "client_id": str(ObjectId()),
            "status": "broken",
            "delivery_driver_id": None,
        })
        with patch("common.management.commands.verify_data.database", return_value=self.db):
            with self.assertRaises(Exception):
                call_command("verify_data", stdout=StringIO(), stderr=StringIO())


    def test_preflight_command(self):
        from unittest.mock import call, patch as mock_patch

        with mock_patch("common.management.commands.preflight.call_command") as mocked:
            out = StringIO()
            call_command("preflight", stdout=out)

        self.assertEqual(
            mocked.call_args_list,
            [
                call("check_mongodb", stdout=mocked.call_args_list[0].kwargs["stdout"], stderr=mocked.call_args_list[0].kwargs["stderr"]),
                call("verify_data", stdout=mocked.call_args_list[1].kwargs["stdout"], stderr=mocked.call_args_list[1].kwargs["stderr"]),
            ],
        )
        self.assertIn("Préflight Data / intégration : OK", out.getvalue())
