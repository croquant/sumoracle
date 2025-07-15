import random

from base.models import GameDate
from generators.name import RikishiNameGenerator
from generators.shusshin import ShusshinGenerator
from rikishi.models import Rikishi, RikishiStats

MIN_POTENTIAL = 5
AVG_POTENTIAL = 25
MAX_POTENTIAL = 100


class RikishiGenerator:
    def __init__(self) -> None:
        self.name_generator = RikishiNameGenerator()
        self.shusshin_generator = ShusshinGenerator()

    def get_potential_ability(self):
        potential = random.triangular(
            MIN_POTENTIAL, MAX_POTENTIAL, AVG_POTENTIAL
        )
        return round(potential)

    def get_current_ability(self, potential: int):
        current = random.triangular(
            MIN_POTENTIAL,
            max(potential / 2, MIN_POTENTIAL),
            max(potential / 4, MIN_POTENTIAL),
        )
        return round(current)

    def get_stats(self, rikishi: Rikishi):
        potential = self.get_potential_ability()
        current = self.get_current_ability(potential)
        new_stats = RikishiStats(rikishi=rikishi, potential=potential)
        new_stats.increase_random_stats(current - 5)
        return new_stats

    def get(self):
        name, name_jp = self.name_generator.get()
        shusshin = self.shusshin_generator.get()
        debut = GameDate.objects.current()
        new_rikishi = Rikishi(
            name=name, name_jp=name_jp, shusshin=shusshin, debut=debut
        )
        new_stats = self.get_stats(new_rikishi)
        return (new_rikishi, new_stats)
