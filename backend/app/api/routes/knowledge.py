from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.diagnosis import Diagnosis
from app.models.diagnosis_value import DiagnosisValue
from app.models.indicator import Indicator
from app.models.normal_value import NormalValue
from app.models.possible_value import PossibleValue
from app.models.severity_name import SeverityName
from app.models.severity_value import SeverityValue
from app.models.state_characteristic import StateCharacteristic

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# =========================
# Pydantic payloads
# =========================

class NamePayload(BaseModel):
    name: str

class IndicatorPayload(BaseModel):
    name: str
    value_type: str

class ValueTextPayload(BaseModel):
    indicator_id: int
    value_text: str


class StateCharacteristicPayload(BaseModel):
    diagnosis_id: int
    indicator_ids: list[int]


class RuleRowPayload(BaseModel):
    indicator_id: int
    value_text: str


class SeverityValuesPayload(BaseModel):
    severity_id: int
    rows: list[RuleRowPayload]


class DiagnosisValuesPayload(BaseModel):
    diagnosis_id: int
    rows: list[RuleRowPayload]


# =========================
# Helpers
# =========================

def normalize_name(name: str) -> str:
    return name.strip()

def normalize_indicator_type(value_type: str) -> str:
    value = value_type.strip().lower()

    if value not in {"numeric", "categorical"}:
        raise HTTPException(
            status_code=400,
            detail="Тип показателя должен быть numeric или categorical",
        )

    return value

def validate_parsed_value_for_indicator(indicator: Indicator, parsed: dict):
    if indicator.value_type == "numeric" and parsed["value_kind"] != "range":
        raise HTTPException(
            status_code=400,
            detail=f'Для показателя "{indicator.name}" разрешён только диапазон',
        )

    if indicator.value_type == "categorical" and parsed["value_kind"] != "scalar":
        raise HTTPException(
            status_code=400,
            detail=f'Для показателя "{indicator.name}" разрешено только текстовое значение',
        )

def float_to_text(value: float | None) -> str:
    if value is None:
        return ""
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def format_value(value_kind: str, min_value, max_value, min_inclusive, max_inclusive, scalar_value) -> str:
    if value_kind == "scalar":
        return scalar_value or ""

    left = "[" if min_inclusive else "("
    right = "]" if max_inclusive else ")"
    return f"{left}{float_to_text(min_value)};{float_to_text(max_value)}{right}"


def parse_value_text(value_text: str) -> dict:
    text = value_text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Значение не может быть пустым")

    # Интервал вида [0;30], (30;60], [50;80), ...
    if (
        len(text) >= 5
        and text[0] in "[("
        and text[-1] in "])"
        and ";" in text
    ):
        inner = text[1:-1]
        parts = inner.split(";")
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail=f"Некорректный интервал: {text}")

        try:
            min_value = float(parts[0].replace(",", ".").strip())
            max_value = float(parts[1].replace(",", ".").strip())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Некорректные числа в интервале: {text}")

        return {
            "value_kind": "range",
            "min_value": min_value,
            "max_value": max_value,
            "min_inclusive": text[0] == "[",
            "max_inclusive": text[-1] == "]",
            "scalar_value": None,
        }

    # Иначе считаем это скалярным значением
    return {
        "value_kind": "scalar",
        "min_value": None,
        "max_value": None,
        "min_inclusive": True,
        "max_inclusive": True,
        "scalar_value": text,
    }


def get_state_characteristic_map(db: Session, diagnosis_id: int) -> dict[int, int]:
    rows = db.query(StateCharacteristic).filter(StateCharacteristic.diagnosis_id == diagnosis_id).all()
    return {row.indicator_id: row.id for row in rows}


# =========================
# Seed endpoints
# =========================

