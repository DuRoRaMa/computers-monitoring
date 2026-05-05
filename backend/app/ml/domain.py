from __future__ import annotations

import random
from typing import Any

STATE_ORDER = {
    "Оптимальное": 0,
    "Хорошее": 1,
    "Критическое": 2,
    "Критическое с риском отказа": 3,
}

FEATURE_NAMES = [
    "cpu_load",
    "ram_usage",
    "cpu_temp",
    "disk_speed",
    "disk_fill",
    "network_bandwidth",
    "process_count",
    "service_state",
]

NUMERIC_FEATURES = [
    "cpu_load",
    "ram_usage",
    "cpu_temp",
    "disk_speed",
    "disk_fill",
    "network_bandwidth",
    "process_count",
]

CATEGORICAL_FEATURES = ["service_state"]

DISPLAY_NAMES = {
    "cpu_load": "CPU загрузка",
    "ram_usage": "RAM занятость",
    "cpu_temp": "CPU температура",
    "disk_speed": "Диск скорость",
    "disk_fill": "Диск заполнение",
    "network_bandwidth": "Сеть пропускная",
    "process_count": "Процессы количество",
    "service_state": "Сервисы состояние",
}

SERVICE_STATES = [
    "Все работают",
    "Некоторые остановлены",
    "Критический сервис остановлен",
]

# Интервалы для генерации данных по состояниям
RANGES: dict[str, dict[str, list[tuple[float, float]]]] = {
    "cpu_load": {
        "Оптимальное": [(0, 30)],
        "Хорошее": [(30, 60)],
        "Критическое": [(60, 90)],
        "Критическое с риском отказа": [(90, 100)],
    },
    "ram_usage": {
        "Оптимальное": [(0, 40)],
        "Хорошее": [(40, 70)],
        "Критическое": [(70, 95)],
        "Критическое с риском отказа": [(95, 100)],
    },
    "cpu_temp": {
        "Оптимальное": [(20, 50)],
        "Хорошее": [(50, 75)],
        "Критическое": [(75, 100)],
        "Критическое с риском отказа": [(100, 120)],
    },
    "disk_speed": {
        "Оптимальное": [(80, 1000)],
        "Хорошее": [(50, 80)],
        "Критическое": [(10, 50)],
        "Критическое с риском отказа": [(0, 10)],
    },
    "disk_fill": {
        "Оптимальное": [(0, 70)],
        "Хорошее": [(70, 85)],
        "Критическое": [(85, 98)],
        "Критическое с риском отказа": [(98, 100)],
    },
    "network_bandwidth": {
        "Оптимальное": [(0, 8000)],
        "Хорошее": [(8000, 9000)],
        "Критическое": [(9000, 10000)],
    },
    "process_count": {
        "Оптимальное": [(30, 100)],
        "Хорошее": [(100, 200)],
        "Критическое": [(200, 500)],
        "Критическое с риском отказа": [(0, 10), (500, 1000)],
    },
}

SERVICE_BY_STATE = {
    "Оптимальное": ["Все работают"],
    "Хорошее": ["Все работают"],
    "Критическое": ["Некоторые остановлены"],
    "Критическое с риском отказа": ["Критический сервис остановлен"],
}


def _sample_from_intervals(intervals: list[tuple[float, float]], rng: random.Random) -> float:
    lo, hi = rng.choice(intervals)
    return rng.uniform(lo, hi)


def _sample_process_count(intervals: list[tuple[float, float]], rng: random.Random) -> int:
    lo, hi = rng.choice(intervals)
    return int(rng.randint(int(lo), int(hi)))


def sample_feature_value(feature: str, state: str, rng: random.Random) -> Any:
    if feature == "service_state":
        return rng.choice(SERVICE_BY_STATE[state])

    intervals = RANGES[feature][state]
    if feature == "process_count":
        return _sample_process_count(intervals, rng)

    value = _sample_from_intervals(intervals, rng)
    return round(value, 2)


def available_states_for_feature(feature: str) -> list[str]:
    if feature == "service_state":
        return list(SERVICE_BY_STATE.keys())
    return list(RANGES[feature].keys())


def severity_for_feature(feature: str, value: Any) -> str:
    if feature == "service_state":
        if value == "Все работают":
            return "Оптимальное"
        if value == "Некоторые остановлены":
            return "Критическое"
        return "Критическое с риском отказа"

    if feature == "cpu_load":
        if value <= 30:
            return "Оптимальное"
        if value <= 60:
            return "Хорошее"
        if value <= 90:
            return "Критическое"
        return "Критическое с риском отказа"

    if feature == "ram_usage":
        if value <= 40:
            return "Оптимальное"
        if value <= 70:
            return "Хорошее"
        if value <= 95:
            return "Критическое"
        return "Критическое с риском отказа"

    if feature == "cpu_temp":
        if value <= 50:
            return "Оптимальное"
        if value <= 75:
            return "Хорошее"
        if value <= 100:
            return "Критическое"
        return "Критическое с риском отказа"

    if feature == "disk_speed":
        if value >= 80:
            return "Оптимальное"
        if value >= 50:
            return "Хорошее"
        if value >= 10:
            return "Критическое"
        return "Критическое с риском отказа"

    if feature == "disk_fill":
        if value <= 70:
            return "Оптимальное"
        if value <= 85:
            return "Хорошее"
        if value <= 98:
            return "Критическое"
        return "Критическое с риском отказа"

    if feature == "network_bandwidth":
        if value <= 8000:
            return "Оптимальное"
        if value <= 9000:
            return "Хорошее"
        return "Критическое"

    if feature == "process_count":
        if value < 10:
            return "Критическое с риском отказа"
        if value <= 100:
            return "Оптимальное"
        if value <= 200:
            return "Хорошее"
        if value <= 500:
            return "Критическое"
        return "Критическое с риском отказа"

    raise ValueError(f"Неизвестный признак: {feature}")


def infer_state_from_features(row: dict[str, Any]) -> str:
    severities: list[str] = []

    for feature in FEATURE_NAMES:
        value = row.get(feature)
        if value is None:
            continue
        severities.append(severity_for_feature(feature, value))

    if not severities:
        raise ValueError("Невозможно определить состояние без признаков")

    return max(severities, key=lambda s: STATE_ORDER[s])
