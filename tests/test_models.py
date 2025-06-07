from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.urls import reverse

from app.admin.division import DivisionAdmin
from app.models.basho import Basho
from app.models.division import Division
from app.models.rank import Rank
from app.models.rikishi import Heya, Rikishi, Shusshin


class DivisionModelTests(TestCase):
    def test_str_returns_name(self):
        division = Division.objects.get(name="Makuuchi")
        self.assertEqual(str(division), "Makuuchi")

    def test_get_absolute_url(self):
        division = Division.objects.get(name="Makuuchi")
        expected_url = reverse("division-detail", args=["makuuchi"])
        self.assertEqual(division.get_absolute_url(), expected_url)


class DivisionAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = DivisionAdmin(Division, self.site)

    def test_all_permissions_disabled(self):
        self.assertFalse(self.admin.has_add_permission(None))
        self.assertFalse(self.admin.has_change_permission(None))
        self.assertFalse(self.admin.has_delete_permission(None))


class BashoModelExtraTests(TestCase):
    def test_name_and_str(self):
        basho = Basho(slug="202401", year=2024, month=1)
        self.assertEqual(basho.name(), "Hastu")
        self.assertEqual(str(basho), "Hastu 2024")


class RankModelExtraTests(TestCase):
    def setUp(self):
        self.division = Division.objects.get(name="Makuuchi")

    def test_string_helpers_with_order(self):
        rank = Rank(
            slug="m1e",
            division=self.division,
            title="Maegashira",
            level=5,
            order=1,
            direction="East",
        )
        self.assertEqual(rank.name(), "Maegashira 1E")
        self.assertEqual(str(rank), "Maegashira 1E")
        self.assertEqual(rank.long_name(), "Maegashira 1 East")
        self.assertEqual(rank.short_name(), "M1E")

    def test_string_helpers_no_order(self):
        rank = Rank(
            slug="y",
            division=self.division,
            title="Yokozuna",
            level=1,
        )
        self.assertEqual(rank.name(), "Yokozuna")
        self.assertEqual(rank.long_name(), "Yokozuna")
        self.assertEqual(rank.short_name(), "Y")


class RikishiRelatedModelTests(TestCase):
    def test_heya_save_and_str(self):
        heya = Heya(name="Test Stable")
        with patch(
            "django.db.models.base.Model.save", return_value=None
        ) as super_save:
            heya.save()
            super_save.assert_called_once()
        self.assertEqual(heya.slug, "test-stable")
        self.assertEqual(str(heya), "Test Stable")

    def test_shusshin_save_flag_and_str(self):
        local = Shusshin(name="Tokyo", international=False)
        with patch("django.db.models.base.Model.save", return_value=None):
            local.save()
        self.assertEqual(local.slug, "tokyo")
        self.assertEqual(local.flag(), "\U0001f1ef\U0001f1f5")
        self.assertEqual(str(local), "\U0001f1ef\U0001f1f5Tokyo")

        with patch("pycountry.countries.lookup") as lookup:
            lookup.return_value = SimpleNamespace(flag="\U0001f1fa\U0001f1f8")
            intl = Shusshin(name="USA", international=True)
            with patch("django.db.models.base.Model.save", return_value=None):
                intl.save()
            self.assertEqual(intl.slug, "usa")
            self.assertEqual(intl.flag(), "\U0001f1fa\U0001f1f8")
            self.assertEqual(str(intl), "\U0001f1fa\U0001f1f8USA")

    def test_rikishi_str(self):
        rikishi = Rikishi(id=1, name="Hakuho", name_jp="\u767d\u9cf4")
        self.assertEqual(str(rikishi), "Hakuho")
