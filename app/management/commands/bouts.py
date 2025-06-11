from app.management.commands import AsyncBaseCommand
from app.models import Basho, Bout, Division, Rikishi
from libs.sumoapi import SumoApiClient


class Command(AsyncBaseCommand):
    help = "Import bouts for a rikishi"

    def add_arguments(self, parser):
        parser.add_argument("rikishi_id", nargs="?", type=int)
        parser.add_argument("--basho", dest="basho_id")

    async def run(self, rikishi_id=None, basho_id=None, **options):
        async with SumoApiClient() as api:
            rikishi_ids = (
                [rikishi_id]
                if rikishi_id
                else list(await Rikishi.objects.values_list("id", flat=True))
            )
            params = {"bashoId": basho_id} if basho_id else {}
            total = 0
            for rid in rikishi_ids:
                data = await api.get_rikishi_matches(rid, **params)
                records = data.get("records", [])
                total += len(records)
                for entry in records:
                    basho_slug = entry.get("bashoId")
                    basho, _ = await Basho.objects.aget_or_create(
                        slug=basho_slug,
                        defaults={
                            "year": int(basho_slug[:4]),
                            "month": int(basho_slug[-2:]),
                        },
                    )
                    division = await Division.objects.aget(
                        name=entry["division"]
                    )
                    east = await Rikishi.objects.aget(id=entry["eastId"])
                    west = await Rikishi.objects.aget(id=entry["westId"])
                    winner = await Rikishi.objects.aget(id=entry["winnerId"])
                    await Bout.objects.aupdate_or_create(
                        basho=basho,
                        day=entry["day"],
                        match_no=entry["matchNo"],
                        east=east,
                        west=west,
                        defaults={
                            "division": division,
                            "east_shikona": entry["eastShikona"],
                            "west_shikona": entry["westShikona"],
                            "kimarite": entry["kimarite"],
                            "winner": winner,
                        },
                    )
            self.stdout.write(self.style.SUCCESS(f"Imported {total} bouts"))