@router.post("/seed-basic")
def seed_basic_knowledge(db: Session = Depends(get_db)):
    indicator_names = [
        ("CPU загрузка", "numeric"),
        ("RAM занятость", "numeric"),
        ("CPU температура", "numeric"),
        ("Диск скорость", "numeric"),
        ("Диск заполнение", "numeric"),
        ("Сеть пропускная", "numeric"),
        ("Процессы количество", "numeric"),
        ("Сервисы состояние", "categorical"),
    ]

    diagnosis_names = [
        "Исправен",
        "Требует обслуживания",
    ]

    severity_names = [
        ("Оптимальное", 1),
        ("Хорошее", 2),
        ("Критическое", 3),
        ("Критическое с риском отказа", 4),
    ]

    for name, value_type in indicator_names:
        name = normalize_name(name)
        value_type = normalize_indicator_type(value_type)

        exists = db.query(Indicator).filter(Indicator.name == name).first()
        if not exists:
            db.add(Indicator(name=name, value_type=value_type))

    for name in diagnosis_names:
        name = normalize_name(name)
        exists = db.query(Diagnosis).filter(Diagnosis.name == name).first()
        if not exists:
            db.add(Diagnosis(name=name))

    for name, order_number in severity_names:
        name = normalize_name(name)
        exists = db.query(SeverityName).filter(SeverityName.name == name).first()
        if not exists:
            db.add(SeverityName(name=name, order_number=order_number))

    db.commit()
    return {"message": "Базовые знания успешно добавлены"}


