import unittest
from unittest.mock import patch

from .shusshin import ShusshinGenerator, get_country_probs, get_pref_probs


class TestShusshinGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ShusshinGenerator()

    def test_get_japanese(self):
        # Mock the random.choices function to always return "Tokyo"
        with patch("random.choices", return_value=["Tokyo"]):
            shusshin = self.generator.get_japanese()
            self.assertEqual(shusshin.country, "JP")
            self.assertEqual(shusshin.prefecture, "Tokyo")

    def test_get_japanese_different_prefecture(self):
        # Mock the random.choices function to return "Tottori"
        with patch("random.choices", return_value=["Tottori"]):
            shusshin = self.generator.get_japanese()
            self.assertEqual(shusshin.country, "JP")
            self.assertEqual(shusshin.prefecture, "Tottori")

    def test_get_foreigner(self):
        # Mock the random.choices function to always return "MN (Mongolia)"
        with patch("random.choices", return_value=["MN"]):
            shusshin = self.generator.get_foreigner()
            self.assertEqual(shusshin.country, "MN")
            self.assertIsNone(shusshin.prefecture)

    def test_get_other_foreigner(self):
        # Mock the random.choices function to always return "Other"
        with (
            patch("random.choices", return_value=["Other"]),
            patch("random.choice", return_value="BE"),
        ):
            shusshin = self.generator.get_foreigner()
            self.assertEqual(shusshin.country, "BE")
            self.assertIsNone(shusshin.prefecture)

    def test_get(self):
        # It should return a Japanese Shusshin
        with (
            patch("random.random", return_value=0.1),
        ):
            shusshin = self.generator.get()
            self.assertEqual(shusshin.country, "JP")
            self.assertIsNotNone(shusshin.prefecture)

        # It should return a foreign Shusshin
        with (
            patch("random.random", return_value=0.9),
        ):
            shusshin = self.generator.get()
            self.assertNotEqual(shusshin.country, "JP")
            self.assertIsNone(shusshin.prefecture)

    def test_prob(self):
        # It should generate a Japanese around 88% of the time

        # Generate 10000 shusshin
        num_shusshin = 10000
        num_japanese = 0
        for _ in range(num_shusshin):
            generated_shusshin = self.generator.get()
            if generated_shusshin.country == "JP":
                num_japanese += 1

        self.assertAlmostEqual(num_japanese, num_shusshin * 0.88, delta=100)

    def test_get_pref_probs(self):
        # Ensure that the probabilities sum up to 1
        pref_probs = get_pref_probs()
        total_prob = sum(pref_probs.values())
        self.assertAlmostEqual(total_prob, 1.0, places=6)

    def test_get_country_probs(self):
        # Ensure that the probabilities sum up to 1
        country_probs = get_country_probs()
        total_prob = sum(country_probs.values())
        self.assertAlmostEqual(total_prob, 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
