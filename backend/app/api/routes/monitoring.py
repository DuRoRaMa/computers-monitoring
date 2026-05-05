from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.inference import predict_state
from app.schemas.monitoring import MonitoringInput
from app.services.expert_solver import ExpertSolver

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

MONITORING_KEYS = [
    "cpu_load",
    "ram_usage",
    "cpu_temp",
    "disk_speed",
    "disk_fill",
    "network_bandwidth",
    "process_count",
    "service_state",
]

MISSING_LABELS = {
    "cpu_load": "CPU загрузка",
    "ram_usage": "RAM занятость",
    "cpu_temp": "CPU температура",
    "disk_speed": "Диск скорость",
    "disk_fill": "Диск заполнение",
    "network_bandwidth": "Сеть пропускная",
    "process_count": "Процессы количество",
    "service_state": "Сервисы состояние",
}

DEFAULTS = {
    "cpu_load": 20,
    "ram_usage": 35,
    "cpu_temp": 45,
    "disk_speed": 150,
    "disk_fill": 40,
    "network_bandwidth": 3000,
    "process_count": 80,
    "service_state": "Все работают",
}


def _count_provided(data: MonitoringInput) -> int:
    return sum(1 for key in MONITORING_KEYS if getattr(data, key) is not None)


def _missing_indicators(data: MonitoringInput) -> list[str]:
    return [MISSING_LABELS[key] for key in MONITORING_KEYS if getattr(data, key) is None]


def _resolved_expert_payload(data: MonitoringInput) -> dict:
    payload = {"previous_state": data.previous_state}
    for key in MONITORING_KEYS:
        value = getattr(data, key)
        payload[key] = DEFAULTS[key] if value is None else value
    return payload


def _raw_payload(data: MonitoringInput) -> dict:
    payload = {"previous_state": data.previous_state}
    for key in MONITORING_KEYS:
        payload[key] = getattr(data, key)
    return payload


@router.post("/evaluate")
def evaluate_monitoring(data: MonitoringInput, db: Session = Depends(get_db)):
    provided_count = _count_provided(data)

    if provided_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Нужно ввести хотя бы один показатель для анализа",
        )

    solver = ExpertSolver(db)

    missing_indicators = _missing_indicators(data)

    # 1) Экспертная система всегда считается
    expert_payload = _resolved_expert_payload(data)
    expert_result = solver.evaluate(expert_payload)

    if missing_indicators:
        expert_result["explanation"] += (
            " Часть показателей не была введена пользователем. "
            "Для экспертной системы использовано допущение об оптимальном состоянии: "
            + ", ".join(missing_indicators)
            + "."
        )

    # 2) МО тоже всегда считается
    ml_payload = _raw_payload(data)
    ml_result = predict_state(ml_payload)

    # Динамика для МО только если есть previous_state
    if data.previous_state:
        ml_dynamics = solver.detect_dynamics(
            ml_result["final_state"],
            data.previous_state,
        )
    else:
        ml_dynamics = None

    ml_diagnosis = solver.detect_diagnosis(
        ml_result["final_state"],
        ml_dynamics,
    )

    ml_result["dynamics"] = ml_dynamics
    ml_result["diagnosis"] = ml_diagnosis

    if missing_indicators:
        ml_result["explanation"] += (
            " Модель машинного обучения использована для уточнения результата, "
            "так как часть показателей отсутствовала."
        )
    else:
        ml_result["explanation"] += (
            " Модель машинного обучения рассчитана параллельно с экспертной системой "
            "для сравнения результатов."
        )

    # 3) Кто даёт итоговый ответ
    expert_is_decisive = provided_count == len(MONITORING_KEYS)
    final_source = "expert" if expert_is_decisive else "ml"
    final_result = expert_result if expert_is_decisive else ml_result

    if final_source == "expert":
        final_explanation = (
            "Итоговый ответ принят по результату экспертной системы, "
            "так как все показатели были введены и экспертная система "
            "однозначно определила состояние компьютера."
        )
    else:
        final_explanation = (
            "Итоговый ответ принят по результату модели машинного обучения, "
            "так как часть показателей не была введена и экспертная система "
            "использовала допущение об оптимальном состоянии пропущенных признаков."
        )

    return {
        "mode": "expert_and_ml",
        "final_source": final_source,
        "final_state": final_result["final_state"],
        "dynamics": final_result.get("dynamics"),
        "diagnosis": final_result["diagnosis"],
        "explanation": final_explanation,
        "missing_indicators": missing_indicators,
        "indicator_results": expert_result["indicator_results"],
        "expert_result": expert_result,
        "ml_result": ml_result,
        "resolved_input": expert_payload,
        "raw_input": ml_payload,
    }
