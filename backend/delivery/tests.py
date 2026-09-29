from common.testing import APITestCase

class DriverTests(APITestCase):
    def test_status_location_and_available(self):
        driver = self.api.post("/api/delivery-drivers/", self.driver_data(), format="json").data
        url = f"/api/delivery-drivers/{driver['id']}/"
        self.assertEqual(len(self.api.get("/api/delivery-drivers/available/").data), 1)
        self.assertEqual(self.api.patch(url + "location/", {"latitude": 43.6045, "longitude": 1.444}, format="json").status_code, 200)
        for data in ({"latitude": 91, "longitude": 0}, {"latitude": 0}, {"latitude": 0, "longitude": 181}):
            self.assertEqual(self.api.patch(url + "location/", data, format="json").status_code, 400)
        self.assertEqual(self.api.patch(url + "status/", {"status": "offline"}, format="json").status_code, 200)
        self.assertEqual(len(self.api.get("/api/delivery-drivers/available/").data), 0)
        self.assertEqual(self.api.patch(url, {"status": "delivering"}, format="json").status_code, 400)
