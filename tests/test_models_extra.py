from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from app.constants import Direction, RankName
from app.models.basho import Basho
from app.models.bout import Bout
from app.models.division import Division
from app.models.rank import Rank
from app.models.rikishi import Heya, Rikishi, Shusshin


class ModelUtilityTests(SimpleTestCase):
    def test_basho_methods(self):
        basho = Basho(year=2025, month=1)
        self.assertEqual(basho.name(), "Hastu")
        self.assertEqual(str(basho), "Hastu 2025")

    def test_basho_slug_generation(self):
        basho = Basho(year=2025, month=3)
        with patch("django.db.models.Model.save") as mock_save:
            basho.save()
            mock_save.assert_called_once()
        self.assertEqual(basho.slug, "202503")

    def test_rank_methods(self):
        division = Division(name="Makuuchi", name_short="M", level=1)
        rank = Rank(
            division=division,
            title=RankName.YOKOZUNA,
            level=1,
            order=1,
            direction=Direction.EAST,
        )
        self.assertEqual(str(rank), rank.name())
        self.assertEqual(rank.name(), "Yokozuna 1E")
        self.assertEqual(rank.long_name(), "Yokozuna 1 East")
        self.assertEqual(rank.short_name(), "Y1E")

        rank_no_order = Rank(
            division=division,
            title=RankName.OZEKI,
            level=2,
        )
        self.assertEqual(rank_no_order.name(), "Ozeki")
        self.assertEqual(rank_no_order.long_name(), "Ozeki")
        self.assertEqual(rank_no_order.short_name(), "O")

    def test_heya_shusshin_and_rikishi(self):
        heya = Heya(name="TestBeya")
        with patch("django.db.models.Model.save") as mock_save:
            heya.save()
            mock_save.assert_called_once()
        self.assertEqual(heya.slug, "testbeya")
        self.assertEqual(str(heya), "TestBeya")

        shusshin = Shusshin(name="Tokyo")
        with patch("django.db.models.Model.save") as mock_save:
            shusshin.save()
            mock_save.assert_called_once()
        self.assertEqual(shusshin.slug, "tokyo")
        self.assertEqual(shusshin.flag(), "🇯🇵")
        shusshin.international = True
        with patch("pycountry.countries.lookup") as lookup:
            lookup.return_value = SimpleNamespace(flag="🇺🇸")
            self.assertEqual(shusshin.flag(), "🇺🇸")
            self.assertTrue(str(shusshin).startswith("🇺"))

        rikishi = Rikishi(name="Hakuho", name_jp="白鵬")
        self.assertEqual(str(rikishi), "Hakuho")

    def test_import_history_module(self):
        from app import models  # noqa: F401
        from app.models import history as mod

        self.assertTrue(hasattr(mod, "BashoHistory"))

    def test_bout_str(self):
        basho = Basho(year=2025, month=5, slug="202505")
        division = Division(name="Makuuchi", name_short="M", level=1)
        east = Rikishi(id=1, name="East", name_jp="")
        west = Rikishi(id=2, name="West", name_jp="")
        bout = Bout(
            basho=basho,
            division=division,
            day=1,
            match_no=1,
            east=east,
            west=west,
            east_shikona="East",
            west_shikona="West",
            kimarite="yorikiri",
            winner=east,
        )
        self.assertIn("202505", str(bout))
