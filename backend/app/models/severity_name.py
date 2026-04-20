from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SeverityName(Base):
    __tablename__ = "severity_name"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    order_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)