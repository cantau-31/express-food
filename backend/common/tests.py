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
