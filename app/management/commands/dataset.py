import csv
from datetime import date

from app.management.commands import AsyncBaseCommand
from app.models import BashoHistory, BashoRating, Bout, Heya, Shusshin


class Command(AsyncBaseCommand):
    """Export bout data as a CSV training dataset."""

    help = "Generate dataset for ML training"

    def add_arguments(self, parser):
        parser.add_argument("outfile", help="CSV file path")

    async def run(self, outfile, **options):
        heya_slugs = [
            s
            async for s in Heya.objects.order_by("slug").values_list(
                "slug", flat=True
            )
        ]
        shusshin_slugs = [
            s
            async for s in Shusshin.objects.order_by("slug").values_list(
                "slug", flat=True
            )
        ]
        heya_map = {slug: idx for idx, slug in enumerate(heya_slugs)}
        shusshin_map = {slug: idx for idx, slug in enumerate(shusshin_slugs)}

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
            "same_heya",
            "same_shusshin",
            "east_heya",
            "west_heya",
            "east_shusshin",
            "west_shusshin",
        ]
        headers.append("east_win")
        with open(outfile, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)

            self.stdout.write("Querying basho histories...")
            hist_map: dict[tuple[int, int], BashoHistory] = {}
            async for hist in BashoHistory.objects.select_related(
                "rank__division"
            ).aiterator(chunk_size=1000):
                hist_map[(hist.rikishi_id, hist.basho_id)] = hist

            self.stdout.write("Querying ratings...")
            rating_map: dict[tuple[int, int], BashoRating] = {}
            async for rating in BashoRating.objects.aiterator(chunk_size=1000):
                rating_map[(rating.rikishi_id, rating.basho_id)] = rating

            self.stdout.write("Querying bouts...")
            qs = Bout.objects.select_related(
                "basho",
                "east__heya",
                "west__heya",
                "east__shusshin",
                "west__shusshin",
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

                same_heya = (
                    1
                    if bout.east.heya_id
                    and bout.west.heya_id
                    and bout.east.heya_id == bout.west.heya_id
                    else 0
                )
                same_shusshin = (
                    1
                    if bout.east.shusshin_id
                    and bout.west.shusshin_id
                    and bout.east.shusshin_id == bout.west.shusshin_id
                    else 0
                )

                east_heya = (
                    heya_map.get(bout.east.heya.slug)
                    if bout.east.heya_id
                    else ""
                )
                west_heya = (
                    heya_map.get(bout.west.heya.slug)
                    if bout.west.heya_id
                    else ""
                )
                east_shusshin = (
                    shusshin_map.get(bout.east.shusshin.slug)
                    if bout.east.shusshin_id
                    else ""
                )
                west_shusshin = (
                    shusshin_map.get(bout.west.shusshin.slug)
                    if bout.west.shusshin_id
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
                        same_heya,
                        same_shusshin,
                        east_heya,
                        west_heya,
                        east_shusshin,
                        west_shusshin,
                        1 if bout.winner_id == bout.east_id else 0,
                    ]
                )

                totals[bout.winner_id] = totals.get(bout.winner_id, 0) + 1

                processed += 1
                if processed % step == 0:
                    self.stdout.write(f"Processed {processed} bouts")

        msg = self.style.SUCCESS(f"Dataset saved to {outfile}")
        self.stdout.write(msg)
