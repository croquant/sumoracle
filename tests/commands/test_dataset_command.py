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
    Heya,
    Rank,
    Rikishi,
    Shusshin,
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
        self.heya1 = Heya.objects.create(name="Miyagino")
        self.heya2 = Heya.objects.create(name="Isegahama")
        self.shusshin1 = Shusshin.objects.create(name="Tokyo")
        self.shusshin2 = Shusshin.objects.create(
            name="Mongolia", international=True
        )

        self.r1 = Rikishi.objects.create(
            id=1,
            name="A",
            name_jp="A",
            heya=self.heya1,
            shusshin=self.shusshin1,
        )
        self.r2 = Rikishi.objects.create(
            id=2,
            name="B",
            name_jp="B",
            heya=self.heya2,
            shusshin=self.shusshin2,
        )
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
        rank_idx = headers.index("rank_diff")
        rd_idx = headers.index("rd_diff")
        vol_idx = headers.index("vol_diff")
        east_rd_idx = headers.index("east_rd")
        west_rd_idx = headers.index("west_rd")
        east_vol_idx = headers.index("east_vol")
        west_vol_idx = headers.index("west_vol")
        bmi_idx = headers.index("bmi_diff")
        self.assertEqual(float(data[rating_idx]), 0)
        self.assertEqual(float(data[height_idx]), -2)
        self.assertEqual(float(data[weight_idx]), -5)
        self.assertEqual(data[age_idx], "")
        self.assertEqual(data[exp_idx], "")
        self.assertEqual(float(data[rank_idx]), 0)
        self.assertEqual(float(data[rd_idx]), 0)
        self.assertEqual(float(data[vol_idx]), 0)
        self.assertEqual(float(data[east_rd_idx]), 350)
        self.assertEqual(float(data[west_rd_idx]), 350)
        self.assertAlmostEqual(float(data[east_vol_idx]), 0.11, places=2)
        self.assertAlmostEqual(float(data[west_vol_idx]), 0.11, places=2)
        self.assertAlmostEqual(float(data[bmi_idx]), -0.49, places=2)

        same_heya_idx = headers.index("same_heya")
        same_shusshin_idx = headers.index("same_shusshin")
        east_heya_idx = headers.index("east_heya")
        west_heya_idx = headers.index("west_heya")
        east_shusshin_idx = headers.index("east_shusshin")
        west_shusshin_idx = headers.index("west_shusshin")
        self.assertEqual(int(data[same_heya_idx]), 0)
        self.assertEqual(int(data[same_shusshin_idx]), 0)
        self.assertEqual(int(data[east_heya_idx]), 1)
        self.assertEqual(int(data[west_heya_idx]), 0)
        self.assertEqual(int(data[east_shusshin_idx]), 1)
        self.assertEqual(int(data[west_shusshin_idx]), 0)

        east_win_rate_idx = headers.index("east_win_rate")
        west_win_rate_idx = headers.index("west_win_rate")
        east_streak_idx = headers.index("east_streak")
        west_streak_idx = headers.index("west_streak")
        east_change_idx = headers.index("east_avg_rating_change")
        west_change_idx = headers.index("west_avg_rating_change")
        self.assertEqual(float(data[east_win_rate_idx]), 0)
        self.assertEqual(float(data[west_win_rate_idx]), 0)
        self.assertEqual(int(data[east_streak_idx]), 0)
        self.assertEqual(int(data[west_streak_idx]), 0)
        self.assertEqual(float(data[east_change_idx]), 0)
        self.assertEqual(float(data[west_change_idx]), 0)

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
        diff_idx = headers.index("bmi_diff")
        self.assertEqual(float(data[east_idx]), 46.3)
        self.assertAlmostEqual(float(data[west_idx]), 46.79, places=2)
        self.assertAlmostEqual(float(data[diff_idx]), -0.49, places=2)

    def test_head_to_head_records(self):
        prev = Basho.objects.create(
            year=2024,
            month=11,
            start_date=date(2024, 11, 10),
        )
        division = Division.objects.get(name="Makuuchi")
        Bout.objects.create(
            basho=prev,
            division=division,
            day=1,
            match_no=1,
            east=self.r2,
            west=self.r1,
            east_shikona="B",
            west_shikona="A",
            kimarite="yorikiri",
            winner=self.r2,
        )
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
        target = next(row for row in rows[1:] if row[0] == "2025")
        east_idx = headers.index("east_record")
        west_idx = headers.index("west_record")
        diff_idx = headers.index("record_diff")
        self.assertEqual(int(target[east_idx]), 0)
        self.assertEqual(int(target[west_idx]), 1)
        self.assertEqual(int(target[diff_idx]), -1)

    def test_missing_history(self):
        """Rows should handle bouts missing ``BashoHistory`` entries."""
        r3 = Rikishi.objects.create(id=3, name="C", name_jp="C")
        r4 = Rikishi.objects.create(id=4, name="D", name_jp="D")
        division = Division.objects.get(name="Makuuchi")
        Bout.objects.create(
            basho=self.basho,
            division=division,
            day=2,
            match_no=1,
            east=r3,
            west=r4,
            east_shikona="C",
            west_shikona="D",
            kimarite="oshidashi",
            winner=r3,
        )
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
        target = next(
            row
            for row in rows[1:]
            if row[headers.index("east_id")] == str(r3.id)
        )
        self.assertEqual(target[headers.index("east_height")], "")
        self.assertEqual(target[headers.index("west_weight")], "")
        self.assertEqual(target[headers.index("height_diff")], "")
        self.assertEqual(target[headers.index("rank_diff")], "")
        self.assertEqual(target[headers.index("east_rd")], "")
        self.assertEqual(target[headers.index("west_rd")], "")
        self.assertEqual(target[headers.index("east_vol")], "")
        self.assertEqual(target[headers.index("west_vol")], "")

    def test_rolling_statistics(self):
        prev = Basho.objects.create(
            year=2024,
            month=11,
            start_date=date(2024, 11, 10),
        )
        division = Division.objects.get(name="Makuuchi")
        BashoHistory.objects.create(rikishi=self.r1, basho=prev, rank=self.rank)
        BashoHistory.objects.create(rikishi=self.r2, basho=prev, rank=self.rank)
        BashoRating.objects.create(
            rikishi=self.r1,
            basho=prev,
            rating=1520.0,
            rd=200.0,
            vol=0.06,
        )
        BashoRating.objects.create(
            rikishi=self.r2,
            basho=prev,
            rating=1480.0,
            rd=210.0,
            vol=0.06,
        )
        Bout.objects.create(
            basho=prev,
            division=division,
            day=1,
            match_no=1,
            east=self.r2,
            west=self.r1,
            east_shikona="B",
            west_shikona="A",
            kimarite="yorikiri",
            winner=self.r2,
        )
        rating1 = BashoRating.objects.get(rikishi=self.r1, basho=self.basho)
        rating2 = BashoRating.objects.get(rikishi=self.r2, basho=self.basho)
        rating1.previous_rating = 1520.0
        rating1.rating = 1540.0
        rating1.save()
        rating2.previous_rating = 1480.0
        rating2.rating = 1470.0
        rating2.save()

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
        target = next(row for row in rows[1:] if row[0] == "2025")
        e_wr_idx = headers.index("east_win_rate")
        w_wr_idx = headers.index("west_win_rate")
        e_streak_idx = headers.index("east_streak")
        w_streak_idx = headers.index("west_streak")
        e_delta_idx = headers.index("east_avg_rating_change")
        w_delta_idx = headers.index("west_avg_rating_change")
        self.assertEqual(float(target[e_wr_idx]), 0.0)
        self.assertEqual(float(target[w_wr_idx]), 1.0)
        self.assertEqual(int(target[e_streak_idx]), 0)
        self.assertEqual(int(target[w_streak_idx]), 1)
        self.assertEqual(float(target[e_delta_idx]), 20.0)
        self.assertEqual(float(target[w_delta_idx]), -20.0)

    def test_missing_rating(self):
        """Rows should handle bouts missing ``BashoRating`` entries."""
        r3 = Rikishi.objects.create(id=3, name="C", name_jp="C")
        r4 = Rikishi.objects.create(id=4, name="D", name_jp="D")
        BashoHistory.objects.create(
            rikishi=r3,
            basho=self.basho,
            rank=self.rank,
        )
        BashoHistory.objects.create(
            rikishi=r4,
            basho=self.basho,
            rank=self.rank,
        )
        division = Division.objects.get(name="Makuuchi")
        Bout.objects.create(
            basho=self.basho,
            division=division,
            day=3,
            match_no=1,
            east=r3,
            west=r4,
            east_shikona="C",
            west_shikona="D",
            kimarite="yorikiri",
            winner=r4,
        )
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
        target = next(
            row
            for row in rows[1:]
            if row[headers.index("east_id")] == str(r3.id)
        )
        self.assertEqual(target[headers.index("east_rating")], "")
        self.assertEqual(target[headers.index("west_rating")], "")
        self.assertEqual(target[headers.index("rating_diff")], "")
        self.assertEqual(target[headers.index("rd_diff")], "")
        self.assertEqual(target[headers.index("vol_diff")], "")
        self.assertEqual(target[headers.index("east_rd")], "")
        self.assertEqual(target[headers.index("west_rd")], "")
        self.assertEqual(target[headers.index("east_vol")], "")
        self.assertEqual(target[headers.index("west_vol")], "")
