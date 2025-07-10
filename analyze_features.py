from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_dataset(path: str) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)
    if "east_win" not in df.columns:
        raise ValueError("Dataset must contain 'east_win' column")
    X = df.drop("east_win", axis=1)
    y = df["east_win"]
    X = X.drop(columns=["east_id", "west_id"], errors="ignore")
    for col in X.select_dtypes(include="object").columns:
        try:
            X[col] = pd.to_numeric(X[col])
        except (ValueError, TypeError):
            X[col] = X[col].astype("category")
    cat_cols = X.select_dtypes(include="category").columns
    X = pd.get_dummies(X, columns=cat_cols, drop_first=True, dtype=np.int8)
    num_cols = X.select_dtypes(include="number").columns
    X[num_cols] = X[num_cols].fillna(X[num_cols].median())
    return X, y


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute permutation feature importances"
    )
    parser.add_argument("dataset", help="CSV dataset path")
    parser.add_argument("--plot", help="Path to save plot", default=None)
    parser.add_argument(
        "--table", help="Optional CSV ranking output", default=None
    )
    args = parser.parse_args()

    X, y = load_dataset(args.dataset)

    stratify = y if y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )

    scaler = StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    score = model.score(X_test, y_test)

    result = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=10,
        random_state=42,
        scoring="accuracy",
    )
    order = result.importances_mean.argsort()[::-1]
    features = np.array(X.columns)[order]
    importances = result.importances_mean[order]

    if args.table:
        table = Path(args.table)
        pd.DataFrame({"feature": features, "importance": importances}).to_csv(
            table, index=False
        )

    if args.plot:
        plt.figure(figsize=(8, max(2, len(features) / 4)))
        plt.barh(features[::-1], importances[::-1])
        plt.xlabel("Mean importance")
        plt.tight_layout()
        plt.savefig(args.plot)

    print(f"Accuracy: {score:.3f}")
    for feat, imp in zip(features[:20], importances[:20], strict=False):
        print(f"{feat}: {imp:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
