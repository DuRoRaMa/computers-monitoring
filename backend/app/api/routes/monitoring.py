from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.monitoring import MonitoringInput
from app.services.expert_solver import ExpertSolver

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _resolved_ml_input(data: MonitoringInput) -> dict:
    return {
        "cpu_load": 20 if data.cpu_load is None else data.cpu_load,
        "ram_usage": 35 if data.ram_usage is None else data.ram_usage,
        "cpu_temp": 45 if data.cpu_temp is None else data.cpu_temp,
        "disk_speed": 150 if data.disk_speed is None else data.disk_speed,
        "disk_fill": 40 if data.disk_fill is None else data.disk_fill,
        "network_bandwidth": 3000 if data.network_bandwidth is None else data.network_bandwidth,
        "process_count": 80 if data.process_count is None else data.process_count,
        "service_state": "Все работают" if data.service_state is None else data.service_state,
        "previous_state": data.previous_state,
    }


@router.post("/evaluate")
def evaluate_monitoring(data: MonitoringInput, db: Session = Depends(get_db)):
    solver = ExpertSolver(db)
    result = solver.evaluate(data.model_dump(exclude_none=True))
    return result


@router.post("/evaluate-ml-stub")
def evaluate_monitoring_ml_stub(data: MonitoringInput):
    """
    Демонстрационная заглушка под будущую ML-модель.
    Это НЕ машинное обучение, а временный имитатор ответа модели.
    """

    resolved = _resolved_ml_input(data)

    cpu_risk = resolved["cpu_load"] / 100
    ram_risk = resolved["ram_usage"] / 100
    temp_risk = _clamp((resolved["cpu_temp"] - 20) / 100, 0, 1)
    disk_speed_risk = 1 - _clamp(resolved["disk_speed"] / 1000, 0, 1)
    disk_fill_risk = resolved["disk_fill"] / 100
    network_risk = 1 - _clamp(resolved["network_bandwidth"] / 10000, 0, 1)
    process_risk = resolved["process_count"] / 1000

    service_risk_map = {
        "Все работают": 0.0,
        "Некоторые остановлены": 0.5,
        "Критический сервис остановлен": 1.0,
    }
    service_risk = service_risk_map.get(resolved["service_state"], 0.0)

    risk_score = (
        cpu_risk * 0.15
        + ram_risk * 0.15
        + temp_risk * 0.20
        + disk_speed_risk * 0.10
        + disk_fill_risk * 0.10
        + network_risk * 0.10
        + process_risk * 0.10
        + service_risk * 0.10
    )

    if risk_score < 0.30:
        final_state = "Хорошее"
        diagnosis = "Исправен"
    elif risk_score < 0.55:
        final_state = "Критическое"
        diagnosis = "Требует внимания"
    else:
        final_state = "Критическое с риском отказа"
        diagnosis = "Требует обслуживания"

    missing_indicators = []
    if data.cpu_load is None:
        missing_indicators.append("CPU загрузка")
    if data.ram_usage is None:
        missing_indicators.append("RAM занятость")
    if data.cpu_temp is None:
        missing_indicators.append("CPU температура")
    if data.disk_speed is None:
        missing_indicators.append("Диск скорость")
    if data.disk_fill is None:
        missing_indicators.append("Диск заполнение")
    if data.network_bandwidth is None:
        missing_indicators.append("Сеть пропускная")
    if data.process_count is None:
        missing_indicators.append("Процессы количество")
    if data.service_state is None:
        missing_indicators.append("Сервисы состояние")

    explanation = (
        "Показан демонстрационный результат модуля машинного обучения. "
        "Реальная ML-модель пока не подключена. "
    )

    if missing_indicators:
        explanation += (
            "Часть признаков не была введена. "
            "Для расчёта заглушка использовала нейтральные значения: "
            + ", ".join(missing_indicators)
            + "."
        )

    probabilities = [
        {"label": "Исправен", "value": round(max(0.0, 1.0 - risk_score * 1.35), 3)},
        {"label": "Требует внимания", "value": round(max(0.0, 0.65 - abs(risk_score - 0.45)), 3)},
        {"label": "Требует обслуживания", "value": round(min(1.0, risk_score * 1.15), 3)},
    ]

    return {
        "mode": "ml_stub",
        "indicator_results": [],
        "final_state": final_state,
        "dynamics": None,
        "diagnosis": diagnosis,
        "explanation": explanation,
        "model_message": "ML-модель пока не обучена и не подключена. Показан демонстрационный результат.",
        "probabilities": probabilities,
        "missing_indicators": missing_indicators,
        "resolved_input": resolved,
    }
