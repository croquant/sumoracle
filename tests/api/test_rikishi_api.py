from datetime import date

from django.test import TestCase

from app.models.basho import Basho
from app.models.division import Division
from app.models.history import BashoHistory
from app.models.rank import Rank
from app.models.rating import BashoRating
from app.models.rikishi import Heya, Rikishi, Shusshin
from libs.constants import Direction, RankName


class RikishiApiTests(TestCase):
    """Verify the rikishi API endpoints."""

    def setUp(self):
        self.makuuchi = Division.objects.get(name="Makuuchi")
        self.juryo = Division.objects.get(name="Juryo")

        self.rank1 = Rank.objects.create(
            slug="y1e",
            division=self.makuuchi,
            title=RankName.YOKOZUNA,
            order=1,
            direction=Direction.EAST,
        )
        self.rank_j = Rank.objects.create(
            slug="j1e",
            division=self.juryo,
            title=RankName.JURYO,
            order=1,
            direction=Direction.EAST,
        )
        self.heya1 = Heya.objects.create(name="Miyagino")
        self.heya2 = Heya.objects.create(name="Isegahama")

        self.shusshin_jp = Shusshin.objects.create(name="Tokyo")
        self.shusshin_mgl = Shusshin.objects.create(
            name="Mongolia", international=True
        )

        Rikishi.objects.create(
            id=1,
            name="Hakuho",
            name_jp="\u767d\u9dc4",
            heya=self.heya1,
            rank=self.rank1,
            shusshin=self.shusshin_jp,
        )
        Rikishi.objects.create(
            id=2,
            name="Kakuryu",
            name_jp="\u9db4\u7adc",
            heya=self.heya2,
            rank=self.rank_j,
            shusshin=self.shusshin_mgl,
        )
        Rikishi.objects.create(
            id=3,
            name="Chiyotaikai",
            name_jp="\u5343\u4ee3\u5927\u6d77",
            heya=self.heya1,
            shusshin=self.shusshin_jp,
            intai=date(2020, 1, 1),
        )

    def get_json(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_list_active_only(self):
        data = self.get_json("/api/rikishi/")
        names = [r["name"] for r in data]
        self.assertEqual(names, ["Hakuho", "Kakuryu"])

    def test_include_retired(self):
        data = self.get_json("/api/rikishi/?include_retired=1")
        names = [r["name"] for r in data]
        self.assertIn("Chiyotaikai", names)
        self.assertEqual(len(names), 3)

    def test_query_filter(self):
        data = self.get_json("/api/rikishi/?q=Haku")
        names = [r["name"] for r in data]
        self.assertEqual(names, ["Hakuho"])

    def test_heya_filter(self):
        data = self.get_json(f"/api/rikishi/?heya={self.heya2.slug}")
        names = [r["name"] for r in data]
        self.assertEqual(names, ["Kakuryu"])

    def test_division_filter(self):
        data = self.get_json(f"/api/rikishi/?division={self.makuuchi.name}")
        names = [r["name"] for r in data]
        self.assertEqual(names, ["Hakuho"])

    def test_international_filter(self):
        data = self.get_json("/api/rikishi/?international=1")
        names = [r["name"] for r in data]
        self.assertEqual(names, ["Kakuryu"])

    def test_detail_endpoint(self):
        data = self.get_json("/api/rikishi/1/")
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Hakuho")

    def test_detail_not_found(self):
        response = self.client.get("/api/rikishi/99/")
        self.assertEqual(response.status_code, 404)

    def test_history_endpoint(self):
        basho = Basho.objects.create(year=2025, month=1)
        BashoHistory.objects.create(
            rikishi_id=1,
            basho=basho,
            rank=self.rank1,
            height=190.0,
            weight=160.0,
            shikona_en="Hakuho",
            shikona_jp="白鵬",
        )
        data = self.get_json("/api/rikishi/1/history/")
        self.assertEqual(data[0]["basho"], basho.slug)
        self.assertEqual(data[0]["rank"], self.rank1.title)

    def test_ratings_endpoint(self):
        basho = Basho.objects.create(year=2025, month=1)
        BashoRating.objects.create(
            rikishi_id=1,
            basho=basho,
            previous_rating=1500.0,
            previous_rd=350.0,
            previous_vol=0.11,
            rating=1500.0,
            rd=200.0,
            vol=0.06,
        )
        data = self.get_json("/api/rikishi/1/ratings/")
        self.assertEqual(data[0]["basho"], basho.slug)
        self.assertEqual(data[0]["previous_rating"], 1500.0)
        self.assertEqual(data[0]["previous_rd"], 350.0)
        self.assertEqual(data[0]["previous_vol"], 0.11)
        self.assertEqual(data[0]["rating"], 1500.0)
