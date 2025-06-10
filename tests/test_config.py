from importlib import reload

from django.test import SimpleTestCase

import config.asgi
import config.wsgi


class ConfigModuleTests(SimpleTestCase):
    def test_asgi_wsgi_import(self):
        reload(config.asgi)
        reload(config.wsgi)
        self.assertIsNotNone(config.asgi.application)
        self.assertIsNotNone(config.wsgi.application)
