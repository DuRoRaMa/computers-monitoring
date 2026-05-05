from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from app.ml.domain import FEATURE_NAMES

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "rf_state_classifier.joblib"


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML model not found: {MODEL_PATH}. "
            "Сначала запусти python -m app.ml.train_model"
        )
    return joblib.load(MODEL_PATH)


def build_model_frame(payload: dict) -> pd.DataFrame:
    row = {}

    for feature in FEATURE_NAMES:
        value = payload.get(feature)
        row[feature] = value
        row[f"{feature}_is_missing"] = int(value is None)

    return pd.DataFrame([row])


def predict_state(payload: dict) -> dict:
    model = load_model()
    X = build_model_frame(payload)

    predicted_state = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]
    classes = list(model.named_steps["model"].classes_)

    result_probs = [
        {"label": class_name, "value": round(float(prob), 4)}
        for class_name, prob in zip(classes, probabilities)
    ]
    result_probs.sort(key=lambda item: item["value"], reverse=True)

    return {
        "final_state": predicted_state,
        "probabilities": result_probs,
        "explanation": (
            "Результат получен моделью Random Forest, обученной на синтетической выборке, "
            "сформированной на основе правил базы знаний."
        ),
    }
