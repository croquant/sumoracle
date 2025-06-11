from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    """Verify behaviour of the index view."""

    def test_view_status_code(self):
        """The index view should return HTTP 200."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        """The expected template should be used."""
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "index.html")

    def test_view_links_to_division_list(self):
        """The page should provide a link to the divisions list."""
        response = self.client.get(reverse("index"))
        self.assertContains(response, reverse("division-list"))
