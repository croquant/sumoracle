import asyncio
import csv
import tempfile
from datetime import date

from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase
from django.test.utils import CaptureQueriesContext

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
        division, _ = Division.objects.get_or_create(
            name="Makuuchi",
            defaults={"name_short": "M", "level": 1},
        )
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
        headers = rows[0]
        east_idx = headers.index("east_id")
        west_idx = headers.index("west_id")
        win_idx = headers.index("east_win")
        self.assertEqual(int(data[east_idx]), self.r1.id)
        self.assertEqual(int(data[west_idx]), self.r2.id)
        self.assertEqual(int(data[win_idx]), 1)

        rating_idx = headers.index("rating_diff")
        height_idx = headers.index("height_diff")
        weight_idx = headers.index("weight_diff")
        age_idx = headers.index("age_diff")
        exp_idx = headers.index("experience_diff")
        self.assertEqual(float(data[rating_idx]), 0)
        self.assertEqual(float(data[height_idx]), -2)
        self.assertEqual(float(data[weight_idx]), -5)
        self.assertEqual(data[age_idx], "")
        self.assertEqual(data[exp_idx], "")

    def test_query_count_small(self):
        """Exporting multiple bouts should use only a few queries."""
        division, _ = Division.objects.get_or_create(
            name="Makuuchi",
            defaults={"name_short": "M", "level": 1},
        )
        Bout.objects.create(
            basho=self.basho,
            division=division,
            day=2,
            match_no=1,
            east=self.r2,
            west=self.r1,
            east_shikona="B",
            west_shikona="A",
            kimarite="oshidashi",
            winner=self.r2,
        )
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            path = tmp.name
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with CaptureQueriesContext(connection) as ctx:
                call_command("dataset", path)
            self.assertLessEqual(len(ctx), 3)
        finally:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop.close()

    def test_bmi_columns(self):
        """BMI values should be written when height and weight are present."""
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
        headers = rows[0]
        data = rows[1]
        east_idx = headers.index("east_bmi")
        west_idx = headers.index("west_bmi")
        self.assertEqual(float(data[east_idx]), 46.3)
        self.assertAlmostEqual(float(data[west_idx]), 46.79, places=2)
