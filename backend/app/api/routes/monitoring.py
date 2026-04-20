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