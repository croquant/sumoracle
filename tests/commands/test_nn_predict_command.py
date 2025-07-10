import csv
import os
import tempfile

from django.core.management import call_command
from django.test import TestCase

from app.models import (
    Basho,
    BashoHistory,
    BashoRating,
    Division,
    Prediction,
    Rank,
    Rikishi,
)
from libs.constants import Direction, RankName


class NNPredictCommandTests(TestCase):
    def setUp(self):
        self.division, _ = Division.objects.get_or_create(
            name="Makuuchi", defaults={"name_short": "M", "level": 1}
        )
        self.rank = Rank.objects.create(
            slug="m1e",
            division=self.division,
            title=RankName.MAEGASHIRA,
            order=1,
            direction=Direction.EAST,
        )
        self.b1 = Basho.objects.create(year=2025, month=1)
        self.b2 = Basho.objects.create(year=2025, month=3)
        self.r1 = Rikishi.objects.create(
            id=1, name="A", name_jp="A", rank=self.rank
        )
        self.r2 = Rikishi.objects.create(
            id=2, name="B", name_jp="B", rank=self.rank
        )
        BashoHistory.objects.create(
            rikishi=self.r1, basho=self.b1, rank=self.rank
        )
        BashoHistory.objects.create(
            rikishi=self.r2, basho=self.b1, rank=self.rank
        )
        BashoHistory.objects.create(
            rikishi=self.r1, basho=self.b2, rank=self.rank
        )
        BashoHistory.objects.create(
            rikishi=self.r2, basho=self.b2, rank=self.rank
        )
        BashoRating.objects.create(
            rikishi=self.r1,
            basho=self.b1,
            rating=1510.0,
            rd=200.0,
            vol=0.06,
        )
        BashoRating.objects.create(
            rikishi=self.r2,
            basho=self.b1,
            rating=1500.0,
            rd=200.0,
            vol=0.06,
        )
        self.dataset = tempfile.NamedTemporaryFile("w", delete=False)
        writer = csv.writer(self.dataset)
        writer.writerow(["rating_diff", "rank_diff", "rd_diff", "east_win"])
        writer.writerow([10, 0, 0, 1])
        writer.writerow([-10, 0, 0, 0])
        self.dataset.close()

    def tearDown(self):
        try:
            os.unlink(self.dataset.name)
        except OSError:
            pass

    def test_predictions_saved(self):
        call_command("nn_predict", self.dataset.name, "--iterations", "10")
        preds = Prediction.objects.filter(basho=self.b2)
        self.assertEqual(preds.count(), 2)
        for p in preds:
            self.assertGreaterEqual(p.wins, 0)
            self.assertLessEqual(p.wins, 15)
