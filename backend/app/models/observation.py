from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.core.database import Base


class Observation(Base):
    __tablename__ = "observation"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cpu_load = Column(Float, nullable=False)
    ram_usage = Column(Float, nullable=False)
    cpu_temp = Column(Float, nullable=False)
    disk_speed = Column(Float, nullable=False)
    disk_fill = Column(Float, nullable=False)
    network_bandwidth = Column(Float, nullable=False)
    process_count = Column(Float, nullable=False)
    service_state = Column(String, nullable=False)
    previous_state = Column(String, nullable=True)

    final_state = Column(String, nullable=False)
    dynamics = Column(String, nullable=True)
    diagnosis = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)

    indicator_results_json = Column(Text, nullable=False)