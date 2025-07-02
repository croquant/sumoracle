import math

from django.test import SimpleTestCase

from libs.glicko2 import GLICKO2_SCALER, Player


class PlayerTests(SimpleTestCase):
    """Unit tests for :class:`Player` rating utilities."""

    def test_property_roundtrip(self):
        """Setting rating or RD should be reversible via the properties."""
        p = Player()
        p.rating = 1600
        p.rd = 100
        self.assertEqual(p.rating, 1600)
        self.assertEqual(p.rd, 100)

    def test_g_and_e_functions(self):
        """The helper math functions should match the official example."""
        p = Player(rating=1500, rd=200, vol=0.06, tau=0.5)
        rd1 = 30 / GLICKO2_SCALER
        rd2 = 100 / GLICKO2_SCALER
        rd3 = 300 / GLICKO2_SCALER
        self.assertAlmostEqual(p._g(rd1), 0.9955, places=4)
        self.assertAlmostEqual(p._g(rd2), 0.9531, places=4)
        self.assertAlmostEqual(p._g(rd3), 0.7242, places=4)
        self.assertAlmostEqual(p._e(-0.5756, rd1), 0.639, places=3)
        self.assertAlmostEqual(p._e(0.2878, rd2), 0.432, places=3)
        self.assertAlmostEqual(p._e(1.1513, rd3), 0.303, places=3)

    def test_update_player_example(self):
        """Updating a player should reproduce the documented results."""
        p = Player(rating=1500, rd=200, vol=0.06, tau=0.5)
        ratings = [1400, 1550, 1700]
        rds = [30, 100, 300]
        outcomes = [1, 0, 0]
        p.update_player(ratings, rds, outcomes)
        self.assertAlmostEqual(p.rating, 1464.05, places=2)
        self.assertAlmostEqual(p.rd, 151.52, places=2)
        self.assertAlmostEqual(p.vol, 0.05999, places=5)

    def test_did_not_compete(self):
        """Step 6 should increase RD based on volatility."""
        p = Player(rating=1500, rd=50, vol=0.06)
        current_rd = p.rd
        p.did_not_compete()
        expected = math.sqrt((current_rd / GLICKO2_SCALER) ** 2 + p.vol**2)
        expected *= GLICKO2_SCALER
        self.assertAlmostEqual(p.rd, expected)
