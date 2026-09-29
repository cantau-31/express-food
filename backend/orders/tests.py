from bson import ObjectId
from common.testing import APITestCase

class OrderTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.customer = self.api.post("/api/clients/", self.client_data(), format="json").data
        self.meal = self.api.post("/api/meals/", self.meal_data(), format="json").data

    def order(self, quantity=1, **extra):
        data = {"client_id": self.customer["id"], "items": [{"meal_id": self.meal["id"], "quantity": quantity}], **extra}
        return self.api.post("/api/orders/", data, format="json")

    def test_totals_and_no_driver(self):
        response = self.order(total="0.01", subtotal="0.01", delivery_fee="0.00")
        self.assertEqual(response.status_code, 201)
        order = response.data
        self.assertEqual((order["subtotal"], order["delivery_fee"], order["total"]), ("10.00", "2.99", "12.99"))
        self.assertEqual(order["status"], "pending")
        self.assertIsNone(order["delivery_driver_id"])
        tracking = self.api.get(f"/api/orders/{order['id']}/status/").data
        self.assertIsNone(tracking["driver"])
        self.assertIsNone(tracking["estimated_delivery_minutes"])

    def test_free_delivery_threshold(self):
        for price, expected in (("19.98", "2.99"), ("19.99", "0.00"), ("20.00", "0.00")):
            self.api.patch(f"/api/meals/{self.meal['id']}/", {"price": price}, format="json")
            self.assertEqual(self.order().data["delivery_fee"], expected)

    def test_exact_decimal_and_quantities(self):
        self.api.patch(f"/api/meals/{self.meal['id']}/", {"price": "0.10"}, format="json")
        response = self.order(3)
        self.assertEqual(response.data["subtotal"], "0.30")
        self.assertEqual(response.data["items"][0]["subtotal"], "0.30")
        self.assertEqual(response.data["total"], "3.29")

    def test_assignment_tracking_and_release(self):
        driver = self.api.post("/api/delivery-drivers/", self.driver_data(latitude=43.6, longitude=1.4), format="json").data
        order = self.order(2).data
        self.assertEqual(order["delivery_driver_id"], driver["id"])
        self.assertEqual(order["status"], "accepted")
        driver_url = f"/api/delivery-drivers/{driver['id']}/"
        self.assertEqual(self.api.get(driver_url).data["status"], "delivering")
        self.assertEqual(self.api.patch(driver_url, {"status": "available"}, format="json").status_code, 400)
        self.assertIsNone(self.order().data["delivery_driver_id"])
        tracking = self.api.get(f"/api/orders/{order['id']}/status/").data
        self.assertEqual(tracking["driver"]["first_name"], "Lucas")
        self.assertEqual(tracking["driver"]["latitude"], 43.6)
        url = f"/api/orders/{order['id']}/status/"
        self.assertEqual(self.api.patch(url, {"status": "delivered"}, format="json").status_code, 200)
        self.assertEqual(self.api.get(driver_url).data["status"], "available")
        self.assertEqual(self.api.patch(url, {"status": "accepted"}, format="json").status_code, 400)
        # Répéter delivered sur l'ancienne commande ne doit pas libérer le livreur réaffecté.
        self.order()
        self.api.patch(url, {"status": "delivered"}, format="json")
        self.assertEqual(self.api.get(driver_url).data["status"], "delivering")

    def test_invalid_references_and_items(self):
        self.assertEqual(self.order(client_id=str(ObjectId())).status_code, 404)
        self.assertEqual(self.order(items=[{"meal_id": str(ObjectId()), "quantity": 1}]).status_code, 404)
        for items in ([], [{"meal_id": "invalid", "quantity": 1}], [{"meal_id": self.meal["id"], "quantity": 0}], [{"meal_id": self.meal["id"], "quantity": 1.5}]):
            self.assertEqual(self.order(items=items).status_code, 400)
        self.assertEqual(self.db.orders.count_documents({}), 0)

    def test_unavailable_or_old_meal(self):
        for data in ({"available": False}, {"available": True, "date": "2020-01-01"}):
            self.api.patch(f"/api/meals/{self.meal['id']}/", data, format="json")
            self.assertEqual(self.order().status_code, 400)

    def test_pending_retry_and_cancellation(self):
        order = self.order().data
        url = f"/api/orders/{order['id']}/status/"
        self.assertEqual(self.api.patch(url, {"status": "accepted"}, format="json").status_code, 400)
        driver = self.api.post("/api/delivery-drivers/", self.driver_data(), format="json").data
        self.assertEqual(self.api.patch(url, {"status": "accepted"}, format="json").status_code, 200)
        self.assertEqual(self.api.patch(url, {"status": "cancelled"}, format="json").status_code, 200)
        self.assertEqual(self.api.get(f"/api/delivery-drivers/{driver['id']}/").data["status"], "available")

    def test_order_is_not_editable(self):
        order = self.order().data
        self.assertEqual(self.api.patch(f"/api/orders/{order['id']}/", {"total": "0.00"}, format="json").status_code, 405)
