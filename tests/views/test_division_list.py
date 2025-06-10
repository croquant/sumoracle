from django.test import TestCase
from django.urls import reverse

from app.models.division import Division


class DivisionListViewTests(TestCase):
    """Verify behaviour of the division list view."""

    def test_view_status_code(self):
        """The list view should return HTTP 200."""
        response = self.client.get(reverse("division-list"))
        self.assertEqual(response.status_code, 200)  # Success

    def test_view_template(self):
        """The expected template should be used."""
        response = self.client.get(reverse("division-list"))
        self.assertTemplateUsed(response, "division_list.html")

    def test_view_lists_all_divisions(self):
        """All divisions in the database should be in the context."""
        response = self.client.get(reverse("division-list"))
        self.assertEqual(
            response.context["object_list"].count(),
            Division.objects.count(),
        )  # Queryset lengths match
