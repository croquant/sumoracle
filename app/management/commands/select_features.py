from __future__ import annotations

import numpy as np
import pandas as pd
from django.core.management.base import CommandError
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from app.management.commands import AsyncBaseCommand


class Command(AsyncBaseCommand):
    """Select informative features from a dataset."""

    help = "Run feature selection on CSV dataset"

    def add_arguments(self, parser):
        parser.add_argument("infile", help="CSV file path")
        parser.add_argument("outfile", nargs="?", help="Reduced CSV path")
        parser.add_argument(
            "--k", type=int, default=20, help="Number of features to keep"
        )

    async def run(
        self, infile: str, outfile: str | None = None, k: int = 20, **options
    ):
        df = pd.read_csv(infile)
        if "east_win" not in df.columns:
            raise CommandError("Dataset must contain 'east_win' column")

        X = df.drop("east_win", axis=1)
        y = df["east_win"]

        # convert possible numeric strings to numbers
        X = X.apply(pd.to_numeric, errors="ignore")

        # drop columns with too many missing values
        miss = X.isnull().mean()
        drop_cols = miss[miss > 0.2].index.tolist()
        if drop_cols:
            X = X.drop(columns=drop_cols)
            self.stdout.write(f"Dropped {len(drop_cols)} columns: {drop_cols}")

        # impute remaining missing values
        num_cols = X.select_dtypes(include="number").columns
        cat_cols = X.select_dtypes(exclude="number").columns

        for col in num_cols:
            if X[col].isnull().any():
                X[col] = X[col].fillna(X[col].median())

        for col in cat_cols:
            if X[col].isnull().any():
                mode = X[col].mode().dropna()
                X[col] = X[col].fillna(mode[0] if not mode.empty else "missing")
        X = pd.get_dummies(X, columns=cat_cols, drop_first=True)

        corr = X.corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        to_drop = [c for c in upper.columns if any(upper[c] > 0.9)]
        if to_drop:
            X = X.drop(columns=to_drop)
            self.stdout.write(f"Dropped {len(to_drop)} correlated cols")

        stratify = y if y.nunique() > 1 else None
        X_train, _x, y_train, _y = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=stratify
        )

        scaler = StandardScaler().fit(X_train)
        X_scaled = scaler.transform(X_train)

        k = min(k, X_scaled.shape[1])
        selector = SelectKBest(score_func=f_classif, k=k).fit(X_scaled, y_train)
        mask = selector.get_support()
        scores = selector.scores_
        selected = X.columns[mask]

        ranking = pd.Series(scores, index=X.columns).sort_values(
            ascending=False
        )

        self.stdout.write("Selected features with scores:")
        for feat, score in ranking.loc[selected].items():
            self.stdout.write(f"- {feat}: {score:.2f}")

        if outfile:
            df[selected.tolist() + ["east_win"]].to_csv(outfile, index=False)
            self.stdout.write(self.style.SUCCESS(f"Saved to {outfile}"))
