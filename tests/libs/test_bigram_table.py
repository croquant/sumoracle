import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from libs.generators.bigram import make_name_char_bigram_table


class BigramTableTests(SimpleTestCase):
    """Tests for the ``make_name_char_bigram_table`` helper."""

    def test_table_created(self):
        """The function should build and persist a bigram table."""
        with tempfile.TemporaryDirectory() as tmp:
            corpus = Path(tmp) / "shikona_corpus.txt"
            corpus.write_text("aa\nab\n", encoding="utf-8")
            out = Path(tmp) / "name_char_bigram_table.json"
            table = make_name_char_bigram_table(corpus, out)
            expected = {
                "^": {"a": 1.0},
                "a": {"$": 1 / 3, "a": 1 / 3, "b": 1 / 3},
                "b": {"$": 1.0},
            }
            self.assertEqual(table, expected)
            self.assertEqual(
                json.loads(out.read_text(encoding="utf-8")), expected
            )
