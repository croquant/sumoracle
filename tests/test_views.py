from django.test import TestCase
from django.urls import reverse

from app.models.division import Division


class DivisionListViewTests(TestCase):
    def test_view_status_code(self):
        response = self.client.get(reverse("division-list"))
        self.assertEqual(response.status_code, 200)

    def test_view_template(self):
        response = self.client.get(reverse("division-list"))
        self.assertTemplateUsed(response, "division_list.html")

    def test_view_lists_all_divisions(self):
        response = self.client.get(reverse("division-list"))
        self.assertEqual(
            response.context["object_list"].count(),
            Division.objects.count(),
        )