@router.post("/seed-rules")
def seed_rules(db: Session = Depends(get_db)):
    indicators = {x.name: x.id for x in db.query(Indicator).all()}
    diagnoses = {x.name: x.id for x in db.query(Diagnosis).all()}
    severities = {x.name: x.id for x in db.query(SeverityName).all()}

    if not indicators or not diagnoses or not severities:
        raise HTTPException(
            status_code=400,
            detail="Сначала вызови /knowledge/seed-basic",
        )

    def add_if_not_exists(model, **kwargs):
        exists = db.query(model).filter_by(**kwargs).first()
        if not exists:
            db.add(model(**kwargs))

    # possible_value
    range_possible = {
        "CPU загрузка": (0, 100),
        "RAM занятость": (0, 100),
        "CPU температура": (20, 120),
        "Диск скорость": (0, 1000),
        "Диск заполнение": (0, 100),
        "Сеть пропускная": (0, 10000),
        "Процессы количество": (0, 1000),
    }

    for indicator_name, (min_v, max_v) in range_possible.items():
        add_if_not_exists(
            PossibleValue,
            indicator_id=indicators[indicator_name],
            value_kind="range",
            min_value=min_v,
            max_value=max_v,
            min_inclusive=True,
            max_inclusive=True,
            scalar_value=None,
        )

    for scalar in [
        "Все работают",
        "Некоторые остановлены",
        "Критический сервис остановлен",
    ]:
        add_if_not_exists(
            PossibleValue,
            indicator_id=indicators["Сервисы состояние"],
            value_kind="scalar",
            min_value=None,
            max_value=None,
            min_inclusive=True,
            max_inclusive=True,
            scalar_value=scalar,
        )

    # normal_value
    normal_ranges = {
        "CPU загрузка": (0, 30),
        "RAM занятость": (0, 40),
        "CPU температура": (20, 60),
        "Диск скорость": (100, 1000),
        "Диск заполнение": (0, 70),
        "Сеть пропускная": (0, 8000),
        "Процессы количество": (30, 200),
    }

    for indicator_name, (min_v, max_v) in normal_ranges.items():
        add_if_not_exists(
            NormalValue,
            indicator_id=indicators[indicator_name],
            value_kind="range",
            min_value=min_v,
            max_value=max_v,
            min_inclusive=True,
            max_inclusive=True,
            scalar_value=None,
        )

    add_if_not_exists(
        NormalValue,
        indicator_id=indicators["Сервисы состояние"],
        value_kind="scalar",
        min_value=None,
        max_value=None,
        min_inclusive=True,
        max_inclusive=True,
        scalar_value="Все работают",
    )

    # severity_value
    severity_rules = [
        ("CPU загрузка", "Оптимальное", "range", 0, 30, True, True, None),
        ("CPU загрузка", "Хорошее", "range", 30, 60, False, True, None),
        ("CPU загрузка", "Критическое", "range", 60, 90, False, True, None),
        ("CPU загрузка", "Критическое с риском отказа", "range", 90, 100, False, True, None),

        ("RAM занятость", "Оптимальное", "range", 0, 40, True, True, None),
        ("RAM занятость", "Хорошее", "range", 40, 70, False, True, None),
        ("RAM занятость", "Критическое", "range", 70, 95, False, True, None),
        ("RAM занятость", "Критическое с риском отказа", "range", 95, 100, False, True, None),

        ("CPU температура", "Оптимальное", "range", 20, 50, True, True, None),
        ("CPU температура", "Хорошее", "range", 50, 75, False, True, None),
        ("CPU температура", "Критическое", "range", 75, 100, False, True, None),
        ("CPU температура", "Критическое с риском отказа", "range", 100, 120, False, True, None),

        ("Диск заполнение", "Оптимальное", "range", 0, 70, True, True, None),
        ("Диск заполнение", "Хорошее", "range", 70, 85, False, True, None),
        ("Диск заполнение", "Критическое", "range", 85, 98, False, True, None),
        ("Диск заполнение", "Критическое с риском отказа", "range", 98, 100, False, True, None),

        ("Диск скорость", "Оптимальное", "range", 80, 1000, True, True, None),
        ("Диск скорость", "Хорошее", "range", 50, 80, True, False, None),
        ("Диск скорость", "Критическое", "range", 10, 50, True, False, None),
        ("Диск скорость", "Критическое с риском отказа", "range", 0, 10, True, False, None),

        ("Сеть пропускная", "Оптимальное", "range", 0, 8000, True, True, None),
        ("Сеть пропускная", "Хорошее", "range", 8000, 9000, False, True, None),
        ("Сеть пропускная", "Критическое", "range", 9000, 10000, False, True, None),

        ("Процессы количество", "Оптимальное", "range", 30, 100, True, True, None),
        ("Процессы количество", "Хорошее", "range", 100, 200, False, True, None),
        ("Процессы количество", "Критическое", "range", 200, 500, False, True, None),
        ("Процессы количество", "Критическое с риском отказа", "range", 500, 1000, False, True, None),
        ("Процессы количество", "Критическое с риском отказа", "range", 0, 10, True, False, None),
    ]

    for indicator_name, severity_name, kind, min_v, max_v, min_inc, max_inc, scalar in severity_rules:
        add_if_not_exists(
            SeverityValue,
            indicator_id=indicators[indicator_name],
            severity_name_id=severities[severity_name],
            value_kind=kind,
            min_value=min_v,
            max_value=max_v,
            min_inclusive=min_inc,
            max_inclusive=max_inc,
            scalar_value=scalar,
        )

    for severity_name, scalar in [
        ("Оптимальное", "Все работают"),
        ("Критическое", "Некоторые остановлены"),
        ("Критическое с риском отказа", "Критический сервис остановлен"),
    ]:
        add_if_not_exists(
            SeverityValue,
            indicator_id=indicators["Сервисы состояние"],
            severity_name_id=severities[severity_name],
            value_kind="scalar",
            min_value=None,
            max_value=None,
            min_inclusive=True,
            max_inclusive=True,
            scalar_value=scalar,
        )

    db.commit()

    # characteristics + diagnosis values
    diagnosis_id = diagnoses["Требует обслуживания"]
    characteristic_indicators = [
        "CPU загрузка",
        "RAM занятость",
        "CPU температура",
        "Диск скорость",
        "Диск заполнение",
        "Сеть пропускная",
        "Процессы количество",
        "Сервисы состояние",
    ]

    for indicator_name in characteristic_indicators:
        exists = (
            db.query(StateCharacteristic)
            .filter_by(diagnosis_id=diagnosis_id, indicator_id=indicators[indicator_name])
            .first()
        )
        if not exists:
            db.add(
                StateCharacteristic(
                    diagnosis_id=diagnosis_id,
                    indicator_id=indicators[indicator_name],
                )
            )

    db.commit()

    state_map = get_state_characteristic_map(db, diagnosis_id)

    diagnosis_range_rules = [
        ("CPU загрузка", 60, 100, False, True),
        ("RAM занятость", 70, 100, False, True),
        ("CPU температура", 75, 120, False, True),
        ("Диск скорость", 0, 50, True, False),
        ("Диск заполнение", 85, 100, False, True),
        ("Сеть пропускная", 9000, 10000, False, True),
        ("Процессы количество", 200, 1000, False, True),
    ]

    for indicator_name, min_v, max_v, min_inc, max_inc in diagnosis_range_rules:
        add_if_not_exists(
            DiagnosisValue,
            state_characteristic_id=state_map[indicators[indicator_name]],
            value_kind="range",
            min_value=min_v,
            max_value=max_v,
            min_inclusive=min_inc,
            max_inclusive=max_inc,
            scalar_value=None,
        )

    for scalar in ["Некоторые остановлены", "Критический сервис остановлен"]:
        add_if_not_exists(
            DiagnosisValue,
            state_characteristic_id=state_map[indicators["Сервисы состояние"]],
            value_kind="scalar",
            min_value=None,
            max_value=None,
            min_inclusive=True,
            max_inclusive=True,
            scalar_value=scalar,
        )

    db.commit()
    return {"message": "Правила успешно добавлены"}


