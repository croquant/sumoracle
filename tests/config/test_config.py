from importlib import reload

from django.test import SimpleTestCase

import config.asgi
import config.wsgi


class ConfigModuleTests(SimpleTestCase):
    """Validate ASGI and WSGI modules import correctly."""

    def test_asgi_wsgi_import(self):
        """Reloading modules should expose the application objects."""
        reload(config.asgi)
        reload(config.wsgi)
        # Both modules define an ``application`` attribute.
        self.assertIsNotNone(config.asgi.application)
        self.assertIsNotNone(config.wsgi.application)
