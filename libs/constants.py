from enum import Enum

from django.db import models


class DivisionEnum(Enum):
    MAKUUCHI = ("Makuuchi", "M", 1)
    JURYO = ("Juryo", "J", 2)
    MAKUSHITA = ("Makushita", "Ms", 3)
    SANDANME = ("Sandanme", "Sd", 4)
    JONIDAN = ("Jonidan", "Jd", 5)
    JONOKUCHI = ("Jonokuchi", "Jk", 6)
    MAEZUMO = ("Mae-zumo", "Mz", 7)
    BANZUKE_GAI = ("Banzuke-gai", "Bg", 8)

    def __init__(self, label: str, short: str, level: int) -> None:
        self.label = label
        self.short = short
        self.level = level


DIVISION_LEVELS = [(d.label, d.level) for d in DivisionEnum]


class RankName(models.TextChoices):
    YOKOZUNA = "Yokozuna", "Yokozuna"
    OZEKI = "Ozeki", "Ozeki"
    SEKIWAKE = "Sekiwake", "Sekiwake"
    KOMUSUBI = "Komusubi", "Komusubi"
    MAEGASHIRA = "Maegashira", "Maegashira"
    JURYO = "Juryo", "Juryo"
    MAKUSHITA = "Makushita", "Makushita"
    SANDANME = "Sandanme", "Sandanme"
    JONIDAN = "Jonidan", "Jonidan"
    JONOKUCHI = "Jonokuchi", "Jonokuchi"
    MAEZUMO = "Mae-zumo", "Mae-zumo"
    BANZUKE_GAI = "Banzuke-gai", "Banzuke-gai"


RANK_NAMES_SHORT = {
    "Yokozuna": "Y",
    "Ozeki": "O",
    "Sekiwake": "S",
    "Komusubi": "K",
    "Maegashira": "M",
    "Juryo": "J",
    "Makushita": "Ms",
    "Sandanme": "Sd",
    "Jonidan": "Jd",
    "Jonokuchi": "Jk",
    "Mae-zumo": "Mz",
    "Banzuke-gai": "Bg",
}

RANKING_LEVELS = {
    "Yokozuna": 1,
    "Ozeki": 2,
    "Sekiwake": 3,
    "Komusubi": 4,
    "Maegashira": 5,
    "Juryo": 6,
    "Makushita": 7,
    "Sandanme": 8,
    "Jonidan": 9,
    "Jonokuchi": 10,
    "Mae-zumo": 11,
    "Banzuke-gai": 12,
}


class Direction(models.TextChoices):
    EAST = "East", "East"
    WEST = "West", "West"


DIRECTION_NAMES_SHORT = {"East": "E", "West": "W"}

BASHO_NAMES = {
    1: "Hatsu",
    3: "Haru",
    5: "Natsu",
    7: "Nagoya",
    9: "Aki",
    11: "Kyushu",
}


# Glicko2 constants
DEFAULT_RATING = 1500
DEFAULT_RD = 350
DEFAULT_VOLATILITY = 0.11
GLICKO2_SCALER = 173.7178
TAU = 0.9
CONVERGENCE_TOLERANCE = 0.000001

# Rolling statistics
RECENT_BOUT_WINDOW = 15
