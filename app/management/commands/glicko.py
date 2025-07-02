from django.core.management.base import BaseCommand

from app.models import Basho, BashoHistory, BashoRating, Bout
from libs.glicko2 import Player


class Command(BaseCommand):
    help = "Calculate Glicko ratings for each rikishi in each basho"

    def handle(self, *args, **options):
        players: dict[int, Player] = {}
        basho_qs = Basho.objects.order_by("year", "month")
        for basho in basho_qs.iterator():
            bouts = Bout.objects.filter(basho=basho)
            results: dict[int, list[tuple[float, float, int]]] = {}
            for bout in bouts.iterator():
                east = players.setdefault(bout.east_id, Player())
                west = players.setdefault(bout.west_id, Player())
                east_out = 1 if bout.winner_id == bout.east_id else 0
                west_out = 1 if bout.winner_id == bout.west_id else 0
                results.setdefault(bout.east_id, []).append(
                    (west.rating, west.rd, east_out)
                )
                results.setdefault(bout.west_id, []).append(
                    (east.rating, east.rd, west_out)
                )

            histories = {
                h.rikishi_id: h
                for h in BashoHistory.objects.filter(basho=basho).iterator()
            }

            for rikishi_id, recs in results.items():
                player = players.setdefault(rikishi_id, Player())
                ratings = [r for r, _, _ in recs]
                rds = [rd for _, rd, _ in recs]
                outcomes = [o for _, _, o in recs]
                player.update_player(ratings, rds, outcomes)

            for rikishi_id in histories:
                if rikishi_id not in results:
                    players.setdefault(rikishi_id, Player()).did_not_compete()

            ratings = []
            for rikishi_id in histories:
                player = players[rikishi_id]
                ratings.append(
                    BashoRating(
                        rikishi_id=rikishi_id,
                        basho=basho,
                        rating=player.rating,
                        rd=player.rd,
                        vol=player.vol,
                    )
                )

            if ratings:
                BashoRating.objects.bulk_create(
                    ratings, batch_size=500, ignore_conflicts=True
                )
