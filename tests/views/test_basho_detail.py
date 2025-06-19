from django.test import TestCase
from django.urls import reverse

from app.models.basho import Basho


class BashoDetailViewTests(TestCase):
    """Verify behaviour of the basho detail view."""

    def setUp(self):
        self.basho = Basho.objects.create(year=2025, month=1)

    def test_view_status_code(self):
        response = self.client.get(
            reverse("basho-detail", args=[self.basho.slug])
        )
        self.assertEqual(response.status_code, 200)

    def test_view_template_and_content(self):
        response = self.client.get(
            reverse("basho-detail", args=[self.basho.slug])
        )
        self.assertTemplateUsed(response, "basho_detail.html")
        self.assertContains(response, self.basho.slug)
        self.assertContains(response, str(self.basho.year))
        self.assertContains(response, str(self.basho.month))
