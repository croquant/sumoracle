from django.core.management import call_command
from django.test import TestCase

from app.models import Basho, BashoHistory, Bout, Division, Rank, Rikishi


class GlickoCommandTests(TestCase):
    def setUp(self):
        self.division = Division.objects.get(name="Makuuchi")
        self.rank = Rank.objects.create(
            slug="m1e",
            title="Maegashira",
            level=5,
            order=1,
            direction="East",
            division=self.division,
        )
        self.b1 = Basho.objects.create(year=2025, month=1)
        self.b2 = Basho.objects.create(year=2025, month=3)
        self.r1 = Rikishi.objects.create(id=1, name="A", name_jp="A")
        self.r2 = Rikishi.objects.create(id=2, name="B", name_jp="B")
        BashoHistory.objects.create(
            rikishi=self.r1,
            basho=self.b1,
            rank=self.rank,
        )
        BashoHistory.objects.create(
            rikishi=self.r2,
            basho=self.b1,
            rank=self.rank,
        )
        BashoHistory.objects.create(
            rikishi=self.r1,
            basho=self.b2,
            rank=self.rank,
        )
        BashoHistory.objects.create(
            rikishi=self.r2,
            basho=self.b2,
            rank=self.rank,
        )
        Bout.objects.create(
            basho=self.b1,
            division=self.division,
            day=1,
            match_no=1,
            east=self.r1,
            west=self.r2,
            east_shikona="A",
            west_shikona="B",
            kimarite="yorikiri",
            winner=self.r1,
        )

    def test_ratings_are_computed(self):
        call_command("glicko")
        h1_r1 = BashoHistory.objects.get(rikishi=self.r1, basho=self.b1)
        h1_r2 = BashoHistory.objects.get(rikishi=self.r2, basho=self.b1)
        h2_r1 = BashoHistory.objects.get(rikishi=self.r1, basho=self.b2)
        h2_r2 = BashoHistory.objects.get(rikishi=self.r2, basho=self.b2)
        self.assertGreater(h1_r1.glicko, h1_r2.glicko)
        self.assertAlmostEqual(h2_r1.glicko, h1_r1.glicko, places=5)
        self.assertAlmostEqual(h2_r2.glicko, h1_r2.glicko, places=5)