# =========================
# CRUD: Diagnoses
# =========================

@router.get("/diagnoses")
def get_diagnoses(db: Session = Depends(get_db)):
    rows = db.query(Diagnosis).order_by(Diagnosis.id).all()
    return [{"id": x.id, "name": x.name} for x in rows]


@router.post("/diagnoses")
def create_diagnosis(payload: NamePayload, db: Session = Depends(get_db)):
    name = normalize_name(payload.name)
    if not name:
        raise HTTPException(status_code=400, detail="Название диагноза не может быть пустым")

    exists = db.query(Diagnosis).filter(Diagnosis.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Такой диагноз уже существует")

    item = Diagnosis(name=name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name}


@router.delete("/diagnoses/{diagnosis_id}")
def delete_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Диагноз не найден")

    state_rows = db.query(StateCharacteristic).filter(StateCharacteristic.diagnosis_id == diagnosis_id).all()
    state_ids = [x.id for x in state_rows]

    if state_ids:
        db.query(DiagnosisValue).filter(DiagnosisValue.state_characteristic_id.in_(state_ids)).delete(synchronize_session=False)

    db.query(StateCharacteristic).filter(StateCharacteristic.diagnosis_id == diagnosis_id).delete(synchronize_session=False)
    db.delete(diagnosis)
    db.commit()

    return {"message": "Диагноз удалён"}


# =========================
# CRUD: Indicators
# =========================

@router.get("/indicators")
def get_indicators(db: Session = Depends(get_db)):
    rows = db.query(Indicator).order_by(Indicator.id).all()
    return [
        {
            "id": x.id,
            "name": x.name,
            "value_type": x.value_type,
        }
        for x in rows
    ]


@router.post("/indicators")
def create_indicator(payload: IndicatorPayload, db: Session = Depends(get_db)):
    name = normalize_name(payload.name)
    value_type = normalize_indicator_type(payload.value_type)

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Название показателя не может быть пустым",
        )

    exists = db.query(Indicator).filter(Indicator.name == name).first()
    if exists:
        raise HTTPException(
            status_code=400,
            detail="Такой показатель уже существует",
        )

    item = Indicator(name=name, value_type=value_type)
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "name": item.name,
        "value_type": item.value_type,
    }


@router.delete("/indicators/{indicator_id}")
def delete_indicator(indicator_id: int, db: Session = Depends(get_db)):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Показатель не найден")

    state_rows = db.query(StateCharacteristic).filter(StateCharacteristic.indicator_id == indicator_id).all()
    state_ids = [x.id for x in state_rows]

    if state_ids:
        db.query(DiagnosisValue).filter(DiagnosisValue.state_characteristic_id.in_(state_ids)).delete(synchronize_session=False)

    db.query(PossibleValue).filter(PossibleValue.indicator_id == indicator_id).delete(synchronize_session=False)
    db.query(NormalValue).filter(NormalValue.indicator_id == indicator_id).delete(synchronize_session=False)
    db.query(SeverityValue).filter(SeverityValue.indicator_id == indicator_id).delete(synchronize_session=False)
    db.query(StateCharacteristic).filter(StateCharacteristic.indicator_id == indicator_id).delete(synchronize_session=False)

    db.delete(indicator)
    db.commit()

    return {"message": "Показатель удалён"}


# =========================
# CRUD: Severity names
# =========================

@router.get("/severity-names")
def get_severity_names(db: Session = Depends(get_db)):
    rows = db.query(SeverityName).order_by(SeverityName.order_number).all()
    return [{"id": x.id, "name": x.name, "order_number": x.order_number} for x in rows]


@router.post("/severity-names")
def create_severity_name(payload: NamePayload, db: Session = Depends(get_db)):
    name = normalize_name(payload.name)
    if not name:
        raise HTTPException(status_code=400, detail="Название степени тяжести не может быть пустым")

    exists = db.query(SeverityName).filter(SeverityName.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Такая степень тяжести уже существует")

    max_order = db.query(SeverityName).count() + 1
    item = SeverityName(name=name, order_number=max_order)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "order_number": item.order_number}


