from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class RecoveryLogDB(Base):
    __tablename__ = "recovery_logs"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    action = Column(String, nullable=False)          # e.g. "RESTART_DEMO_APP"
    reason = Column(String, nullable=False)          # e.g. "ANOMALY_DETECTED"
    details = Column(String, nullable=True)          # store extra info
