from pydantic import BaseModel, Field, field_validator


class MonitoringInput(BaseModel):
    cpu_load: float | None = Field(None, ge=0, le=100)
    ram_usage: float | None = Field(None, ge=0, le=100)
    cpu_temp: float | None = Field(None, ge=20, le=120)
    disk_speed: float | None = Field(None, ge=0, le=1000)
    disk_fill: float | None = Field(None, ge=0, le=100)
    network_bandwidth: float | None = Field(None, ge=0, le=10000)
    process_count: int | None = Field(None, ge=0, le=1000)
    service_state: str | None = None
    previous_state: str | None = None

    @field_validator("service_state")
    @classmethod
    def validate_service_state(cls, value: str | None):
        if value is None:
            return value

        allowed = {
            "Все работают",
            "Некоторые остановлены",
            "Критический сервис остановлен",
        }
        if value not in allowed:
            raise ValueError("Некорректное состояние сервисов")
        return value
