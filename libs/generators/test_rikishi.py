import unittest
from unittest.mock import patch

from base.models import GameDate
from generators.rikishi_generator import (
    AVG_POTENTIAL,
    MAX_POTENTIAL,
    MIN_POTENTIAL,
    RikishiGenerator,
)
from rikishi.models import Rikishi, RikishiStats, Shusshin


class TestRikishiGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = RikishiGenerator()

    @patch("generators.rikishi.RikishiNameGenerator.get")
    @patch("generators.rikishi.ShusshinGenerator.get")
    @patch("base.models.GameDate.objects.current")
    def test_get(self, mock_current, mock_shusshin_get, mock_name_get):
        mock_name_get.return_value = ("Test Name", "テストネーム")
        mock_shusshin_get.return_value = Shusshin(
            country="JP", prefecture="Tokyo"
        )
        mock_current.return_value = GameDate(2023, 1, 1)

        rikishi, stats = self.generator.get()

        self.assertEqual(rikishi.name, "Test Name")
        self.assertEqual(rikishi.name_jp, "テストネーム")
        self.assertIsInstance(rikishi.shusshin, Shusshin)
        self.assertEqual(rikishi.shusshin.country, "JP")
        self.assertEqual(rikishi.shusshin.prefecture, "Tokyo")
        self.assertEqual(rikishi.debut, GameDate(2023, 1, 1))
        self.assertIsInstance(stats, RikishiStats)
        self.assertEqual(stats.rikishi, rikishi)
        self.assertIsNotNone(rikishi.id)
        self.assertIsNotNone(stats.rikishi)
        self.assertEqual(stats.rikishi, rikishi)
        self.assertGreaterEqual(stats.potential, MIN_POTENTIAL)
        self.assertLessEqual(stats.potential, MAX_POTENTIAL)
        self.assertGreaterEqual(stats.current, MIN_POTENTIAL)
        self.assertLessEqual(stats.current, stats.potential)

    def test_get_potential_ability(self):
        for _ in range(100):
            potential = self.generator.get_potential_ability()
            self.assertGreaterEqual(potential, MIN_POTENTIAL)
            self.assertLessEqual(potential, MAX_POTENTIAL)

        with patch("random.triangular", return_value=MIN_POTENTIAL):
            self.assertEqual(
                self.generator.get_potential_ability(), MIN_POTENTIAL
            )
        with patch("random.triangular", return_value=MAX_POTENTIAL):
            self.assertEqual(
                self.generator.get_potential_ability(), MAX_POTENTIAL
            )

    def test_get_current_ability(self):
        test_cases = [MIN_POTENTIAL, AVG_POTENTIAL, MAX_POTENTIAL]
        for potential in test_cases:
            current = self.generator.get_current_ability(potential)
            self.assertGreaterEqual(current, MIN_POTENTIAL)
            self.assertLessEqual(current, potential)

    @patch.object(
        RikishiGenerator, "get_potential_ability", return_value=AVG_POTENTIAL
    )
    @patch.object(
        RikishiGenerator, "get_current_ability", return_value=MIN_POTENTIAL
    )
    def test_get_stats(
        self, mock_get_current_ability, mock_get_potential_ability
    ):
        rikishi = Rikishi(
            name="Test",
            name_jp="テスト",
            shusshin=Shusshin(country="JP", prefecture="Tokyo"),
            debut=GameDate(2023, 1, 1),
        )
        stats = self.generator.get_stats(rikishi)

        self.assertEqual(stats.potential, AVG_POTENTIAL)
        self.assertEqual(stats.current, MIN_POTENTIAL)
        self.assertEqual(stats.rikishi, rikishi)

        # Verify that mocked methods were called
        mock_get_potential_ability.assert_called_once()
        mock_get_current_ability.assert_called_once_with(AVG_POTENTIAL)

        # Test more attributes
        self.assertIsNotNone(stats.rikishi)
        self.assertEqual(stats.rikishi, rikishi)
        self.assertGreaterEqual(stats.strength, 1)
        self.assertLessEqual(stats.strength, 20)
        self.assertGreaterEqual(stats.technique, 1)
        self.assertLessEqual(stats.technique, 20)
        self.assertGreaterEqual(stats.balance, 1)
        self.assertLessEqual(stats.balance, 20)
        self.assertGreaterEqual(stats.endurance, 1)
        self.assertLessEqual(stats.endurance, 20)
        self.assertGreaterEqual(stats.mental, 1)
        self.assertLessEqual(stats.mental, 20)
        # Add more assertions for other attributes as needed


if __name__ == "__main__":
    unittest.main()
