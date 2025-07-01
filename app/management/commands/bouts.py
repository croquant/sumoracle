import asyncio

from asgiref.sync import sync_to_async

from app.management.commands import AsyncBaseCommand
from app.models import Basho, Bout, Division, Rikishi
from libs.sumoapi import SumoApiClient


@sync_to_async
def get_rikishi_map():
    """Return all ``Rikishi`` keyed by ID."""

    return {r.id: r for r in Rikishi.objects.only("id")}


@sync_to_async
def get_division_map():
    """Return all ``Division`` objects keyed by name."""

    return {d.name: d for d in Division.objects.all()}


class Command(AsyncBaseCommand):
    help = "Import bouts for a rikishi"

    def add_arguments(self, parser):
        parser.add_argument("rikishi_id", nargs="?", type=int)
        parser.add_argument("--basho", dest="basho_id")

    async def rikishi_id_iter(self, rikishi_id=None):
        """Yield one or more rikishi IDs."""

        if rikishi_id:
            yield rikishi_id
            return

        qs = Rikishi.objects.values_list("id", flat=True)
        async for rid in qs.aiterator():
            yield rid

    async def _process_rikishi(self, api, rikishi_id, params, sem, rmap, dmap):
        async with sem:
            data = await api.get_rikishi_matches(rikishi_id, **params)

        records = data.get("records") or []
        bouts = []
        for entry in records:
            basho_slug = entry.get("bashoId")
            basho, _ = await Basho.objects.aget_or_create(
                slug=basho_slug,
                defaults={
                    "year": int(basho_slug[:4]),
                    "month": int(basho_slug[-2:]),
                },
            )
            bouts.append(
                Bout(
                    basho=basho,
                    division=dmap.get(entry["division"]),
                    day=entry["day"],
                    match_no=entry["matchNo"],
                    east=rmap.get(entry["eastId"]),
                    west=rmap.get(entry["westId"]),
                    east_shikona=entry["eastShikona"],
                    west_shikona=entry["westShikona"],
                    kimarite=entry["kimarite"],
                    winner=rmap.get(entry["winnerId"]),
                )
            )
        return bouts

    async def run(self, rikishi_id=None, basho_id=None, **options):
        async with SumoApiClient() as api:
            params = {"bashoId": basho_id} if basho_id else {}
            rikishi_map, division_map = await asyncio.gather(
                get_rikishi_map(), get_division_map()
            )
            semaphore = asyncio.Semaphore(10)
            tasks = []
            async for rid in self.rikishi_id_iter(rikishi_id):
                task = asyncio.create_task(
                    self._process_rikishi(
                        api,
                        rid,
                        params,
                        semaphore,
                        rikishi_map,
                        division_map,
                    )
                )
                tasks.append(task)
            results = await asyncio.gather(*tasks)
            bouts = [b for sub in results for b in sub]
            if bouts:
                await Bout.objects.abulk_create(
                    bouts, batch_size=500, ignore_conflicts=True
                )
            msg = self.style.SUCCESS(f"Imported {len(bouts)} bouts")
            self.stdout.write(msg)
