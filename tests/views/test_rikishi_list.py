from datetime import date

from django.test import TestCase
from django.urls import reverse

from app.models.rikishi import Rikishi


class RikishiListViewTests(TestCase):
    """Verify behaviour of the rikishi list view."""

    def setUp(self):
        Rikishi.objects.create(id=1, name="Hakuho", name_jp="白鵬")
        Rikishi.objects.create(id=2, name="Kakuryu", name_jp="鶴竜")
        Rikishi.objects.create(
            id=3,
            name="Chiyotaikai",
            name_jp="千代大海",
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

    def test_view_lists_all_rikishi(self):
        """Paginator count should match the database."""
        response = self.client.get(reverse("rikishi-list"))
        self.assertEqual(
            response.context["paginator"].count,
            Rikishi.objects.count(),
        )

    def test_active_filter(self):
        """Filtering by active should exclude retired rikishi."""
        url = reverse("rikishi-list") + "?active=1"
        response = self.client.get(url)
        names = [r.name for r in response.context["object_list"]]
        self.assertNotIn("Chiyotaikai", names)
        self.assertEqual(
            response.context["paginator"].count,
            Rikishi.objects.filter(intai__isnull=True).count(),
        )
        self.assertTrue(response.context["active_only"])

    def test_names_link_to_detail(self):
        """Each rikishi name should link to the detail view."""
        response = self.client.get(reverse("rikishi-list"))
        for rikishi in Rikishi.objects.all():
            detail_url = reverse("rikishi-detail", args=[rikishi.id])
            self.assertContains(response, f'href="{detail_url}"')
