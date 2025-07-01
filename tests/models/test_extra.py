from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from app.models.basho import Basho
from app.models.bout import Bout
from app.models.division import Division
from app.models.history import BashoHistory
from app.models.rank import Rank
from app.models.rikishi import Heya, Rikishi, Shusshin
from libs.constants import Direction, RankName


class ModelUtilityTests(SimpleTestCase):
    """Unit tests for miscellaneous model helpers."""

    def test_basho_methods(self):
        """``Basho.name`` and ``__str__`` should reflect the tournament."""
        basho = Basho(year=2025, month=1)
        self.assertEqual(basho.name(), "Hatsu")  # Month name
        self.assertEqual(str(basho), "Hatsu 2025")  # Includes year

    def test_basho_slug_generation(self):
        """Saving a ``Basho`` should populate the ``slug`` field."""
        basho = Basho(year=2025, month=3)
        with patch("django.db.models.Model.save") as mock_save:
            basho.save()
            mock_save.assert_called_once()  # Save was triggered
        self.assertEqual(basho.slug, "202503")

    def test_rank_methods(self):
        """Formatting helpers on :class:`Rank` should match expectations."""
        division = Division(name="Makuuchi", name_short="M", level=1)
        rank = Rank(
            division=division,
            title=RankName.YOKOZUNA,
            level=1,
            order=1,
            direction=Direction.EAST,
        )
        self.assertEqual(str(rank), rank.name())  # __str__ proxies name
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
        """Slug generation and string reps for related models."""
        heya = Heya(name="TestBeya")
        with patch("django.db.models.Model.save") as mock_save:
            heya.save()
            mock_save.assert_called_once()  # Save delegated to Model
        self.assertEqual(heya.slug, "testbeya")
        self.assertEqual(str(heya), "TestBeya")

        shusshin = Shusshin(name="Tokyo")
        with patch("django.db.models.Model.save") as mock_save:
            shusshin.save()
            mock_save.assert_called_once()
        self.assertEqual(shusshin.slug, "tokyo")
        self.assertEqual(shusshin.flag(), "🇯🇵")  # Defaults to Japan
        shusshin.international = True
        with patch("pycountry.countries.lookup") as lookup:
            lookup.return_value = SimpleNamespace(flag="🇺🇸")
            self.assertEqual(shusshin.flag(), "🇺🇸")  # Uses lookup flag
            self.assertTrue(str(shusshin).startswith("🇺"))

        with patch("pycountry.countries.lookup") as lookup:
            lookup.side_effect = LookupError
            self.assertEqual(shusshin.flag(), "🏳️")

        rikishi = Rikishi(name="Hakuho", name_jp="白鵬")
        self.assertEqual(str(rikishi), "Hakuho")  # __str__ uses name

    def test_import_history_module(self):
        """The ``history`` submodule should be importable."""
        from app import models  # noqa: F401
        from app.models import history as mod

        self.assertTrue(hasattr(mod, "BashoHistory"))

    def test_bout_str(self):
        """``Bout.__str__`` includes the basho slug."""
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
        self.assertIn("202505", str(bout))  # slug appears in text

    def test_bashohistory_shikona_fields(self):
        """Shikona values should be stored unchanged."""
        division = Division(name="Makuuchi", name_short="M", level=1)
        rank = Rank(division=division, title="Yokozuna", level=1)
        basho = Basho(year=2025, month=1)
        rikishi = Rikishi(name="Hakuho", name_jp="白鵬")
        history = BashoHistory(
            rikishi=rikishi,
            basho=basho,
            rank=rank,
            shikona_en="Hakuho",
            shikona_jp="白鵬",
        )
        self.assertEqual(history.shikona_en, "Hakuho")  # English name
        self.assertEqual(history.shikona_jp, "白鵬")  # Japanese name
