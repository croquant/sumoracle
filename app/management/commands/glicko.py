from django.core.management.base import BaseCommand

from app.models import Basho, BashoHistory, BashoRating, Bout
from libs.glicko2 import Player


class Command(BaseCommand):
    help = "Calculate Glicko ratings for each rikishi in each basho"

    def handle(self, *args, **options):
        # Clear existing ratings
        self.stdout.write("Clearing existing ratings...")
        BashoRating.objects.all().delete()

        self.stdout.write("Calculating Glicko ratings...")
        players: dict[int, Player] = {}
        basho_qs = Basho.objects.order_by("year", "month")
        for basho in basho_qs.iterator():
            bouts = Bout.objects.filter(basho=basho).order_by("day", "match_no")
            if not bouts.exists():
                self.stdout.write(
                    f"No bouts found for {basho.slug}. Skipping..."
                )
                continue

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

            ratings = []
            for rikishi_id in histories:
                player = players.setdefault(rikishi_id, Player())
                before_rating = player.rating
                before_rd = player.rd
                before_vol = player.vol
                recs = results.get(rikishi_id)
                if recs:
                    r_list = [r for r, _, _ in recs]
                    rd_list = [rd for _, rd, _ in recs]
                    o_list = [o for _, _, o in recs]
                    player.update_player(r_list, rd_list, o_list)
                else:
                    player.did_not_compete()
                ratings.append(
                    BashoRating(
                        rikishi_id=rikishi_id,
                        basho=basho,
                        previous_rating=before_rating,
                        previous_rd=before_rd,
                        previous_vol=before_vol,
                        rating=player.rating,
                        rd=player.rd,
                        vol=player.vol,
                    )
                )

            if ratings:
                BashoRating.objects.bulk_create(
                    ratings, batch_size=500, ignore_conflicts=True
                )
