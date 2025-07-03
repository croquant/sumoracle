import asyncio
import csv
import tempfile
from datetime import date

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


class DatasetCommandTests(TransactionTestCase):
    def setUp(self):
        division = Division.objects.get(name="Makuuchi")
        self.rank = Rank.objects.create(
            slug="m1e",
            division=division,
            title=RankName.MAEGASHIRA,
            order=1,
            direction=Direction.EAST,
        )
        self.basho = Basho.objects.create(
            year=2025,
            month=1,
            start_date=date(2025, 1, 10),
        )
        self.r1 = Rikishi.objects.create(id=1, name="A", name_jp="A")
        self.r2 = Rikishi.objects.create(id=2, name="B", name_jp="B")
        BashoHistory.objects.create(
            rikishi=self.r1,
            basho=self.basho,
            rank=self.rank,
            height=180.0,
            weight=150.0,
        )
        BashoHistory.objects.create(
            rikishi=self.r2,
            basho=self.basho,
            rank=self.rank,
            height=182.0,
            weight=155.0,
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

    def test_dataset_file_created(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = tmp.name
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            call_command("dataset", path)
        finally:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop.close()
        with open(path) as fh:
            rows = list(csv.reader(fh))
        self.assertEqual(rows[0][0], "year")
        self.assertEqual(len(rows), 2)
        data = rows[1]
        self.assertEqual(int(data[5]), self.r1.id)
        self.assertEqual(int(data[6]), self.r2.id)
        self.assertEqual(int(data[-1]), 1)