@router.delete("/severity-names/{severity_id}")
def delete_severity_name(severity_id: int, db: Session = Depends(get_db)):
    severity = db.query(SeverityName).filter(SeverityName.id == severity_id).first()
    if not severity:
        raise HTTPException(status_code=404, detail="Степень тяжести не найдена")

    db.query(SeverityValue).filter(SeverityValue.severity_name_id == severity_id).delete(synchronize_session=False)
    db.delete(severity)
    db.commit()

    return {"message": "Степень тяжести удалена"}


# =========================
# CRUD: Possible values
# =========================

@router.get("/possible-values")
def get_possible_values(
    indicator_id: int = Query(...),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PossibleValue)
        .filter(PossibleValue.indicator_id == indicator_id)
        .order_by(PossibleValue.id)
        .all()
    )

    return [
        {
            "id": x.id,
            "indicator_id": x.indicator_id,
            "value_text": format_value(
                x.value_kind, x.min_value, x.max_value,
                x.min_inclusive, x.max_inclusive, x.scalar_value
            ),
        }
        for x in rows
    ]


@router.post("/possible-values")
def create_possible_value(payload: ValueTextPayload, db: Session = Depends(get_db)):
    indicator = db.query(Indicator).filter(Indicator.id == payload.indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Показатель не найден")

    parsed = parse_value_text(payload.value_text)
    validate_parsed_value_for_indicator(indicator, parsed)

    item = PossibleValue(
        indicator_id=payload.indicator_id,
        **parsed,
    )


@router.delete("/possible-values/{value_id}")
def delete_possible_value(value_id: int, db: Session = Depends(get_db)):
    row = db.query(PossibleValue).filter(PossibleValue.id == value_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Возможное значение не найдено")

    db.delete(row)
    db.commit()
    return {"message": "Возможное значение удалено"}


# =========================
# CRUD: Normal values
# =========================

@router.get("/normal-values")
def get_normal_values(
    indicator_id: int = Query(...),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(NormalValue)
        .filter(NormalValue.indicator_id == indicator_id)
        .order_by(NormalValue.id)
        .all()
    )

    return [
        {
            "id": x.id,
            "indicator_id": x.indicator_id,
            "value_text": format_value(
                x.value_kind, x.min_value, x.max_value,
                x.min_inclusive, x.max_inclusive, x.scalar_value
            ),
        }
        for x in rows
    ]


@router.post("/normal-values")
def create_normal_value(payload: ValueTextPayload, db: Session = Depends(get_db)):
    indicator = db.query(Indicator).filter(Indicator.id == payload.indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Показатель не найден")

    parsed = parse_value_text(payload.value_text)
    validate_parsed_value_for_indicator(indicator, parsed)

    item = NormalValue(
        indicator_id=payload.indicator_id,
        **parsed,
    )


@router.delete("/normal-values/{value_id}")
def delete_normal_value(value_id: int, db: Session = Depends(get_db)):
    row = db.query(NormalValue).filter(NormalValue.id == value_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Нормальное значение не найдено")

    db.delete(row)
    db.commit()
    return {"message": "Нормальное значение удалено"}


# =========================
# State characteristics
# =========================

@router.get("/state-characteristics")
def get_state_characteristics(
    diagnosis_id: int = Query(...),
    db: Session = Depends(get_db),
):
    selected_ids = (
        db.query(StateCharacteristic.indicator_id)
        .filter(StateCharacteristic.diagnosis_id == diagnosis_id)
        .all()
    )

    return {
        "diagnosis_id": diagnosis_id,
        "selected_indicator_ids": [x[0] for x in selected_ids],
    }


@router.put("/state-characteristics")
def replace_state_characteristics(payload: StateCharacteristicPayload, db: Session = Depends(get_db)):
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == payload.diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Диагноз не найден")

    current_rows = db.query(StateCharacteristic).filter(
        StateCharacteristic.diagnosis_id == payload.diagnosis_id
    ).all()
    current_ids = [x.id for x in current_rows]

    if current_ids:
        db.query(DiagnosisValue).filter(DiagnosisValue.state_characteristic_id.in_(current_ids)).delete(
            synchronize_session=False
        )

    db.query(StateCharacteristic).filter(
        StateCharacteristic.diagnosis_id == payload.diagnosis_id
    ).delete(synchronize_session=False)

    for indicator_id in payload.indicator_ids:
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if indicator:
            db.add(
                StateCharacteristic(
                    diagnosis_id=payload.diagnosis_id,
                    indicator_id=indicator_id,
                )
            )

    db.commit()
    return {"message": "Характеристики состояния обновлены"}


# =========================
# Severity values by severity
# =========================

@router.get("/severity-values")
def get_severity_values(
    severity_id: int = Query(...),
    db: Session = Depends(get_db),
):
    indicators = db.query(Indicator).order_by(Indicator.id).all()
    rows = []

    for indicator in indicators:
        value = (
            db.query(SeverityValue)
            .filter(
                SeverityValue.severity_name_id == severity_id,
                SeverityValue.indicator_id == indicator.id,
            )
            .first()
        )

        rows.append(
            {
                "indicator_id": indicator.id,
                "indicator_name": indicator.name,
                "indicator_value_type": indicator.value_type,
                "value_text": format_value(
                    value.value_kind,
                    value.min_value,
                    value.max_value,
                    value.min_inclusive,
                    value.max_inclusive,
                    value.scalar_value,
                ) if value else "",
            }
        )

    return {"severity_id": severity_id, "rows": rows}


@router.put("/severity-values")
def replace_severity_values(payload: SeverityValuesPayload, db: Session = Depends(get_db)):
    severity = db.query(SeverityName).filter(SeverityName.id == payload.severity_id).first()
    if not severity:
        raise HTTPException(status_code=404, detail="Степень тяжести не найдена")

    db.query(SeverityValue).filter(
        SeverityValue.severity_name_id == payload.severity_id
    ).delete(synchronize_session=False)

    for row in payload.rows:
        value_text = row.value_text.strip()
        if not value_text:
            continue

        indicator = db.query(Indicator).filter(Indicator.id == row.indicator_id).first()
        if not indicator:
            continue

        parsed = parse_value_text(value_text)
        validate_parsed_value_for_indicator(indicator, parsed)

        db.add(
            SeverityValue(
                indicator_id=row.indicator_id,
                severity_name_id=payload.severity_id,
                **parsed,
            )
        )

    db.commit()
    return {"message": "Значения показателей степени тяжести обновлены"}


# =========================
# Diagnosis values by diagnosis
# =========================

@router.get("/diagnosis-values")
def get_diagnosis_values(
    diagnosis_id: int = Query(...),
    db: Session = Depends(get_db),
):
    state_map = get_state_characteristic_map(db, diagnosis_id)
    selected_indicator_ids = list(state_map.keys())

    if not selected_indicator_ids:
        return {"diagnosis_id": diagnosis_id, "rows": []}

    indicators = (
        db.query(Indicator)
        .filter(Indicator.id.in_(selected_indicator_ids))
        .order_by(Indicator.id)
        .all()
    )

    rows = []
    for indicator in indicators:
        value_text = ""

        value = (
            db.query(DiagnosisValue)
            .filter(DiagnosisValue.state_characteristic_id == state_map[indicator.id])
            .first()
        )
        if value:
            value_text = format_value(
                value.value_kind,
                value.min_value,
                value.max_value,
                value.min_inclusive,
                value.max_inclusive,
                value.scalar_value,
            )

        rows.append(
            {
                "indicator_id": indicator.id,
                "indicator_name": indicator.name,
                "indicator_value_type": indicator.value_type,
                "value_text": value_text,
            }
        )

    return {"diagnosis_id": diagnosis_id, "rows": rows}


@router.put("/diagnosis-values")
def replace_diagnosis_values(payload: DiagnosisValuesPayload, db: Session = Depends(get_db)):
    diagnosis = db.query(Diagnosis).filter(Diagnosis.id == payload.diagnosis_id).first()
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Диагноз не найден")

    state_map = get_state_characteristic_map(db, payload.diagnosis_id)

    used_state_ids = list(state_map.values())
    if used_state_ids:
        db.query(DiagnosisValue).filter(
            DiagnosisValue.state_characteristic_id.in_(used_state_ids)
        ).delete(synchronize_session=False)

    for row in payload.rows:
        value_text = row.value_text.strip()
        if not value_text:
            continue

        if row.indicator_id not in state_map:
            raise HTTPException(
                status_code=400,
                detail="Нельзя задать правило для показателя, который не выбран в характеристиках состояния",
            )

        indicator = db.query(Indicator).filter(Indicator.id == row.indicator_id).first()
        if not indicator:
            continue

        parsed = parse_value_text(value_text)
        validate_parsed_value_for_indicator(indicator, parsed)

        db.add(
            DiagnosisValue(
                state_characteristic_id=state_map[row.indicator_id],
                **parsed,
            )
        )

    db.commit()
    return {"message": "Значения показателей диагноза обновлены"}