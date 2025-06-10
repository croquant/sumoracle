from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from app.admin.division import DivisionAdmin
from app.models.division import Division


class DivisionAdminPermissionTests(SimpleTestCase):
    def setUp(self):
        self.admin = DivisionAdmin(Division, AdminSite())

    def test_no_permissions(self):
        self.assertFalse(self.admin.has_add_permission(None))
        self.assertFalse(self.admin.has_change_permission(None))
        self.assertFalse(self.admin.has_delete_permission(None))
