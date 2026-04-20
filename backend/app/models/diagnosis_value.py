from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DiagnosisValue(Base):
    __tablename__ = "diagnosis_value"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    state_characteristic_id: Mapped[int] = mapped_column(
        ForeignKey("state_characteristic.id"),
        nullable=False
    )

    value_kind: Mapped[str] = mapped_column(String(20), nullable=False)

    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_inclusive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_inclusive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    scalar_value: Mapped[str | None] = mapped_column(String(255), nullable=True)