import random
from itertools import combinations

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from app.models import Basho, BashoHistory, BashoRating, Prediction, Rikishi


class Command(BaseCommand):
    help = "Train NN from dataset and predict next basho"

    def add_arguments(self, parser):
        parser.add_argument("dataset", help="CSV training dataset")
        parser.add_argument("--iterations", type=int, default=1000)

    def handle(self, dataset, iterations, *args, **options):
        df = pd.read_csv(dataset)
        required = ["rating_diff", "rank_diff", "rd_diff", "east_win"]
        if not all(col in df.columns for col in required):
            raise CommandError("Dataset missing required columns")
        df = df.dropna(subset=required)
        X = df[["rating_diff", "rank_diff", "rd_diff"]].astype(float)
        y = df["east_win"].astype(int)

        scaler = StandardScaler()
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
                feat = [
                    rating1.rating - rating2.rating,
                    history1.rank.value - history2.rank.value,
                    rating1.rd - rating2.rd,
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

        for rec in records.values():
            total = rec["total"]
            win_rate = rec["wins"] / total if total else 0
            rec["pred_wins"] = win_rate * 15
            Prediction.objects.update_or_create(
                rikishi=rec["obj"],
                basho=next_basho,
                defaults={"wins": rec["pred_wins"]},
            )
            self.stdout.write(
                f"{rec['obj'].name: <12} {rec['pred_wins']:.2f} wins"
            )
