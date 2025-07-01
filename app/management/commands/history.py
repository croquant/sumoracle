# app/management/commands/history.py

import asyncio
from datetime import datetime

from asgiref.sync import sync_to_async
from django.utils.text import slugify

from app.management.commands import AsyncBaseCommand
from app.models.basho import Basho
from app.models.division import Division
from app.models.history import BashoHistory
from app.models.rank import Rank
from app.models.rikishi import Rikishi
from libs.sumoapi import SumoApiClient


def pick_measurements(measure_map, basho_slug):
    """Return measurements for ``basho_slug`` or fallback to a prior record."""
    record = measure_map.get(basho_slug)
    if record and (record.get("height") or record.get("weight")):
        return record

    keys = [k for k in measure_map if k <= basho_slug]
    for key in sorted(keys, reverse=True):
        rec = measure_map[key]
        if rec.get("height") or rec.get("weight"):
            return rec

    return {}


def pick_shikona(shikona_map, basho_slug):
    """Return shikona for ``basho_slug`` or fallback to the prior record."""
    record = shikona_map.get(basho_slug)
    if record and (record.get("shikonaEn") or record.get("shikonaJp")):
        return record

    keys = [k for k in shikona_map if k <= basho_slug]
    for key in sorted(keys, reverse=True):
        rec = shikona_map[key]
        if rec.get("shikonaEn") or rec.get("shikonaJp"):
            return rec

    return {}


@sync_to_async
def get_rikishis():
    return list(Rikishi.objects.only("id", "name"))


@sync_to_async
def get_existing_basho():
    return {b.slug: b for b in Basho.objects.all()}


@sync_to_async
def get_existing_rank():
    return {r.slug: r for r in Rank.objects.all()}


@sync_to_async
def get_existing_keys():
    return set(BashoHistory.objects.values_list("rikishi_id", "basho__slug"))


@sync_to_async
def get_existing_divisions():
    return {d.name: d for d in Division.objects.all()}


class Command(AsyncBaseCommand):
    help = "Populate rikishi history (async)"

    def log(self, message):
        self.stdout.write(self.style.NOTICE(message))

    async def run(self, *args, **kwargs):
        async with SumoApiClient() as api:
            self.log("Prefetching database objects...")
            rikishis = await get_rikishis()
            existing_basho = await get_existing_basho()
            existing_rank = await get_existing_rank()
            existing_keys = await get_existing_keys()
            existing_divisions = await get_existing_divisions()
            shikona_cache = {}
            measurement_cache = {}

            BATCH_SIZE = 50
            ranking_history_to_create = []

            for i in range(0, len(rikishis), BATCH_SIZE):
                batch = rikishis[i : i + BATCH_SIZE]
                self.log(
                    (
                        f"Processing batch {i // BATCH_SIZE + 1}/"
                        f"{(len(rikishis) + BATCH_SIZE - 1) // BATCH_SIZE}"
                    )
                )

                ranking_histories = await api.get_ranking_history(
                    [r.id for r in batch]
                )

                # Fetch measurement and shikona history if not cached
                shikona_tasks = {
                    r.id: api.get_shikonas(rikishiId=r.id)
                    for r in batch
                    if r.id not in shikona_cache
                }
                measurement_tasks = {
                    r.id: api.get_measurements(rikishiId=r.id)
                    for r in batch
                    if r.id not in measurement_cache
                }
                if shikona_tasks or measurement_tasks:
                    responses = await asyncio.gather(
                        *shikona_tasks.values(), *measurement_tasks.values()
                    )
                    resp_iter = iter(responses)
                    for rikishi_id in shikona_tasks:
                        data = next(resp_iter)
                        shikona_cache[rikishi_id] = {
                            rec.get("bashoId"): rec for rec in data
                        }
                    for rikishi_id in measurement_tasks:
                        data = next(resp_iter)
                        measurement_cache[rikishi_id] = {
                            rec.get("bashoId"): rec for rec in data
                        }

                for rikishi in batch:
                    history = ranking_histories.get(rikishi.id, [])
                    for entry in history:
                        basho_slug = entry.get("bashoId")
                        rank_str = entry.get("rank")
                        if (
                            not basho_slug
                            or not rank_str
                            or (rikishi.id, basho_slug) in existing_keys
                        ):
                            continue

                        if basho_slug not in existing_basho:
                            if int(basho_slug) < 195803:
                                self.log(f"Skipping old basho {basho_slug}")
                                continue
                            basho_data = await api.get_basho_by_id(basho_slug)
                            if not basho_data:
                                self.log(
                                    f"Missing basho {basho_slug}, skipping"
                                )
                                continue
                            basho = await self.create_basho_from_api(basho_data)
                            existing_basho[basho.slug] = basho
                        else:
                            basho = existing_basho[basho_slug]

                        rank = await self.get_or_create_rank(
                            rank_str, existing_rank, existing_divisions
                        )

                        shikona_data = pick_shikona(
                            shikona_cache.get(rikishi.id, {}), basho_slug
                        )
                        measurement_data = pick_measurements(
                            measurement_cache.get(rikishi.id, {}), basho_slug
                        )
                        ranking_history_to_create.append(
                            BashoHistory(
                                rikishi=rikishi,
                                basho=basho,
                                rank=rank,
                                shikona_en=shikona_data.get("shikonaEn", ""),
                                shikona_jp=shikona_data.get("shikonaJp", ""),
                                height=measurement_data.get("height"),
                                weight=measurement_data.get("weight"),
                            )
                        )

                        if len(ranking_history_to_create) >= 1000:
                            await self.bulk_save(ranking_history_to_create)
                            ranking_history_to_create.clear()
                            existing_keys = await get_existing_keys()

            if ranking_history_to_create:
                await self.bulk_save(ranking_history_to_create)
                self.log(
                    f"Inserted final {len(ranking_history_to_create)} records."
                )

            self.log("✅ Ranking history import completed.")

    async def create_basho_from_api(self, basho_data):
        slug = basho_data["date"]
        return await Basho.objects.acreate(
            slug=slug,
            year=int(slug[:4]),
            month=int(slug[-2:]),
            start_date=datetime.strptime(
                basho_data["startDate"], "%Y-%m-%dT%H:%M:%SZ"
            ),
            end_date=datetime.strptime(
                basho_data["endDate"], "%Y-%m-%dT%H:%M:%SZ"
            ),
        )

    async def get_or_create_rank(self, rank_string, rank_cache, division_cache):
        slug = slugify(rank_string)
        if slug in rank_cache:
            return rank_cache[slug]

        parts = rank_string.split(" ")
        division = division_cache.get(parts[0]) or division_cache.get(
            "Makuuchi"
        )

        if len(parts) == 3:
            rank, _ = await Rank.objects.aget_or_create(
                slug=slug,
                title=parts[0],
                order=parts[1],
                direction=parts[2],
                division=division,
            )
        elif len(parts) == 2:
            rank, _ = await Rank.objects.aget_or_create(
                slug=slugify(f"{rank_string} West"),
                title=parts[0],
                order=parts[1],
                direction="West",
                division=division,
            )
        else:
            rank, _ = await Rank.objects.aget_or_create(
                slug=slug, title=parts[0], division=division
            )

        rank_cache[slug] = rank
        return rank

    async def bulk_save(self, objs):
        self.log(f"Inserting {len(objs)} BashoHistory objects...")
        await BashoHistory.objects.abulk_create(objs, batch_size=500)
