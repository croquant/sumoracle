from django.test import TestCase

from app.models.division import Division


class DivisionApiTests(TestCase):
    """Verify the division API endpoints."""

    def get_json(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_list_endpoint(self):
        data = self.get_json("/api/division/")
        names = [d["name"] for d in data]
        expected = list(Division.objects.values_list("name", flat=True))
        self.assertEqual(names, expected)

    def test_detail_endpoint(self):
        data = self.get_json("/api/division/makuuchi/")
        self.assertEqual(data["name"], "Makuuchi")
        self.assertEqual(data["name_short"], "M")
        self.assertEqual(data["level"], 1)

    def test_detail_not_found(self):
        response = self.client.get("/api/division/unknown/")
        self.assertEqual(response.status_code, 404)
