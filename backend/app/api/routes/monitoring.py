from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.monitoring import MonitoringInput
from app.services.expert_solver import ExpertSolver

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/evaluate")
def evaluate_monitoring(data: MonitoringInput, db: Session = Depends(get_db)):
    solver = ExpertSolver(db)
    result = solver.evaluate(data.model_dump())
    return result


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


@router.post("/evaluate-ml-stub")
def evaluate_monitoring_ml_stub(data: MonitoringInput):
    """
    Демонстрационная заглушка под будущую ML-модель.
    Это НЕ машинное обучение, а временный имитатор ответа модели.
    """

    cpu_risk = data.cpu_load / 100
    ram_risk = data.ram_usage / 100
    temp_risk = _clamp((data.cpu_temp - 20) / 100, 0, 1)
    disk_speed_risk = 1 - _clamp(data.disk_speed / 1000, 0, 1)
    disk_fill_risk = data.disk_fill / 100
    network_risk = 1 - _clamp(data.network_bandwidth / 10000, 0, 1)
    process_risk = data.process_count / 1000

    service_risk_map = {
        "Все работают": 0.0,
        "Некоторые остановлены": 0.5,
        "Критический сервис остановлен": 1.0,
    }
    service_risk = service_risk_map.get(data.service_state, 0.0)

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

    probabilities = [
        {
            "label": "Исправен",
            "value": round(max(0.0, 1.0 - risk_score * 1.35), 3),
        },
        {
            "label": "Требует внимания",
            "value": round(max(0.0, 0.65 - abs(risk_score - 0.45)), 3),
        },
        {
            "label": "Требует обслуживания",
            "value": round(min(1.0, risk_score * 1.15), 3),
        },
    ]

    explanation = (
        "Сейчас выбран режим работы с моделью машинного обучения, "
        "но реальная модель ещё не подключена. "
        "Поэтому показан демонстрационный ответ заглушки, "
        "который имитирует вероятностную оценку состояния системы."
    )

    return {
        "mode": "ml_stub",
        "indicator_results": [],
        "final_state": final_state,
        "dynamics": None,
        "diagnosis": diagnosis,
        "explanation": explanation,
        "model_message": "ML-модель пока не обучена и не подключена. Показан демонстрационный результат.",
        "probabilities": probabilities,
    }