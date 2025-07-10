from django.core.exceptions import ValidationError
from django.test import TestCase

from app.models import Basho, Prediction, Rikishi


class PredictionModelTests(TestCase):
    """Tests for the ``Prediction`` model."""

    def setUp(self):
        self.rikishi = Rikishi.objects.create(id=1, name="A", name_jp="A")
        self.basho = Basho.objects.create(year=2025, month=1)

    def test_prediction_creation(self):
        """Predictions should store the wins value."""
        p = Prediction.objects.create(
            rikishi=self.rikishi,
            basho=self.basho,
            wins=10.5,
        )
        self.assertEqual(p.wins, 10.5)

    def test_wins_validation(self):
        """Wins outside 0-15 should raise a validation error."""
        bad = Prediction(
            rikishi=self.rikishi,
            basho=self.basho,
            wins=16,
        )
        with self.assertRaises(ValidationError):
            bad.full_clean()
        bad.wins = -1
        with self.assertRaises(ValidationError):
            bad.full_clean()
