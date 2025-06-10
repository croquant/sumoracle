from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from app.models.basho import Basho
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
            title="Yokozuna",
            level=1,
            order=1,
            direction="East",
        )
        self.assertEqual(str(rank), rank.name())
        self.assertEqual(rank.name(), "Yokozuna 1E")
        self.assertEqual(rank.long_name(), "Yokozuna 1 East")
        self.assertEqual(rank.short_name(), "Y1E")

        rank_no_order = Rank(
            division=division,
            title="Ozeki",
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
