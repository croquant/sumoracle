import csv
from collections import defaultdict
from datetime import date

from app.management.commands import AsyncBaseCommand
from app.models import BashoHistory, BashoRating, Bout


def recent_form(bouts):
    """Return weighted win percentages keyed by ``(rikishi_id, basho_slug)``."""

    results = defaultdict(lambda: [0, 0])
    basho_map = {}
    for bout in bouts:
        basho_map[bout.basho_id] = bout.basho
        results[(bout.east_id, bout.basho_id)][1] += 1
        results[(bout.west_id, bout.basho_id)][1] += 1
        if bout.winner_id == bout.east_id:
            results[(bout.east_id, bout.basho_id)][0] += 1
        else:
            results[(bout.west_id, bout.basho_id)][0] += 1

    history = defaultdict(list)
    for (rid, bid), (wins, total) in results.items():
        pct = wins / total if total else 0
        history[rid].append((basho_map[bid], pct))

    for recs in history.values():
        recs.sort(key=lambda r: (r[0].year, r[0].month))

    weights = [1.0, 0.5, 0.25]
    form = {}
    for rid, recs in history.items():
        for idx, (basho, _) in enumerate(recs):
            prior = [r[1] for r in recs[max(0, idx - 3) : idx]][::-1]
            if not prior:
                continue
            value = 0.0
            weight_total = 0.0
            for w, pct in zip(weights, prior):  # noqa: B905
                value += w * pct
                weight_total += w
            form[(rid, basho.slug)] = round(value / weight_total * 100, 2)
    return form


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
            "east_form",
            "west_form",
            "east_win",
        ]
        with open(outfile, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
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

            bouts = [bout async for bout in qs.aiterator()]
            total = len(bouts)
            step = max(total // 10, 1)
            processed = 0
            basho_ids = {b.basho_id for b in bouts}
            rikishi_ids = {b.east_id for b in bouts} | {
                b.west_id for b in bouts
            }

            self.stdout.write("Querying basho histories...")
            hist_qs = BashoHistory.objects.filter(
                basho_id__in=basho_ids,
                rikishi_id__in=rikishi_ids,
            ).select_related("rank__division")
            histories = [h async for h in hist_qs]

            self.stdout.write("Querying ratings...")
            rating_qs = BashoRating.objects.filter(
                basho_id__in=basho_ids,
                rikishi_id__in=rikishi_ids,
            )
            ratings = [r async for r in rating_qs]

            records: dict[tuple[int, int], dict[date, dict[int, int]]] = {}
            for b in bouts:
                start = b.basho.start_date or date(
                    b.basho.year,
                    b.basho.month,
                    1,
                )
                pair = tuple(sorted((b.east_id, b.west_id)))
                records.setdefault(pair, {}).setdefault(start, {})
                winner_counts = records[pair][start]
                winner_counts[b.winner_id] = (
                    winner_counts.get(b.winner_id, 0) + 1
                )

            cumulative: dict[tuple[int, int], dict[date, dict[int, int]]] = {}
            for pair, date_map in records.items():
                dates = sorted(date_map)
                r1, r2 = pair
                totals = {r1: 0, r2: 0}
                before: dict[date, dict[int, int]] = {}
                for d in dates:
                    before[d] = totals.copy()
                    for rid, cnt in date_map[d].items():
                        totals[rid] = totals.get(rid, 0) + cnt
                cumulative[pair] = before

            hist_map = {(h.rikishi_id, h.basho_id): h for h in histories}
            rating_map = {(r.rikishi_id, r.basho_id): r for r in ratings}
            form_map = recent_form(bouts)

            for bout in bouts:
                east_hist = hist_map.get((bout.east_id, bout.basho_id))
                west_hist = hist_map.get((bout.west_id, bout.basho_id))
                east_rating = rating_map.get((bout.east_id, bout.basho_id))
                west_rating = rating_map.get((bout.west_id, bout.basho_id))
                start = bout.basho.start_date or date(
                    bout.basho.year,
                    bout.basho.month,
                    1,
                )
                pair = tuple(sorted((bout.east_id, bout.west_id)))
                prior_counts = cumulative.get(pair, {}).get(
                    start,
                    {bout.east_id: 0, bout.west_id: 0},
                )
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
                east_form = form_map.get((bout.east_id, bout.basho_id), "")
                west_form = form_map.get((bout.west_id, bout.basho_id), "")

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
                        east_form,
                        west_form,
                        1 if bout.winner_id == bout.east_id else 0,
                    ]
                )
                processed += 1
                if processed % step == 0 or processed == total:
                    percent = processed * 100 // total
                    filled = percent // 10
                    bar = "=" * filled + "." * (10 - filled)
                    self.stdout.write(f"[{bar}] {percent}%")
        msg = self.style.SUCCESS(f"Dataset saved to {outfile}")
        self.stdout.write(msg)
