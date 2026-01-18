from fastapi import FastAPI, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import MetricsDB
from database import Base

app = FastAPI(title="Predictive System Monitor API")

# create DB tables
Base.metadata.create_all(bind=engine)


class Metrics(BaseModel):
    timestamp: str
    cpu_usage: float
    memory_usage: float
    system_name: str = "windows-machine"


# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Backend is running ✅"}


@app.post("/metrics")
def receive_metrics(metrics: Metrics, db: Session = Depends(get_db)):
    record = MetricsDB(
        timestamp=metrics.timestamp,
        cpu_usage=metrics.cpu_usage,
        memory_usage=metrics.memory_usage,
        system_name=metrics.system_name,
        server_received_time=datetime.utcnow()
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "status": "success",
        "id": record.id
    }


@app.get("/metrics")
def get_metrics(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.query(MetricsDB).order_by(MetricsDB.id.desc()).limit(limit).all()

    # convert DB objects → JSON
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "cpu_usage": r.cpu_usage,
            "memory_usage": r.memory_usage,
            "system_name": r.system_name,
            "server_received_time": str(r.server_received_time)
        }
        for r in rows
    ]


@app.get("/health")
def health(db: Session = Depends(get_db)):
    count = db.query(MetricsDB).count()
    return {"status": "ok", "records_in_db": count}
