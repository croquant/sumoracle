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
            "east_rd",
            "west_rd",
            "east_vol",
            "west_vol",
            "east_height",
            "west_height",
            "east_weight",
            "west_weight",
            "east_bmi",
            "west_bmi",
            "east_age",
            "west_age",
            "east_experience",
            "west_experience",
            "east_record",
            "west_record",
            "rating_diff",
            "height_diff",
            "weight_diff",
            "age_diff",
            "experience_diff",
            "record_diff",
            "rank_diff",
            "rd_diff",
            "vol_diff",
            "bmi_diff",
            "east_win",
        ]
        with open(outfile, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)

            self.stdout.write("Querying basho histories...")
            histories = [
                h
                async for h in BashoHistory.objects.select_related(
                    "rank__division"
                )
            ]

            self.stdout.write("Querying ratings...")
            ratings = [r async for r in BashoRating.objects.all()]

            hist_map = {(h.rikishi_id, h.basho_id): h for h in histories}
            rating_map = {(r.rikishi_id, r.basho_id): r for r in ratings}

            self.stdout.write("Querying bouts...")
            qs = Bout.objects.select_related(
                "basho",
                "east",
                "west",
                "division",
            ).order_by(
                "basho__year",
                "basho__month",
                "day",
                "-division",
                "match_no",
            )

            processed = 0
            step = 1000
            totals_map: dict[tuple[int, int], dict[int, int]] = {}
            start_map: dict[tuple[int, int, date], dict[int, int]] = {}

            async for bout in qs.aiterator(chunk_size=1000):
                start = bout.basho.start_date or date(
                    bout.basho.year,
                    bout.basho.month,
                    1,
                )
                pair = tuple(sorted((bout.east_id, bout.west_id)))

                totals = totals_map.setdefault(
                    pair,
                    {bout.east_id: 0, bout.west_id: 0},
                )
                start_key = (pair[0], pair[1], start)
                if start_key not in start_map:
                    start_map[start_key] = totals.copy()

                prior_counts = start_map[start_key]

                east_hist = hist_map.get((bout.east_id, bout.basho_id))
                west_hist = hist_map.get((bout.west_id, bout.basho_id))
                east_rating = rating_map.get((bout.east_id, bout.basho_id))
                west_rating = rating_map.get((bout.west_id, bout.basho_id))

                east_record = prior_counts.get(bout.east_id, 0)
                west_record = prior_counts.get(bout.west_id, 0)

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
                east_height = (
                    east_hist and east_hist.height or bout.east.height or ""
                )
                west_height = (
                    west_hist and west_hist.height or bout.west.height or ""
                )
                east_weight = (
                    east_hist and east_hist.weight or bout.east.weight or ""
                )
                west_weight = (
                    west_hist and west_hist.weight or bout.west.weight or ""
                )
                east_bmi = (
                    round(east_weight / ((east_height / 100) ** 2), 2)
                    if east_height and east_weight
                    else ""
                )
                west_bmi = (
                    round(west_weight / ((west_height / 100) ** 2), 2)
                    if west_height and west_weight
                    else ""
                )

                rating_diff = (
                    round(
                        east_rating.previous_rating
                        - west_rating.previous_rating,
                        2,
                    )
                    if east_rating and west_rating
                    else ""
                )
                height_diff = (
                    round(east_height - west_height, 1)
                    if east_height and west_height
                    else ""
                )
                weight_diff = (
                    round(east_weight - west_weight, 1)
                    if east_weight and west_weight
                    else ""
                )
                age_diff = (
                    round(east_age - west_age, 2)
                    if east_age is not None and west_age is not None
                    else ""
                )
                experience_diff = (
                    round(east_experience - west_experience, 2)
                    if east_experience is not None
                    and west_experience is not None
                    else ""
                )
                record_diff = east_record - west_record
                rank_diff = (
                    east_hist.rank.value - west_hist.rank.value
                    if east_hist and west_hist
                    else ""
                )
                east_rd = east_rating.previous_rd if east_rating else ""
                west_rd = west_rating.previous_rd if west_rating else ""
                rd_diff = (
                    round(east_rd - west_rd, 2)
                    if east_rating and west_rating
                    else ""
                )
                east_vol = (
                    round(east_rating.previous_vol, 5) if east_rating else ""
                )
                west_vol = (
                    round(west_rating.previous_vol, 5) if west_rating else ""
                )
                vol_diff = (
                    round(east_vol - west_vol, 5)
                    if east_rating and west_rating
                    else ""
                )
                bmi_diff = (
                    round(east_bmi - west_bmi, 2)
                    if east_bmi and west_bmi
                    else ""
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
                        east_rd,
                        west_rd,
                        east_vol,
                        west_vol,
                        east_height,
                        west_height,
                        east_weight,
                        west_weight,
                        east_bmi,
                        west_bmi,
                        round(east_age, 2) if east_age is not None else "",
                        round(west_age, 2) if west_age is not None else "",
                        round(east_experience, 2)
                        if east_experience is not None
                        else "",
                        round(west_experience, 2)
                        if west_experience is not None
                        else "",
                        east_record,
                        west_record,
                        rating_diff,
                        height_diff,
                        weight_diff,
                        age_diff,
                        experience_diff,
                        record_diff,
                        rank_diff,
                        rd_diff,
                        vol_diff,
                        bmi_diff,
                        1 if bout.winner_id == bout.east_id else 0,
                    ]
                )

                totals[bout.winner_id] = totals.get(bout.winner_id, 0) + 1

                processed += 1
                if processed % step == 0:
                    self.stdout.write(f"Processed {processed} bouts")

        msg = self.style.SUCCESS(f"Dataset saved to {outfile}")
        self.stdout.write(msg)
