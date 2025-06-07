import builtins
import sys
from unittest import TestCase
from unittest.mock import patch

import manage


class ManageMainTests(TestCase):
    def test_main_executes_commands(self):
        with patch(
            "django.core.management.execute_from_command_line"
        ) as exec_fn:
            with patch.object(sys, "argv", ["manage.py", "check"]):
                manage.main()
            exec_fn.assert_called_once_with(["manage.py", "check"])

    def test_main_import_error(self):
        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "django.core.management":
                raise ImportError("missing")
            return real_import(name, globals, locals, fromlist, level)

        fake_import("math")

        with patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(ImportError):
                manage.main()
