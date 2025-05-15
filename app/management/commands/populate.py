from datetime import datetime

import pycountry
from django.core.management.base import BaseCommand

from app.constants import DIVISION_LEVELS
from app.models.rikishi import Division, Heya, Rank, Rikishi, Shusshin
from libs.sumoapi import SumoApiClient

sumoapi = SumoApiClient()


def populate_divisions():
    for division in DIVISION_LEVELS:
        Division.objects.get_or_create(name=division[0], level=division[1])


class Command(BaseCommand):
    args = ""
    help = "Populate DB with Rikishi"

    def handle(self, *args, **options):
        populate_divisions()
        rikishis = sumoapi.get_all_rikishi()

        for r in rikishis:
            print(r)
            if Rikishi.objects.filter(id=r["id"]).exists():
                rikishi = Rikishi.objects.get(id=r["id"])
            else:
                rikishi = Rikishi(id=r["id"])

            if "sumodbId" in r:
                rikishi.sumodb_id = r["sumodbId"]

            if "nskId" in r and r["nskId"] != 0:
                rikishi.nsk_id = r["nskId"]

            if "currentRank" in r:
                rank = None
                rank_parts = r["currentRank"].split(" ")
                if len(rank_parts) > 1:
                    rank = Rank.objects.get_or_create(
                        title=rank_parts[0],
                        order=rank_parts[1],
                        direction=rank_parts[2],
                    )[0]
                else:
                    rank = Rank.objects.get_or_create(title=rank_parts[0])[0]
                rikishi.rank = rank

            if "heya" in r and r["heya"] != "-":
                heya = Heya.objects.get_or_create(name=r["heya"])[0]
                rikishi.heya = heya

            if "shusshin" in r and r["shusshin"] != "-":
                search = (
                    r["shusshin"]
                    .split(",")[0]
                    .split("-")[0]
                    .split("(")[0]
                    .replace(".", "")
                    .replace("Western Samoa", "Samoa")
                    .replace("British Commonwealth", "United Kingdom")
                )
                country = pycountry.countries.search_fuzzy(search)[0]
                shusshin = None
                if country.name == "Japan":
                    shusshin = Shusshin.objects.get_or_create(name=search)[0]
                else:
                    shusshin = Shusshin.objects.get_or_create(
                        name=country.name, international=True
                    )[0]
                rikishi.shusshin = shusshin

            if "shikonaEn" not in r:
                print(f"Skipping {r['id']}")
                continue
            rikishi.name = r["shikonaEn"]

            if "shikonaJp" in r:
                rikishi.name_jp = r["shikonaJp"]

            if "height" in r:
                rikishi.height = r["height"]

            if "weight" in r:
                rikishi.weight = r["weight"]

            if "birthDate" in r:
                rikishi.birth_date = datetime.strptime(
                    r["birthDate"], "%Y-%m-%dT%H:%M:%SZ"
                )

            if "debut" in r:
                rikishi.debut = datetime.strptime(r["debut"], "%Y%m")

            if "intai" in r:
                rikishi.intai = datetime.strptime(r["intai"], "%Y-%m-%dT%H:%M:%SZ")

            rikishi.save()
