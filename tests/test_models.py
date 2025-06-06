from django.test import TestCase
from django.urls import reverse

from app.models.division import Division


class DivisionModelTests(TestCase):
    def test_str_returns_name(self):
        division = Division.objects.get(name="Makuuchi")
        self.assertEqual(str(division), "Makuuchi")

    def test_get_absolute_url(self):
        division = Division.objects.get(name="Makuuchi")
        expected_url = reverse("division-detail", args=["makuuchi"])
        self.assertEqual(division.get_absolute_url(), expected_url)
