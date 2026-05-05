from typing import Any

from sqlalchemy.orm import Session

from app.models.indicator import Indicator
from app.models.severity_name import SeverityName
from app.models.severity_value import SeverityValue


class ExpertSolver:
    def __init__(self, db: Session):
        self.db = db
    def _get_default_payload(self) -> dict[str, Any]:
        return {
            "cpu_load": 20,
            "ram_usage": 35,
            "cpu_temp": 45,
            "disk_speed": 150,
            "disk_fill": 40,
            "network_bandwidth": 3000,
            "process_count": 80,
            "service_state": "Все работают",
        }
    def _match_rule(self, value: Any, rule: SeverityValue) -> bool:
        if rule.value_kind == "scalar":
            return str(value) == str(rule.scalar_value)

        if rule.value_kind == "range":
            if not isinstance(value, (int, float)):
                return False

            lower_ok = True
            upper_ok = True

            if rule.min_value is not None:
                if rule.min_inclusive:
                    lower_ok = value >= rule.min_value
                else:
                    lower_ok = value > rule.min_value

            if rule.max_value is not None:
                if rule.max_inclusive:
                    upper_ok = value <= rule.max_value
                else:
                    upper_ok = value < rule.max_value

            return lower_ok and upper_ok

        return False

    def _get_indicator_by_name(self, name: str) -> Indicator | None:
        return self.db.query(Indicator).filter(Indicator.name == name).first()

    def _get_severity_order_map(self) -> dict[str, int]:
        rows = self.db.query(SeverityName).all()
        return {row.name: row.order_number for row in rows}

    def detect_indicator_severity(self, indicator_name: str, value: Any) -> dict[str, Any]:
        indicator = self._get_indicator_by_name(indicator_name)
        if indicator is None:
            raise ValueError(f"Показатель '{indicator_name}' не найден в базе знаний")

        rules = (
            self.db.query(SeverityValue, SeverityName)
            .join(SeverityName, SeverityValue.severity_name_id == SeverityName.id)
            .filter(SeverityValue.indicator_id == indicator.id)
            .all()
        )

        for rule, severity in rules:
            if self._match_rule(value, rule):
                return {
                    "indicator": indicator_name,
                    "value": value,
                    "severity": severity.name,
                    "severity_order": severity.order_number,
                }

        raise ValueError(
            f"Для показателя '{indicator_name}' не найдено правило, "
            f"подходящее для значения '{value}'"
        )

    def detect_final_state(self, indicator_results: list[dict[str, Any]]) -> str:
        worst = max(indicator_results, key=lambda item: item["severity_order"])
        return worst["severity"]

    def detect_dynamics(self, current_state: str, previous_state: str | None) -> str | None:
        if previous_state is None:
            return None

        order_map = self._get_severity_order_map()

        if previous_state not in order_map:
            raise ValueError(f"Неизвестное предыдущее состояние: {previous_state}")

        current_order = order_map[current_state]
        previous_order = order_map[previous_state]

        if current_order > previous_order:
            return "Ухудшение"
        if current_order < previous_order:
            return "Улучшение"
        return "Стабильно"

    def detect_diagnosis(self, final_state: str, dynamics: str | None) -> str:
        if final_state in {"Критическое", "Критическое с риском отказа"}:
            return "Требует обслуживания"

        if dynamics == "Ухудшение":
            return "Требует обслуживания"

        return "Исправен"

    def build_explanation(
        self,
        indicator_results: list[dict[str, Any]],
        final_state: str,
        dynamics: str | None,
        diagnosis: str,
        missing_indicators: list[str],
    ) -> str:
        worst = max(indicator_results, key=lambda item: item["severity_order"])

        explanation = (
            f"Итоговая степень тяжести состояния определена как '{final_state}', "
            f"так как наиболее тяжёлым оказался показатель '{worst['indicator']}' "
            f"со значением '{worst['value']}', которому соответствует состояние "
            f"'{worst['severity']}'. "
        )

        if missing_indicators:
            explanation += (
                "Часть показателей не была введена пользователем. "
                "Для этих показателей экспертная система использовала допущение "
                "об их оптимальном состоянии: "
                + ", ".join(missing_indicators)
                + ". "
            )

        if dynamics is not None:
            explanation += f"Динамика состояния компьютера определена как '{dynamics}'. "

        explanation += f"Итоговый диагноз: '{diagnosis}'."
        return explanation

    def evaluate(self, payload: dict[str, Any]) -> dict[str, Any]:
        defaults = self._get_default_payload()

        source_to_indicator = {
            "cpu_load": "CPU загрузка",
            "ram_usage": "RAM занятость",
            "cpu_temp": "CPU температура",
            "disk_speed": "Диск скорость",
            "disk_fill": "Диск заполнение",
            "network_bandwidth": "Сеть пропускная",
            "process_count": "Процессы количество",
            "service_state": "Сервисы состояние",
        }

        resolved_input: dict[str, Any] = {}
        missing_indicators: list[str] = []

        for source_key, indicator_name in source_to_indicator.items():
            if payload.get(source_key) is None:
                resolved_input[source_key] = defaults[source_key]
                missing_indicators.append(indicator_name)
            else:
                resolved_input[source_key] = payload[source_key]

        indicators_map = {
            "CPU загрузка": resolved_input["cpu_load"],
            "RAM занятость": resolved_input["ram_usage"],
            "CPU температура": resolved_input["cpu_temp"],
            "Диск скорость": resolved_input["disk_speed"],
            "Диск заполнение": resolved_input["disk_fill"],
            "Сеть пропускная": resolved_input["network_bandwidth"],
            "Процессы количество": resolved_input["process_count"],
            "Сервисы состояние": resolved_input["service_state"],
        }

        indicator_results = []
        for indicator_name, value in indicators_map.items():
            indicator_results.append(self.detect_indicator_severity(indicator_name, value))

        final_state = self.detect_final_state(indicator_results)
        dynamics = self.detect_dynamics(final_state, payload.get("previous_state"))
        diagnosis = self.detect_diagnosis(final_state, dynamics)

        explanation = self.build_explanation(
            indicator_results=indicator_results,
            final_state=final_state,
            dynamics=dynamics,
            diagnosis=diagnosis,
            missing_indicators=missing_indicators,
        )

        return {
            "indicator_results": indicator_results,
            "final_state": final_state,
            "dynamics": dynamics,
            "diagnosis": diagnosis,
            "explanation": explanation,
            "missing_indicators": missing_indicators,
            "resolved_input": {
                **resolved_input,
                "previous_state": payload.get("previous_state"),
            },
        }