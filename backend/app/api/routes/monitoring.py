from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.inference import predict_state
from app.models.indicator import Indicator
from app.models.possible_value import PossibleValue
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

NUMERIC_MONITORING_KEYS = [
    "cpu_load",
    "ram_usage",
    "cpu_temp",
    "disk_speed",
    "disk_fill",
    "network_bandwidth",
    "process_count",
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


def _normalize_monitoring_value(key: str, value):
    if value is None:
        return None

    if key in NUMERIC_MONITORING_KEYS:
        return int(value)

    return value


def _resolved_expert_payload(data: MonitoringInput) -> dict:
    payload = {"previous_state": data.previous_state}
    for key in MONITORING_KEYS:
        value = getattr(data, key)
        payload[key] = DEFAULTS[key] if value is None else _normalize_monitoring_value(key, value)
    return payload


def _raw_payload(data: MonitoringInput) -> dict:
    payload = {"previous_state": data.previous_state}
    for key in MONITORING_KEYS:
        payload[key] = _normalize_monitoring_value(key, getattr(data, key))
    return payload


def _float_to_text(value: float | None) -> str:
    if value is None:
        return ""

    if float(value).is_integer():
        return str(int(value))

    return str(value)


def _format_possible_value(value: PossibleValue) -> str:
    if value.value_kind == "scalar":
        return value.scalar_value or ""

    left = "[" if value.min_inclusive else "("
    right = "]" if value.max_inclusive else ")"

    return f"{left}{_float_to_text(value.min_value)};{_float_to_text(value.max_value)}{right}"


def _number_in_possible_range(number: float, possible_value: PossibleValue) -> bool:
    if possible_value.value_kind != "range":
        return False

    if possible_value.min_value is None or possible_value.max_value is None:
        return False

    left_ok = (
        number >= possible_value.min_value
        if possible_value.min_inclusive
        else number > possible_value.min_value
    )

    right_ok = (
        number <= possible_value.max_value
        if possible_value.max_inclusive
        else number < possible_value.max_value
    )

    return left_ok and right_ok


def _scalar_in_possible_values(value: str, possible_value: PossibleValue) -> bool:
    if possible_value.value_kind != "scalar":
        return False

    return str(value).strip() == str(possible_value.scalar_value).strip()


def _validate_numeric_monitoring_value(indicator_name: str, value) -> int:
    if isinstance(value, bool):
        raise HTTPException(
            status_code=400,
            detail=f"Значение показателя «{indicator_name}» должно быть целым числом",
        )

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail=f"Значение показателя «{indicator_name}» должно быть целым числом",
        )

    if not numeric_value.is_integer():
        raise HTTPException(
            status_code=400,
            detail=f"Значение показателя «{indicator_name}» должно быть целым числом",
        )

    return int(numeric_value)


def _validate_monitoring_input_by_possible_values(data: MonitoringInput, db: Session) -> None:
    for field_name in MONITORING_KEYS:
        value = getattr(data, field_name)

        if value is None:
            continue

        indicator_name = MISSING_LABELS[field_name]

        indicator = (
            db.query(Indicator)
            .filter(Indicator.name == indicator_name)
            .first()
        )

        if not indicator:
            raise HTTPException(
                status_code=400,
                detail=f"В базе знаний не найден показатель «{indicator_name}»",
            )

        possible_values = (
            db.query(PossibleValue)
            .filter(PossibleValue.indicator_id == indicator.id)
            .order_by(PossibleValue.id)
            .all()
        )

        if not possible_values:
            raise HTTPException(
                status_code=400,
                detail=f"Для показателя «{indicator_name}» сначала задайте возможное значение",
            )

        if indicator.value_type == "numeric":
            numeric_value = _validate_numeric_monitoring_value(indicator_name, value)
            is_valid = any(
                _number_in_possible_range(numeric_value, possible_value)
                for possible_value in possible_values
            )
        else:
            is_valid = any(
                _scalar_in_possible_values(str(value), possible_value)
                for possible_value in possible_values
            )

        if not is_valid:
            allowed_values = ", ".join(_format_possible_value(row) for row in possible_values)
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Значение показателя «{indicator_name}» должно входить "
                    f"в возможное значение: {allowed_values}"
                ),
            )


@router.post("/evaluate")
def evaluate_monitoring(data: MonitoringInput, db: Session = Depends(get_db)):
    provided_count = _count_provided(data)

    if provided_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Нужно ввести хотя бы один показатель для анализа",
        )

    _validate_monitoring_input_by_possible_values(data, db)

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
