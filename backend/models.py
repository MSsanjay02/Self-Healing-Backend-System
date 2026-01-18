from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base
from sqlalchemy import Boolean


class MetricsDB(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=False)

    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)

    system_name = Column(String, default="windows-machine")

    server_received_time = Column(DateTime, default=datetime.utcnow)
    anomaly_score = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, default=False)

