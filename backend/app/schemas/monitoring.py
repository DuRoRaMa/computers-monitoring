from pydantic import BaseModel, field_validator


class MonitoringInput(BaseModel):
    # Жесткие диапазоны здесь не задаются.
    # Допустимость значений проверяется в /monitoring/evaluate
    # по возможным значениям из базы знаний.
    cpu_load: float | None = None
    ram_usage: float | None = None
    cpu_temp: float | None = None
    disk_speed: float | None = None
    disk_fill: float | None = None
    network_bandwidth: float | None = None
    process_count: float | None = None
    service_state: str | None = None
    previous_state: str | None = None

    @field_validator(
        "cpu_load",
        "ram_usage",
        "cpu_temp",
        "disk_speed",
        "disk_fill",
        "network_bandwidth",
        "process_count",
    )
    @classmethod
    def validate_integer_numeric_value(cls, value: float | None) -> float | None:
        if value is None:
            return value

        if not float(value).is_integer():
            raise ValueError("Значение числового показателя должно быть целым числом")

        return value
