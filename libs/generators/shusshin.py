import json
import os
import random

import pycountry
from rikishi.models import Shusshin

DIRNAME = os.path.dirname(__file__)

JAPANESE_PROB = 0.88

country_codes = [country.alpha_2 for country in pycountry.countries]


def get_pref_probs():
    with open(os.path.join(DIRNAME, "data", "jp_pref_probs.json"), "r") as f:
        try:
            return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise Exception(
                "Failed to load file 'jp_pref_probs.json': " + str(e)
            ) from e


def get_country_probs():
    with open(
        os.path.join(DIRNAME, "data", "foreign_country_probs.json"), "r"
    ) as f:
        try:
            return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise Exception(
                "Failed to load file 'foreign_country_probs.json': " + str(e)
            ) from e


class ShusshinGenerator:
    def __init__(self) -> None:
        self.pref_probs = get_pref_probs()
        self.country_probs = get_country_probs()

    def get_japanese(self):
        population, weights = zip(*self.pref_probs.items(), strict=False)
        prefecture = random.choices(population=population, weights=weights)[0]
        return Shusshin(country="JP", prefecture=prefecture)

    def get_foreigner(self):
        population, weights = zip(*self.country_probs.items(), strict=False)
        country = random.choices(population=population, weights=weights)[0]
        if country == "Other":
            country = random.choice(country_codes)
        return Shusshin(country=country)

    def get(self):
        if random.random() < JAPANESE_PROB:
            return self.get_japanese()
        else:
            return self.get_foreigner()
