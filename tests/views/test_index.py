from django.test import TestCase
from django.urls import reverse

from app.models import Basho, Division, Rikishi


class IndexViewTests(TestCase):
    """Verify behaviour of the index view."""

    def setUp(self):
        Basho.objects.create(year=2025, month=1)
        Rikishi.objects.create(id=1, name="Test", name_jp="テスト")

    def test_view_status_code(self):
        """The index view should return HTTP 200."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """The expected template should be used."""
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "index.html")

    def test_view_links_to_division_list(self):
        """Each card should link to the list views."""
        response = self.client.get(reverse("index"))
        self.assertContains(response, reverse("division-list"))
        self.assertContains(response, reverse("rikishi-list"))
        self.assertContains(response, reverse("basho-list"))

    def test_counts_in_context(self):
        """Summary counts should be rendered on the page."""
        response = self.client.get(reverse("index"))
        self.assertContains(response, str(Rikishi.objects.count()))
        self.assertContains(response, str(Basho.objects.first()))
        self.assertContains(response, str(Division.objects.count()))
