import csv
from datetime import date

from app.management.commands import AsyncBaseCommand
from app.models import BashoHistory, BashoRating, Bout


class Command(AsyncBaseCommand):
    """Export bout data as a CSV training dataset."""

    help = "Generate dataset for ML training"

    def add_arguments(self, parser):
        parser.add_argument("outfile", help="CSV file path")

    async def run(self, outfile, **options):
        headers = [
            "year",
            "month",
            "division",
            "day",
            "match_no",
            "east_id",
            "west_id",
            "east_rank",
            "west_rank",
            "east_rating",
            "west_rating",
            "east_height",
            "west_height",
            "east_weight",
            "west_weight",
            "east_age",
            "west_age",
            "east_experience",
            "west_experience",
            "east_win",
        ]
        with open(outfile, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            qs = Bout.objects.select_related(
                "basho",
                "east",
                "west",
                "division",
            ).order_by(
                "basho__year", "basho__month", "day", "-division", "match_no"
            )
            async for bout in qs.aiterator():
                east_hist = (
                    await BashoHistory.objects.filter(
                        rikishi_id=bout.east_id,
                        basho=bout.basho,
                    )
                    .select_related("rank__division")
                    .afirst()
                )
                west_hist = (
                    await BashoHistory.objects.filter(
                        rikishi_id=bout.west_id,
                        basho=bout.basho,
                    )
                    .select_related("rank__division")
                    .afirst()
                )
                east_rating = await BashoRating.objects.filter(
                    rikishi_id=bout.east_id,
                    basho=bout.basho,
                ).afirst()
                west_rating = await BashoRating.objects.filter(
                    rikishi_id=bout.west_id,
                    basho=bout.basho,
                ).afirst()
                start = bout.basho.start_date or date(
                    bout.basho.year,
                    bout.basho.month,
                    1,
                )
                east_age = (
                    (start - bout.east.birth_date).days / 365.25
                    if bout.east.birth_date
                    else None
                )
                west_age = (
                    (start - bout.west.birth_date).days / 365.25
                    if bout.west.birth_date
                    else None
                )
                east_experience = (
                    (start - bout.east.debut).days / 365.25
                    if bout.east.debut
                    else None
                )
                west_experience = (
                    (start - bout.west.debut).days / 365.25
                    if bout.west.debut
                    else None
                )
                writer.writerow(
                    [
                        bout.basho.year,
                        bout.basho.month,
                        bout.division.level,
                        bout.day,
                        bout.match_no,
                        bout.east_id,
                        bout.west_id,
                        east_hist.rank.value if east_hist else "",
                        west_hist.rank.value if west_hist else "",
                        east_rating.previous_rating if east_rating else "",
                        west_rating.previous_rating if west_rating else "",
                        (east_hist.height or bout.east.height or ""),
                        (west_hist.height or bout.west.height or ""),
                        (east_hist.weight or bout.east.weight or ""),
                        (west_hist.weight or bout.west.weight or ""),
                        round(east_age, 2) if east_age is not None else "",
                        round(west_age, 2) if west_age is not None else "",
                        round(east_experience, 2)
                        if east_experience is not None
                        else "",
                        round(west_experience, 2)
                        if west_experience is not None
                        else "",
                        1 if bout.winner_id == bout.east_id else 0,
                    ]
                )
        msg = self.style.SUCCESS(f"Dataset saved to {outfile}")
        self.stdout.write(msg)
