from common.testing import APITestCase

class MealTests(APITestCase):
    def test_today_only_available(self):
        for extra in ({}, {"type": "dessert"}, {"available": False}, {"date": "2020-01-01"}):
            self.assertEqual(self.api.post("/api/meals/", self.meal_data(**extra), format="json").status_code, 201)
        response = self.api.get("/api/meals/today/")
        self.assertEqual(len(response.data), 2)
        self.assertEqual({meal["type"] for meal in response.data}, {"dish", "dessert"})

    def test_invalid_price_and_type(self):
        for extra in ({"price": "-1"}, {"price": "1.001"}, {"type": "drink"}):
            self.assertEqual(self.api.post("/api/meals/", self.meal_data(**extra), format="json").status_code, 400)
