from django.test import TestCase
from django.urls import reverse

from app.models.division import Division


class DivisionModelTests(TestCase):
    """Tests for :class:`Division` model helper methods."""

    def test_str_returns_name(self):
        """``__str__`` should return the division name."""
        division = Division.objects.get(name="Makuuchi")
        self.assertEqual(str(division), "Makuuchi")  # Uses ``name`` field

    def test_get_absolute_url(self):
        """``get_absolute_url`` returns the detail view URL."""
        division = Division.objects.get(name="Makuuchi")
        expected_url = reverse("division-detail", args=["makuuchi"])
        self.assertEqual(
            division.get_absolute_url(),
            expected_url,
        )  # Named route matches slug
