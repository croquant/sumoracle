from django.test import TestCase

from app.models.basho import Basho
from app.models.bout import Bout
from app.models.division import Division
from app.models.rikishi import Rikishi


class BoutApiTests(TestCase):
    """Verify the basho bouts API endpoint."""

    def setUp(self):
        self.div_m = Division.objects.get(name="Makuuchi")
        self.div_j = Division.objects.get(name="Juryo")
        self.basho = Basho.objects.create(year=2025, month=1)
        self.r1 = Rikishi.objects.create(id=1, name="A", name_jp="A")
        self.r2 = Rikishi.objects.create(id=2, name="B", name_jp="B")
        self.r3 = Rikishi.objects.create(id=3, name="C", name_jp="C")
        Bout.objects.create(
            basho=self.basho,
            division=self.div_m,
            day=1,
            match_no=1,
            east=self.r1,
            west=self.r2,
            east_shikona="A",
            west_shikona="B",
            kimarite="yorikiri",
            winner=self.r1,
        )
        Bout.objects.create(
            basho=self.basho,
            division=self.div_j,
            day=2,
            match_no=1,
            east=self.r2,
            west=self.r3,
            east_shikona="B",
            west_shikona="C",
            kimarite="uwatenage",
            winner=self.r3,
        )

    def get_json(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_list_all(self):
        data = self.get_json(f"/api/basho/{self.basho.slug}/bouts/")
        self.assertEqual(len(data), 2)

    def test_division_filter(self):
        data = self.get_json(
            f"/api/basho/{self.basho.slug}/bouts/?division={self.div_m.name}"
        )
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["division"], "Makuuchi")

    def test_day_filter(self):
        data = self.get_json(f"/api/basho/{self.basho.slug}/bouts/?day=2")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["day"], 2)

    def test_rikishi_filter(self):
        data = self.get_json(
            f"/api/basho/{self.basho.slug}/bouts/?rikishi_id=1"
        )
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["east"], "A")

    def test_no_extra_queries(self):
        """Fetching bouts should use a single optimized query."""
        with self.assertNumQueries(1):
            self.get_json(f"/api/basho/{self.basho.slug}/bouts/")
