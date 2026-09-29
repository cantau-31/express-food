from common.testing import APITestCase

class ClientTests(APITestCase):
    def test_crud_and_unique_email(self):
        response = self.api.post("/api/clients/", self.client_data(), format="json")
        self.assertEqual(response.status_code, 201)
        pk = response.data["id"]
        self.assertEqual(self.api.get(f"/api/clients/{pk}/").status_code, 200)
        duplicate = {**self.client_data(), "email": "JULIEN@example.com"}
        self.assertEqual(self.api.post("/api/clients/", duplicate, format="json").status_code, 400)
        self.assertEqual(self.api.patch(f"/api/clients/{pk}/", {"first_name": "Jules"}, format="json").data["first_name"], "Jules")
        self.assertEqual(self.api.delete(f"/api/clients/{pk}/").status_code, 204)
        self.assertEqual(self.api.get(f"/api/clients/{pk}/").status_code, 404)

    def test_validation(self):
        for data in ({}, {**self.client_data(), "email": "incorrect"}):
            self.assertEqual(self.api.post("/api/clients/", data, format="json").status_code, 400)
        self.assertEqual(self.api.get("/api/clients/bad-id/").status_code, 404)
