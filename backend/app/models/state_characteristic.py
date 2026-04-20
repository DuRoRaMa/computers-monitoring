from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StateCharacteristic(Base):
    __tablename__ = "state_characteristic"
    __table_args__ = (
        UniqueConstraint("diagnosis_id", "indicator_id", name="uq_state_characteristic"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    diagnosis_id: Mapped[int] = mapped_column(ForeignKey("diagnosis.id"), nullable=False)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicator.id"), nullable=False)