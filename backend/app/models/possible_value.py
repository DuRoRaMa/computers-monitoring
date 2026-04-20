from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PossibleValue(Base):
    __tablename__ = "possible_value"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicator.id"), nullable=False)

    # "range" или "scalar"
    value_kind: Mapped[str] = mapped_column(String(20), nullable=False)

    min_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_inclusive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_inclusive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    scalar_value: Mapped[str | None] = mapped_column(String(255), nullable=True)