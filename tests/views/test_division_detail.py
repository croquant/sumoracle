from django.test import TestCase
from django.urls import reverse

from app.models.division import Division


class DivisionDetailViewTests(TestCase):
    """Verify behaviour of the division detail view."""

    def test_view_status_code(self):
        """The detail view should return HTTP 200."""
        division = Division.objects.get(name="Makuuchi")
        response = self.client.get(
            reverse("division-detail", args=[division.name])
        )
        self.assertEqual(response.status_code, 200)  # Success

    def test_view_template(self):
        """The expected template should be used."""
        division = Division.objects.get(name="Makuuchi")
        response = self.client.get(
            reverse("division-detail", args=[division.name])
        )
        self.assertTemplateUsed(response, "division_detail.html")

    def test_lowercase_slug_returns_page(self):
        """Using a lowercase slug should still return the page."""
        response = self.client.get("/division/makuuchi")
        self.assertEqual(response.status_code, 200)
