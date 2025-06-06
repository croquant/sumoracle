import asyncio
from datetime import datetime

import pycountry
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from app.constants import DIVISION_LEVELS
from app.models.rikishi import Heya, Rikishi, Shusshin
from app.models.division import Division
from app.models.rank import Rank
from libs.sumoapi import SumoApiClient


def clean_shusshin_name(name):
    return (
        name.split(",")[0]
        .split("-")[0]
        .split("(")[0]
        .replace(".", "")
        .replace("Western Samoa", "Samoa")
        .replace("British Commonwealth", "United Kingdom")
        .strip()
    )


def parse_date(date_str, fmt):
    try:
        return datetime.strptime(date_str, fmt)
    except Exception:
        return None


class Command(BaseCommand):
    help = "Populate DB with Rikishi (async version)"

    def log(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))

    def warn(self, msg):
        self.stdout.write(self.style.WARNING(msg))

    def handle(self, *args, **kwargs):
        asyncio.run(self._handle_async())

    async def _handle_async(self):
        api = SumoApiClient()

        await self._populate_divisions()
        self.log("Fetching rikishi from API...")
        rikishi_data = await api.get_all_rikishi()
        await api.aclose()
        self.log(f"Fetched {len(rikishi_data)} rikishi.")

        # Prefetch caches
        existing_rikishi = await sync_to_async(
            lambda: {r.id: r for r in Rikishi.objects.all()}
        )()
        existing_ids = set(existing_rikishi.keys())

        rank_cache = await sync_to_async(
            lambda: {
                tuple([r.title, r.order, r.direction]): r for r in Rank.objects.all()
            }
        )()
        heya_cache = await sync_to_async(
            lambda: {h.name: h for h in Heya.objects.all()}
        )()
        shusshin_cache = await sync_to_async(
            lambda: {(s.name, s.international): s for s in Shusshin.objects.all()}
        )()

        new_rikishi = []
        updated_rikishi = []
        skipped = []

        for data in rikishi_data:
            rikishi_id = data.get("id")
            if not rikishi_id or "shikonaEn" not in data:
                self.warn(f"Skipping rikishi with missing ID or name: {data}")
                skipped.append(data)
                continue

            is_new = rikishi_id not in existing_ids
            rikishi = Rikishi(id=rikishi_id) if is_new else existing_rikishi[rikishi_id]

            # Fields
            rikishi.sumodb_id = data.get("sumodbId")
            rikishi.nsk_id = data.get("nskId") or None
            rikishi.name = data.get("shikonaEn")
            rikishi.name_jp = data.get("shikonaJp") or ""
            rikishi.height = data.get("height")
            rikishi.weight = data.get("weight")
            rikishi.birth_date = parse_date(data.get("birthDate"), "%Y-%m-%dT%H:%M:%SZ")
            rikishi.debut = parse_date(data.get("debut"), "%Y%m")
            rikishi.intai = parse_date(data.get("intai"), "%Y-%m-%dT%H:%M:%SZ")

            # Rank
            rank_str = data.get("currentRank")
            if rank_str:
                parts = rank_str.split(" ")
                key = tuple(parts)
                if key not in rank_cache:
                    if len(parts) == 3:
                        rank = await Rank.objects.aget_or_create(
                            title=parts[0], order=parts[1], direction=parts[2]
                        )
                    else:
                        rank = await Rank.objects.aget_or_create(title=parts[0])
                    rank_cache[key] = rank[0]
                rikishi.rank = rank_cache[key]

            # Heya
            heya_name = data.get("heya")
            if heya_name and heya_name != "-":
                if heya_name not in heya_cache:
                    heya_cache[heya_name], _ = await Heya.objects.aget_or_create(
                        name=heya_name
                    )
                rikishi.heya = heya_cache[heya_name]

            # Shusshin
            shusshin_raw = data.get("shusshin")
            if shusshin_raw and shusshin_raw != "-":
                cleaned = clean_shusshin_name(shusshin_raw)
                try:
                    country = pycountry.countries.search_fuzzy(cleaned)[0]
                    is_japan = country.name == "Japan"
                    key = (cleaned if is_japan else country.name, not is_japan)
                    if key not in shusshin_cache:
                        if is_japan:
                            (
                                shusshin_cache[key],
                                _,
                            ) = await Shusshin.objects.aget_or_create(name=key[0])
                        else:
                            (
                                shusshin_cache[key],
                                _,
                            ) = await Shusshin.objects.aget_or_create(
                                name=key[0], international=True
                            )
                    rikishi.shusshin = shusshin_cache[key]
                except LookupError:
                    self.warn(f"Could not identify country: {cleaned}")

            # Save logic
            if is_new:
                new_rikishi.append(rikishi)
            else:
                updated_rikishi.append(rikishi)

        if skipped:
            self.warn(f"Skipped {len(skipped)} rikishi due to missing data.")

        await self._bulk_save(new_rikishi, updated_rikishi)
        self.log("✅ Rikishi import complete.")

    async def _populate_divisions(self):
        for name, level in DIVISION_LEVELS:
            await Division.objects.aget_or_create(name=name, level=level)

    async def _bulk_save(self, new_rikishi, updated_rikishi):
        if new_rikishi:
            await Rikishi.objects.abulk_create(new_rikishi, batch_size=500)
            self.log(f"Created {len(new_rikishi)} new rikishi.")

        if updated_rikishi:
            await Rikishi.objects.bulk_update(
                updated_rikishi,
                fields=[
                    "sumodb_id",
                    "nsk_id",
                    "name",
                    "name_jp",
                    "height",
                    "weight",
                    "birth_date",
                    "debut",
                    "intai",
                    "rank",
                    "heya",
                    "shusshin",
                ],
                batch_size=500,
            )
            self.log(f"Updated {len(updated_rikishi)} existing rikishi.")
