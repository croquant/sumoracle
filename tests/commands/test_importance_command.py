import asyncio
import csv
import io
import tempfile

from django.core.management import call_command
from django.test import SimpleTestCase


class ImportanceCommandTests(SimpleTestCase):
    def test_feature_output(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            writer = csv.writer(tmp)
            writer.writerow(["a", "b", "east_win"])
            writer.writerow([1, 2, 1])
            writer.writerow([2, 1, 0])
            path = tmp.name
        out = io.StringIO()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            call_command("importance", path, stdout=out)
        finally:
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop.close()
        lines = [l for l in out.getvalue().splitlines() if l]
        self.assertGreaterEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("a:"))
        self.assertIn("Training complete", lines[-1])
