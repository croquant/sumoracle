from django.test import TestCase


class ApiRouteTests(TestCase):
    """Verify the Ninja API router is mounted."""

    def test_docs_available_at_root(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        # docs should still be accessible via /api/docs
        self.assertEqual(self.client.get("/api/docs").status_code, 200)
