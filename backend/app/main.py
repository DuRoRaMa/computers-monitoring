from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.monitoring import router as monitoring_router
from app.core.database import Base, engine

from app.models.indicator import Indicator  # noqa: F401
from app.models.diagnosis import Diagnosis  # noqa: F401
from app.models.severity_name import SeverityName  # noqa: F401
from app.models.possible_value import PossibleValue  # noqa: F401
from app.models.normal_value import NormalValue  # noqa: F401
from app.models.state_characteristic import StateCharacteristic  # noqa: F401
from app.models.diagnosis_value import DiagnosisValue  # noqa: F401
from app.models.severity_value import SeverityValue  # noqa: F401
from app.api.routes import knowledge, monitoring, observations

app = FastAPI(title="Computer Monitoring KBS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(knowledge_router)
app.include_router(monitoring_router)
app.include_router(observations.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)