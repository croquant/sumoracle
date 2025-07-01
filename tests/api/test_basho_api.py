from django.test import TestCase

from app.models.basho import Basho


class BashoApiTests(TestCase):
    """Verify the basho API endpoints."""

    def setUp(self):
        self.b1 = Basho.objects.create(year=2025, month=1)
        self.b2 = Basho.objects.create(year=2025, month=3)

    def get_json(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def get_slugs(self, data):
        return [b["slug"] for b in data["items"]]

    def test_list_endpoint(self):
        data = self.get_json("/api/basho/")
        self.assertEqual(self.get_slugs(data), [self.b2.slug, self.b1.slug])

    def test_detail_endpoint(self):
        data = self.get_json(f"/api/basho/{self.b1.slug}/")
        self.assertEqual(data["slug"], self.b1.slug)
        self.assertEqual(data["year"], 2025)
        self.assertEqual(data["month"], 1)

    def test_limit_offset(self):
        data = self.get_json("/api/basho/?limit=1&offset=1")
        self.assertEqual(data["limit"], 1)
        self.assertEqual(self.get_slugs(data), [self.b1.slug])
