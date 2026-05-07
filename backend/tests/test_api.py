"""
Unit tests for Computer Monitoring API.

Как запускать:
1. Положить файл в backend/tests/test_api.py
2. Из папки backend выполнить:
   pytest -q

Важно:
- POST /knowledge/seed-basic и POST /knowledge/seed-rules используются только как подготовка изолированной тестовой БД.
- Они не считаются тестами функциональности системы.
- ML-модель замокана, потому что это unit-тестирование API, а не тестирование файла обученной модели.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
import app.api.routes.monitoring as monitoring_route


@pytest.fixture()
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def fake_predict_state(payload: dict) -> dict:
        if payload.get("cpu_load") is not None and payload["cpu_load"] >= 90:
            final_state = "Критическое с риском отказа"
        elif payload.get("cpu_load") is not None and payload["cpu_load"] >= 60:
            final_state = "Критическое"
        else:
            final_state = "Оптимальное"

        return {
            "final_state": final_state,
            "probabilities": [
                {"label": final_state, "value": 0.95},
                {"label": "Оптимальное", "value": 0.05},
            ],
            "explanation": "Тестовая заглушка ML-модели.",
        }

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(monitoring_route, "predict_state", fake_predict_state)

    with TestClient(app) as test_client:
        # Подготовка базы знаний для тестов экспертной системы.
        # Эти вызовы не входят в отчет как отдельные тесты.
        test_client.post("/knowledge/seed-basic")
        test_client.post("/knowledge/seed-rules")
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def item_id_by_name(client: TestClient, endpoint: str, name: str) -> int:
    response = client.get(endpoint)
    assert response.status_code == 200
    for item in response.json():
        if item["name"] == name:
            return item["id"]
    raise AssertionError(f"Item with name {name!r} not found at {endpoint}")


def create_indicator(client: TestClient, name: str, value_type: str = "numeric") -> int:
    response = client.post(
        "/knowledge/indicators",
        json={"name": name, "value_type": value_type},
    )
    assert response.status_code == 200
    return response.json()["id"]


def create_diagnosis(client: TestClient, name: str) -> int:
    response = client.post("/knowledge/diagnoses", json={"name": name})
    assert response.status_code == 200
    return response.json()["id"]


def observation_payload() -> dict:
    return {
        "cpu_load": 20,
        "ram_usage": 35,
        "cpu_temp": 45,
        "disk_speed": 150,
        "disk_fill": 40,
        "network_bandwidth": 3000,
        "process_count": 80,
        "service_state": "Все работают",
        "previous_state": None,
        "final_state": "Оптимальное",
        "dynamics": None,
        "diagnosis": "Исправен",
        "explanation": "Тестовое сохранение результата мониторинга.",
        "indicator_results": [
            {"indicator": "CPU загрузка", "value": 20, "severity": "Оптимальное"},
            {"indicator": "RAM занятость", "value": 35, "severity": "Оптимальное"},
        ],
    }


def create_observation(client: TestClient) -> int:
    response = client.post("/observations", json=observation_payload())
    assert response.status_code == 200
    return response.json()["id"]


def test_health_check_returns_ok(client):
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_indicator_success(client):
    response = client.post(
        "/knowledge/indicators",
        json={"name": "Тестовый показатель", "value_type": "numeric"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Тестовый показатель"
    assert body["value_type"] == "numeric"


def test_create_indicator_empty_name_rejected(client):
    response = client.post(
        "/knowledge/indicators",
        json={"name": "   ", "value_type": "numeric"},
    )

    assert response.status_code == 400
    assert "не может быть пустым" in response.json()["detail"]


def test_create_indicator_duplicate_rejected(client):
    payload = {"name": "Дублируемый показатель", "value_type": "numeric"}
    first = client.post("/knowledge/indicators", json=payload)
    second = client.post("/knowledge/indicators", json=payload)

    assert first.status_code == 200
    assert second.status_code == 400
    assert "уже существует" in second.json()["detail"]


def test_create_indicator_invalid_type_rejected(client):
    response = client.post(
        "/knowledge/indicators",
        json={"name": "Показатель с ошибочным типом", "value_type": "integer"},
    )

    assert response.status_code == 400
    assert "numeric или categorical" in response.json()["detail"]


def test_create_possible_value_numeric_range_success(client):
    indicator_id = create_indicator(client, "Показатель возможного диапазона")

    response = client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )

    assert response.status_code == 200


def test_create_possible_value_numeric_scalar_rejected(client):
    indicator_id = item_id_by_name(client, "/knowledge/indicators", "CPU загрузка")

    response = client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "Текстовое значение"},
    )

    assert response.status_code == 400
    assert "разрешён только диапазон" in response.json()["detail"]


def test_create_possible_value_categorical_scalar_success(client):
    indicator_id = create_indicator(client, "Тестовый статус сервиса", "categorical")

    response = client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "Работает"},
    )

    assert response.status_code == 200


def test_create_possible_value_categorical_range_rejected(client):
    indicator_id = item_id_by_name(client, "/knowledge/indicators", "Сервисы состояние")

    response = client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )

    assert response.status_code == 400
    assert "только текстовое значение" in response.json()["detail"]


def test_create_normal_value_inside_possible_range_success(client):
    indicator_id = create_indicator(client, "Показатель нормального диапазона")
    client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )

    response = client.post(
        "/knowledge/normal-values",
        json={"indicator_id": indicator_id, "value_text": "[20;80]"},
    )

    assert response.status_code == 200
    assert response.json()["value_text"] == "[20;80]"


def test_create_normal_value_outside_possible_range_rejected(client):
    indicator_id = create_indicator(client, "Показатель нормального диапазона вне границ")
    client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )

    response = client.post(
        "/knowledge/normal-values",
        json={"indicator_id": indicator_id, "value_text": "[-10;80]"},
    )

    assert response.status_code == 400
    assert "возмож" in response.json()["detail"].lower()


def test_create_second_normal_value_for_indicator_rejected(client):
    indicator_id = create_indicator(client, "Показатель с одним нормальным значением")
    client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )
    first = client.post(
        "/knowledge/normal-values",
        json={"indicator_id": indicator_id, "value_text": "[10;20]"},
    )
    second = client.post(
        "/knowledge/normal-values",
        json={"indicator_id": indicator_id, "value_text": "[30;40]"},
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert "уже задано" in second.json()["detail"]


def test_create_severity_name_success(client):
    response = client.post("/knowledge/severity-names", json={"name": "Тестовая тяжесть"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Тестовая тяжесть"
    assert body["order_number"] > 0


def test_move_severity_name_invalid_direction_rejected(client):
    severity_id = item_id_by_name(client, "/knowledge/severity-names", "Оптимальное")

    response = client.post(
        f"/knowledge/severity-names/{severity_id}/move",
        json={"direction": "left"},
    )

    assert response.status_code == 400
    assert "up или down" in response.json()["detail"]


def test_replace_severity_values_inside_possible_range_success(client):
    indicator_id = create_indicator(client, "Показатель тяжести внутри диапазона")
    severity_id = item_id_by_name(client, "/knowledge/severity-names", "Оптимальное")
    client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )

    response = client.put(
        "/knowledge/severity-values",
        json={
            "severity_id": severity_id,
            "rows": [{"indicator_id": indicator_id, "value_text": "[0;30]"}],
        },
    )

    assert response.status_code == 200
    assert "обновлены" in response.json()["message"]


def test_replace_severity_values_outside_possible_range_rejected(client):
    indicator_id = create_indicator(client, "Показатель тяжести вне диапазона")
    severity_id = item_id_by_name(client, "/knowledge/severity-names", "Оптимальное")
    client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )

    response = client.put(
        "/knowledge/severity-values",
        json={
            "severity_id": severity_id,
            "rows": [{"indicator_id": indicator_id, "value_text": "[0;150]"}],
        },
    )

    assert response.status_code == 400
    assert "возмож" in response.json()["detail"].lower()


def test_create_diagnosis_success(client):
    response = client.post("/knowledge/diagnoses", json={"name": "Тестовый диагноз"})

    assert response.status_code == 200
    assert response.json()["name"] == "Тестовый диагноз"


def test_create_diagnosis_empty_name_rejected(client):
    response = client.post("/knowledge/diagnoses", json={"name": "   "})

    assert response.status_code == 400
    assert "не может быть пустым" in response.json()["detail"]


def test_replace_state_characteristics_success(client):
    diagnosis_id = create_diagnosis(client, "Диагноз с характеристиками")
    indicator_id = item_id_by_name(client, "/knowledge/indicators", "CPU загрузка")

    response = client.put(
        "/knowledge/state-characteristics",
        json={"diagnosis_id": diagnosis_id, "indicator_ids": [indicator_id]},
    )

    assert response.status_code == 200
    assert "обновлены" in response.json()["message"]

    get_response = client.get(
        "/knowledge/state-characteristics",
        params={"diagnosis_id": diagnosis_id},
    )
    assert get_response.status_code == 200
    assert get_response.json()["selected_indicator_ids"] == [indicator_id]


def test_replace_state_characteristics_unknown_diagnosis_rejected(client):
    indicator_id = item_id_by_name(client, "/knowledge/indicators", "CPU загрузка")

    response = client.put(
        "/knowledge/state-characteristics",
        json={"diagnosis_id": 999999, "indicator_ids": [indicator_id]},
    )

    assert response.status_code == 404
    assert "Диагноз не найден" in response.json()["detail"]


def test_replace_diagnosis_values_for_selected_indicator_success(client):
    diagnosis_id = create_diagnosis(client, "Диагноз со значениями")
    indicator_id = item_id_by_name(client, "/knowledge/indicators", "CPU загрузка")
    client.put(
        "/knowledge/state-characteristics",
        json={"diagnosis_id": diagnosis_id, "indicator_ids": [indicator_id]},
    )

    response = client.put(
        "/knowledge/diagnosis-values",
        json={
            "diagnosis_id": diagnosis_id,
            "rows": [{"indicator_id": indicator_id, "value_text": "(60;100]"}],
        },
    )

    assert response.status_code == 200
    assert "обновлены" in response.json()["message"]


def test_replace_diagnosis_values_for_not_selected_indicator_rejected(client):
    diagnosis_id = create_diagnosis(client, "Диагноз без нужного показателя")
    selected_indicator_id = item_id_by_name(client, "/knowledge/indicators", "CPU загрузка")
    not_selected_indicator_id = item_id_by_name(client, "/knowledge/indicators", "RAM занятость")
    client.put(
        "/knowledge/state-characteristics",
        json={"diagnosis_id": diagnosis_id, "indicator_ids": [selected_indicator_id]},
    )

    response = client.put(
        "/knowledge/diagnosis-values",
        json={
            "diagnosis_id": diagnosis_id,
            "rows": [{"indicator_id": not_selected_indicator_id, "value_text": "(70;100]"}],
        },
    )

    assert response.status_code == 400
    assert "не выбран" in response.json()["detail"]


def test_replace_diagnosis_values_outside_possible_range_rejected(client):
    diagnosis_id = create_diagnosis(client, "Диагноз со значением вне диапазона")
    indicator_id = create_indicator(client, "Показатель диагноза вне диапазона")
    client.post(
        "/knowledge/possible-values",
        json={"indicator_id": indicator_id, "value_text": "[0;100]"},
    )
    client.put(
        "/knowledge/state-characteristics",
        json={"diagnosis_id": diagnosis_id, "indicator_ids": [indicator_id]},
    )

    response = client.put(
        "/knowledge/diagnosis-values",
        json={
            "diagnosis_id": diagnosis_id,
            "rows": [{"indicator_id": indicator_id, "value_text": "(80;150]"}],
        },
    )

    assert response.status_code == 400
    assert "возмож" in response.json()["detail"].lower()


def test_monitoring_evaluate_complete_input_uses_expert_result(client):
    response = client.post(
        "/monitoring/evaluate",
        json={
            "cpu_load": 20,
            "ram_usage": 35,
            "cpu_temp": 45,
            "disk_speed": 150,
            "disk_fill": 40,
            "network_bandwidth": 3000,
            "process_count": 80,
            "service_state": "Все работают",
            "previous_state": None,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "expert_and_ml"
    assert body["final_source"] == "expert"
    assert body["final_state"] == "Оптимальное"
    assert body["diagnosis"] == "Исправен"
    assert body["missing_indicators"] == []


def test_monitoring_evaluate_partial_input_uses_ml_result(client):
    response = client.post(
        "/monitoring/evaluate",
        json={
            "cpu_load": 95,
            "service_state": "Критический сервис остановлен",
            "previous_state": "Оптимальное",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "expert_and_ml"
    assert body["final_source"] == "ml"
    assert body["final_state"] == "Критическое с риском отказа"
    assert "RAM занятость" in body["missing_indicators"]
    assert body["raw_input"]["ram_usage"] is None


def test_monitoring_evaluate_empty_payload_rejected(client):
    response = client.post("/monitoring/evaluate", json={})

    assert response.status_code == 400
    assert "хотя бы один показатель" in response.json()["detail"]


def test_monitoring_evaluate_invalid_service_state_rejected(client):
    response = client.post(
        "/monitoring/evaluate",
        json={"service_state": "Некорректное состояние"},
    )

    assert response.status_code == 422


def test_create_observation_success(client):
    response = client.post("/observations", json=observation_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["id"] > 0
    assert body["input"]["cpu_load"] == 20
    assert body["result"]["diagnosis"] == "Исправен"


def test_list_observations_contains_created_item(client):
    created_id = create_observation(client)

    response = client.get("/observations")

    assert response.status_code == 200
    items = response.json()
    assert any(item["id"] == created_id for item in items)


def test_get_observation_by_id_success(client):
    created_id = create_observation(client)

    response = client.get(f"/observations/{created_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created_id
    assert body["result"]["final_state"] == "Оптимальное"


def test_get_observation_diagnosis_success(client):
    created_id = create_observation(client)

    response = client.get(f"/observations/{created_id}/diagnosis")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created_id
    assert body["diagnosis"] == "Исправен"
    assert body["explanation"] == "Тестовое сохранение результата мониторинга."


def test_get_observation_not_found_rejected(client):
    response = client.get("/observations/999999")

    assert response.status_code == 404
    assert "Наблюдение не найдено" in response.json()["detail"]
