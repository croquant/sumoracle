from django.test import TestCase
from django.urls import reverse

from app.models.basho import Basho


class BashoListViewTests(TestCase):
    """Verify behaviour of the basho list view."""

    def setUp(self):
        Basho.objects.create(year=2025, month=1)
        Basho.objects.create(year=2025, month=3)

    def test_view_status_code(self):
        response = self.client.get(reverse("basho-list"))
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        response = self.client.get(reverse("basho-list"))
        self.assertTemplateUsed(response, "basho_list.html")

    def test_view_lists_all_basho(self):
        response = self.client.get(reverse("basho-list"))
        self.assertEqual(
            response.context["object_list"].count(),
            Basho.objects.count(),
        )

    def test_names_link_to_detail(self):
        response = self.client.get(reverse("basho-list"))
        for basho in Basho.objects.all():
            detail_url = reverse("basho-detail", args=[basho.slug])
            self.assertContains(response, f'href="{detail_url}"')
