from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd

from app.ml.domain import (
    FEATURE_NAMES,
    STATE_ORDER,
    available_states_for_feature,
    infer_state_from_features,
    sample_feature_value,
)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_full_record(target_state: str, rng: random.Random) -> dict:
    eligible_anchor_features = [
        feature for feature in FEATURE_NAMES
        if target_state in available_states_for_feature(feature)
    ]
    anchor_feature = rng.choice(eligible_anchor_features)

    for _ in range(200):
        row: dict = {}

        for feature in FEATURE_NAMES:
            states = [
                s
                for s in available_states_for_feature(feature)
                if STATE_ORDER[s] <= STATE_ORDER[target_state]
            ]

            chosen_state = target_state if feature == anchor_feature else rng.choice(states)
            row[feature] = sample_feature_value(feature, chosen_state, rng)

        inferred = infer_state_from_features(row)
        if inferred == target_state:
            row["state"] = inferred
            return row

    raise RuntimeError(f"Не удалось сгенерировать запись для состояния {target_state}")


def make_partial_record(full_row: dict, rng: random.Random) -> dict:
    row = dict(full_row)
    feature_count = len(FEATURE_NAMES)
    missing_count = rng.randint(1, feature_count - 1)
    missing_features = rng.sample(FEATURE_NAMES, k=missing_count)

    for feature in missing_features:
        row[feature] = None

    return row


def build_dataset(
    total_rows: int = 10000,
    partial_ratio: float = 0.45,
    seed: int = 42,
) -> pd.DataFrame:
    rng = random.Random(seed)

    states = [
        "Оптимальное",
        "Хорошее",
        "Критическое",
        "Критическое с риском отказа",
    ]
    weights = [0.34, 0.30, 0.22, 0.14]

    full_count = int(total_rows * (1.0 - partial_ratio))
    partial_count = total_rows - full_count

    full_rows = []
    for _ in range(full_count):
        target_state = rng.choices(states, weights=weights, k=1)[0]
        full_rows.append(generate_full_record(target_state, rng))

    partial_rows = []
    for _ in range(partial_count):
        base = rng.choice(full_rows)
        partial_rows.append(make_partial_record(base, rng))

    df = pd.DataFrame(full_rows + partial_rows)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10000)
    parser.add_argument("--partial-ratio", type=float, default=0.45)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=str,
        default=str(ARTIFACTS_DIR / "synthetic_monitoring_dataset.csv"),
    )
    args = parser.parse_args()

    df = build_dataset(
        total_rows=args.rows,
        partial_ratio=args.partial_ratio,
        seed=args.seed,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False, encoding="utf-8-sig")

    print(f"Dataset saved to: {output}")
    print(df["state"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
