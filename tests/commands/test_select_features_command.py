import asyncio
import csv
import io
import tempfile

from django.core.management import call_command
from django.test import TransactionTestCase

from app.models import (
    Basho,
    BashoHistory,
    BashoRating,
    Bout,
    Division,
    Rank,
    Rikishi,
)
from libs.constants import Direction, RankName


class SelectFeaturesCommandTests(TransactionTestCase):
    def setUp(self):
        division, _ = Division.objects.get_or_create(
            name="Makuuchi", defaults={"name_short": "M", "level": 1}
        )
        self.rank = Rank.objects.create(
            slug="m1e",
            division=division,
            title=RankName.MAEGASHIRA,
            order=1,
            direction=Direction.EAST,
        )
        self.basho = Basho.objects.create(year=2025, month=1)
        self.r1 = Rikishi.objects.create(id=1, name="A", name_jp="A")
        self.r2 = Rikishi.objects.create(id=2, name="B", name_jp="B")
        BashoHistory.objects.create(
            rikishi=self.r1,
            basho=self.basho,
            rank=self.rank,
        )
        BashoHistory.objects.create(
            rikishi=self.r2,
            basho=self.basho,
            rank=self.rank,
        )
        BashoRating.objects.create(
            rikishi=self.r1,
            basho=self.basho,
            rating=1500.0,
            rd=200.0,
            vol=0.06,
        )
        BashoRating.objects.create(
            rikishi=self.r2,
            basho=self.basho,
            rating=1490.0,
            rd=210.0,
            vol=0.06,
        )
        Bout.objects.create(
            basho=self.basho,
            division=division,
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
            division=division,
            day=1,
            match_no=2,
            east=self.r2,
            west=self.r1,
            east_shikona="B",
            west_shikona="A",
            kimarite="yorikiri",
            winner=self.r2,
        )

    def test_reduced_file_created(self):
        with tempfile.NamedTemporaryFile(delete=False) as ds:
            dataset_path = ds.name
        with tempfile.NamedTemporaryFile(delete=False) as out:
            out_path = out.name
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        out = io.StringIO()
        try:
            call_command("dataset", dataset_path)
            call_command(
                "select_features",
                dataset_path,
                out_path,
                "--k",
                "5",
                stdout=out,
            )
        finally:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop.close()
        with open(out_path) as fh:
            reader = csv.reader(fh)
            headers = next(reader)
        self.assertLessEqual(len(headers), 6)
        self.assertIn("Selected features with scores:", out.getvalue())
