from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.ml.domain import CATEGORICAL_FEATURES, FEATURE_NAMES, NUMERIC_FEATURES

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
DATASET_PATH = ARTIFACTS_DIR / "synthetic_monitoring_dataset.csv"
MODEL_PATH = ARTIFACTS_DIR / "rf_state_classifier.joblib"
META_PATH = ARTIFACTS_DIR / "rf_state_classifier_meta.json"


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}. "
            "Сначала запусти python -m app.ml.generate_dataset"
        )

    df = pd.read_csv(DATASET_PATH)

    for feature in FEATURE_NAMES:
        df[f"{feature}_is_missing"] = df[feature].isna().astype(int)

    y = df["state"]
    mask_features = [f"{feature}_is_missing" for feature in FEATURE_NAMES]
    X = df[FEATURE_NAMES + mask_features]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                SimpleImputer(strategy="median"),
                NUMERIC_FEATURES,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value="неизвестно")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "mask",
                "passthrough",
                mask_features,
            ),
        ],
        verbose_feature_names_out=False,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                RandomForestClassifier(
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    param_distributions = {
        "model__n_estimators": [200, 300, 500, 700],
        "model__max_depth": [6, 8, 10, 12, 16, None],
        "model__min_samples_split": [2, 5, 10, 20],
        "model__min_samples_leaf": [1, 2, 4, 8],
        "model__max_features": ["sqrt", "log2", None],
        "model__class_weight": [None, "balanced"],
    }

    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_distributions,
        n_iter=20,
        scoring="f1_macro",
        cv=5,
        verbose=2,
        random_state=42,
        n_jobs=-1,
    )

    search.fit(X_train, y_train)

    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)

    macro_f1 = f1_score(y_test, y_pred, average="macro")
    report = classification_report(y_test, y_pred, output_dict=True)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    meta = {
        "dataset_path": str(DATASET_PATH),
        "model_path": str(MODEL_PATH),
        "best_params": search.best_params_,
        "best_cv_score_f1_macro": search.best_score_,
        "test_f1_macro": macro_f1,
        "class_distribution": y.value_counts().to_dict(),
        "feature_names": FEATURE_NAMES,
        "mask_features": mask_features,
        "classification_report": report,
    }

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("Training finished")
    print(f"Best params: {search.best_params_}")
    print(f"Best CV f1_macro: {search.best_score_:.4f}")
    print(f"Test f1_macro: {macro_f1:.4f}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Meta saved to: {META_PATH}")


if __name__ == "__main__":
    main()
