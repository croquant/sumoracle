from datetime import date

from django.test import TestCase
from django.urls import reverse

from app.models.division import Division
from app.models.rank import Rank
from app.models.rikishi import Heya, Rikishi, Shusshin
from libs.constants import Direction, RankName


class RikishiListViewTests(TestCase):
    """Verify behaviour of the rikishi list view."""

    def setUp(self):
        self.makuuchi = Division.objects.get(name="Makuuchi")
        self.juryo = Division.objects.get(name="Juryo")

        self.rank1 = Rank.objects.create(
            slug="y1e",
            division=self.makuuchi,
            title=RankName.YOKOZUNA,
            order=1,
            direction=Direction.EAST,
        )
        self.rank_j = Rank.objects.create(
            slug="j1e",
            division=self.juryo,
            title=RankName.JURYO,
            order=1,
            direction=Direction.EAST,
        )
        self.heya1 = Heya.objects.create(name="Miyagino")
        self.heya2 = Heya.objects.create(name="Isegahama")

        self.shusshin_jp = Shusshin.objects.create(name="Tokyo")
        self.shusshin_mgl = Shusshin.objects.create(
            name="Mongolia", international=True
        )

        Rikishi.objects.create(
            id=1,
            name="Hakuho",
            name_jp="白鵬",
            heya=self.heya1,
            rank=self.rank1,
            shusshin=self.shusshin_jp,
        )
        Rikishi.objects.create(
            id=2,
            name="Kakuryu",
            name_jp="鶴竜",
            heya=self.heya2,
            rank=self.rank_j,
            shusshin=self.shusshin_mgl,
        )
        Rikishi.objects.create(
            id=3,
            name="Chiyotaikai",
            name_jp="千代大海",
            heya=self.heya1,
            shusshin=self.shusshin_jp,
            intai=date(2020, 1, 1),
        )

    def test_view_status_code(self):
        """The list view should return HTTP 200."""
        response = self.client.get(reverse("rikishi-list"))
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """The expected template should be used."""
        response = self.client.get(reverse("rikishi-list"))
        self.assertTemplateUsed(response, "rikishi_list.html")

    def test_view_lists_active_by_default(self):
        """Only active rikishi should be listed without parameters."""
        response = self.client.get(reverse("rikishi-list"))
        self.assertEqual(
            response.context["paginator"].count,
            Rikishi.objects.filter(intai__isnull=True).count(),
        )
        names = [r.name for r in response.context["object_list"]]
        self.assertNotIn("Chiyotaikai", names)

    def test_include_retired_filter(self):
        """Including retired rikishi should list all wrestlers."""
        url = reverse("rikishi-list") + "?include_retired=1"
        response = self.client.get(url)
        self.assertEqual(
            response.context["paginator"].count,
            Rikishi.objects.count(),
        )
        self.assertFalse(response.context["active_only"])

    def test_names_link_to_detail(self):
        """Each rikishi name should link to the detail view."""
        url = reverse("rikishi-list") + "?include_retired=1"
        response = self.client.get(url)
        for rikishi in Rikishi.objects.all():
            detail_url = reverse("rikishi-detail", args=[rikishi.id])
            self.assertContains(response, f'href="{detail_url}"')

    def test_query_filter(self):
        """Filtering by search term should narrow results."""
        url = reverse("rikishi-list") + "?q=Haku"
        response = self.client.get(url)
        names = [r.name for r in response.context["object_list"]]
        self.assertEqual(names, ["Hakuho"])

    def test_heya_filter(self):
        """Filtering by heya should return matching rikishi only."""
        url = reverse("rikishi-list") + f"?heya={self.heya2.slug}"
        response = self.client.get(url)
        names = [r.name for r in response.context["object_list"]]
        self.assertEqual(names, ["Kakuryu"])

    def test_division_filter(self):
        """Filtering by division should return matching rikishi."""
        url = reverse("rikishi-list") + f"?division={self.makuuchi.name}"
        response = self.client.get(url)
        names = [r.name for r in response.context["object_list"]]
        self.assertEqual(names, ["Hakuho"])

    def test_international_filter(self):
        """Filtering for internationals returns only foreign wrestlers."""
        url = reverse("rikishi-list") + "?international=1"
        response = self.client.get(url)
        names = [r.name for r in response.context["object_list"]]
        self.assertEqual(names, ["Kakuryu"])

    def test_status_field_display(self):
        """Rows should indicate whether a rikishi is active or retired."""
        url = reverse("rikishi-list") + "?include_retired=1"
        response = self.client.get(url)
        self.assertContains(response, "Active")
        self.assertContains(response, "Retired")
