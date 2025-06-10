from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from app.admin.division import DivisionAdmin
from app.models.division import Division


class DivisionAdminPermissionTests(SimpleTestCase):
    """Ensure the Division admin is read-only."""

    def setUp(self):
        self.admin = DivisionAdmin(Division, AdminSite())

    def test_no_permissions(self):
        """The admin should disallow modifying Division objects."""
        # Adding new divisions is disabled.
        self.assertFalse(self.admin.has_add_permission(None))
        # Editing existing divisions is disabled.
        self.assertFalse(self.admin.has_change_permission(None))
        # Deleting divisions is disabled.
        self.assertFalse(self.admin.has_delete_permission(None))
