from pydantic import BaseModel, Field, field_validator


class MonitoringInput(BaseModel):
    cpu_load: float = Field(..., ge=0, le=100)
    ram_usage: float = Field(..., ge=0, le=100)
    cpu_temp: float = Field(..., ge=20, le=120)
    disk_speed: float = Field(..., ge=0, le=1000)
    disk_fill: float = Field(..., ge=0, le=100)
    network_bandwidth: float = Field(..., ge=0, le=10000)
    process_count: int = Field(..., ge=0, le=1000)
    service_state: str
    previous_state: str | None = None

    @field_validator("service_state")
    @classmethod
    def validate_service_state(cls, value: str) -> str:
        allowed = {
            "Все работают",
            "Некоторые остановлены",
            "Критический сервис остановлен",
        }
        if value not in allowed:
            raise ValueError(
                "service_state должен быть одним из значений: "
                "'Все работают', 'Некоторые остановлены', "
                "'Критический сервис остановлен'"
            )
        return value