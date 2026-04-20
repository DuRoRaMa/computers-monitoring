import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.observation import Observation

router = APIRouter(prefix="/observations", tags=["observations"])


class IndicatorResultPayload(BaseModel):
    indicator: str
    value: str
    severity: str


class ObservationCreatePayload(BaseModel):
    cpu_load: float
    ram_usage: float
    cpu_temp: float
    disk_speed: float
    disk_fill: float
    network_bandwidth: float
    process_count: float
    service_state: str
    previous_state: str | None = None

    final_state: str
    dynamics: str | None = None
    diagnosis: str
    explanation: str

    indicator_results: list[IndicatorResultPayload]


def serialize_observation(item: Observation):
    return {
        "id": item.id,
        "created_at": item.created_at.isoformat(),
        "input": {
            "cpu_load": item.cpu_load,
            "ram_usage": item.ram_usage,
            "cpu_temp": item.cpu_temp,
            "disk_speed": item.disk_speed,
            "disk_fill": item.disk_fill,
            "network_bandwidth": item.network_bandwidth,
            "process_count": item.process_count,
            "service_state": item.service_state,
            "previous_state": item.previous_state,
        },
        "result": {
            "final_state": item.final_state,
            "dynamics": item.dynamics,
            "diagnosis": item.diagnosis,
            "explanation": item.explanation,
            "indicator_results": json.loads(item.indicator_results_json),
        },
    }


@router.post("")
def create_observation(payload: ObservationCreatePayload, db: Session = Depends(get_db)):
    item = Observation(
        cpu_load=payload.cpu_load,
        ram_usage=payload.ram_usage,
        cpu_temp=payload.cpu_temp,
        disk_speed=payload.disk_speed,
        disk_fill=payload.disk_fill,
        network_bandwidth=payload.network_bandwidth,
        process_count=payload.process_count,
        service_state=payload.service_state,
        previous_state=payload.previous_state,

        final_state=payload.final_state,
        dynamics=payload.dynamics,
        diagnosis=payload.diagnosis,
        explanation=payload.explanation,
        indicator_results_json=json.dumps(
            [x.model_dump() for x in payload.indicator_results],
            ensure_ascii=False
        ),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return serialize_observation(item)


@router.get("")
def list_observations(db: Session = Depends(get_db)):
    rows = db.query(Observation).order_by(Observation.created_at.desc()).all()
    return [
        {
            "id": x.id,
            "created_at": x.created_at.isoformat(),
            "final_state": x.final_state,
            "dynamics": x.dynamics,
            "diagnosis": x.diagnosis,
            "service_state": x.service_state,
        }
        for x in rows
    ]


@router.get("/{observation_id}")
def get_observation(observation_id: int, db: Session = Depends(get_db)):
    item = db.query(Observation).filter(Observation.id == observation_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Наблюдение не найдено")

    return serialize_observation(item)


@router.get("/{observation_id}/diagnosis")
def get_observation_diagnosis(observation_id: int, db: Session = Depends(get_db)):
    item = db.query(Observation).filter(Observation.id == observation_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Наблюдение не найдено")

    return {
        "id": item.id,
        "created_at": item.created_at.isoformat(),
        "final_state": item.final_state,
        "dynamics": item.dynamics,
        "diagnosis": item.diagnosis,
        "explanation": item.explanation,
    }