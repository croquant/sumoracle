import random
from datetime import date
from itertools import combinations

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from app.models import (
    Basho,
    BashoHistory,
    BashoRating,
    Bout,
    Prediction,
    Rikishi,
)

FEATURES = [
    "rating_diff",
    "rank_diff",
    "rd_diff",
    "height_diff",
    "weight_diff",
    "bmi_diff",
    "age_diff",
    "experience_diff",
    "record_diff",
]


class Command(BaseCommand):
    help = "Train NN from dataset and predict next basho"

    def add_arguments(self, parser):
        parser.add_argument("dataset", help="CSV training dataset")
        parser.add_argument("--iterations", type=int, default=10000)

    def handle(self, dataset, iterations, *args, **options):
        df = pd.read_csv(dataset)
        required = FEATURES + ["east_win"]
        if not all(col in df.columns for col in required):
            raise CommandError("Dataset missing required columns")
        df = df.dropna(subset=required)
        X = df[FEATURES].astype(float).to_numpy()
        y = df["east_win"].astype(int).to_numpy()

        scaler = StandardScaler()
        print(X.shape, y.shape)
        X_scaled = scaler.fit_transform(X)

        model = MLPClassifier(
            hidden_layer_sizes=(10,), max_iter=200, random_state=42
        )
        model.fit(X_scaled, y)

        next_basho = (
            Basho.objects.filter(bouts__isnull=True)
            .order_by("-year", "-month")
            .first()
        )
        if not next_basho:
            self.stdout.write("No upcoming basho found")
            return

        rikishi = list(
            Rikishi.objects.filter(
                intai__isnull=True, rank__division__name="Makuuchi"
            ).select_related("rank", "heya")
        )
        if not rikishi:
            self.stdout.write("No rikishi found")
            return

        ratings = {
            r.id: BashoRating.objects.filter(rikishi=r)
            .order_by("-basho__year", "-basho__month")
            .first()
            for r in rikishi
        }
        histories = {
            r.id: BashoHistory.objects.filter(
                rikishi=r, basho=next_basho
            ).first()
            for r in rikishi
        }

        start = next_basho.start_date or date(
            next_basho.year, next_basho.month, 1
        )

        probs = {}
        for r1, r2 in combinations(rikishi, 2):
            if r1.heya_id and r1.heya_id == r2.heya_id:
                continue
            rating1 = ratings.get(r1.id)
            rating2 = ratings.get(r2.id)
            history1 = histories.get(r1.id)
            history2 = histories.get(r2.id)
            if not rating1 or not rating2 or not history1 or not history2:
                p = 0.5
            else:
                h1 = history1.height or r1.height or 0
                h2 = history2.height or r2.height or 0
                w1 = history1.weight or r1.weight or 0
                w2 = history2.weight or r2.weight or 0
                bmi1 = round(w1 / ((h1 / 100) ** 2), 2) if h1 and w1 else 0
                bmi2 = round(w2 / ((h2 / 100) ** 2), 2) if h2 and w2 else 0
                age1 = (
                    (start - r1.birth_date).days / 365.25
                    if r1.birth_date
                    else None
                )
                age2 = (
                    (start - r2.birth_date).days / 365.25
                    if r2.birth_date
                    else None
                )
                exp1 = (start - r1.debut).days / 365.25 if r1.debut else None
                exp2 = (start - r2.debut).days / 365.25 if r2.debut else None
                bouts = Bout.objects.filter(
                    Q(east_id=r1.id, west_id=r2.id)
                    | Q(east_id=r2.id, west_id=r1.id),
                    Q(basho__year__lt=next_basho.year)
                    | Q(
                        basho__year=next_basho.year,
                        basho__month__lt=next_basho.month,
                    ),
                )
                wins1 = bouts.filter(winner=r1).count()
                wins2 = bouts.filter(winner=r2).count()
                rec_diff = wins1 - wins2
                feat = [
                    rating1.rating - rating2.rating,
                    history1.rank.value - history2.rank.value,
                    rating1.rd - rating2.rd,
                    h1 - h2,
                    w1 - w2,
                    bmi1 - bmi2,
                    (
                        age1 - age2
                        if age1 is not None and age2 is not None
                        else 0
                    ),
                    (
                        exp1 - exp2
                        if exp1 is not None and exp2 is not None
                        else 0
                    ),
                    rec_diff,
                ]
                feat = scaler.transform([feat])
                p = float(model.predict_proba(feat)[0, 1])
            probs.setdefault(r1.id, {})[r2.id] = p
            probs.setdefault(r2.id, {})[r1.id] = 1 - p

        records = {r.id: {"wins": 0, "total": 0, "obj": r} for r in rikishi}

        pairs = [
            (r1, r2)
            for r1, r2 in combinations(rikishi, 2)
            if not (r1.heya_id and r1.heya_id == r2.heya_id)
        ]

        for _ in range(iterations):
            for r1, r2 in pairs:
                p = probs[r1.id][r2.id]
                winner = r1 if random.random() < p else r2
                records[winner.id]["wins"] += 1
                records[r1.id]["total"] += 1
                records[r2.id]["total"] += 1

        # Compute predicted wins
        for rec in records.values():
            total = rec["total"]
            win_rate = rec["wins"] / total if total else 0
            rec["pred_wins"] = win_rate * 15
            Prediction.objects.update_or_create(
                rikishi=rec["obj"],
                basho=next_basho,
                defaults={"wins": rec["pred_wins"]},
            )
        # Sort by predicted wins descending
        sorted_records = sorted(
            records.values(), key=lambda r: r["pred_wins"], reverse=True
        )
        self.stdout.write(f"Predictions for {next_basho}:")
        for rec in sorted_records:
            self.stdout.write(
                (
                    f"{rec['obj'].rank.short_name()} "
                    f"{rec['obj'].name: <12} "
                    f"{rec['pred_wins']:.2f} wins"
                )
            )
