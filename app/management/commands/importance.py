import csv

from sklearn.inspection import permutation_importance
from sklearn.neural_network import MLPClassifier

from app.management.commands import AsyncBaseCommand


class Command(AsyncBaseCommand):
    """Train a model and print feature importances."""

    help = "Train model and show feature importance"

    def add_arguments(self, parser):
        parser.add_argument("dataset", help="CSV dataset path")

    async def run(self, dataset, **options):
        with open(dataset) as fh:
            reader = csv.DictReader(fh)
            fields = [f for f in reader.fieldnames if f != "east_win"]
            X = []
            y = []
            for row in reader:
                X.append([float(row[f] or 0) for f in fields])
                y.append(int(row["east_win"]))
        model = MLPClassifier(random_state=42, max_iter=500)
        model.fit(X, y)
        result = permutation_importance(model, X, y, random_state=42)
        pairs = zip(result.importances_mean, fields, strict=False)
        ranked = sorted(pairs, reverse=True)
        for score, name in ranked:
            self.stdout.write(f"{name}: {score:.3f}")
        msg = self.style.SUCCESS("Training complete")
        self.stdout.write(msg)
