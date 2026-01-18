import csv
from io import StringIO
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import MetricsDB
from ml_engine import predict_anomaly

from recovery_models import RecoveryLogDB
from recovery_engine import start_demo_service_once  # ✅ CMD opens only ONCE


app = FastAPI(title="Predictive System Monitor API")

# ✅ Create tables (only if not exists)
Base.metadata.create_all(bind=engine)


# -------------------------
# Pydantic Schema (API input)
# -------------------------
class Metrics(BaseModel):
    timestamp: str
    cpu_usage: float
    memory_usage: float
    system_name: str = "windows-machine"


# -------------------------
# DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Routes
# -------------------------
@app.get("/")
def root():
    return {"message": "Backend is running ✅"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    count = db.query(MetricsDB).count()
    return {"status": "ok", "records_in_db": count}


@app.post("/metrics")
def receive_metrics(metrics: Metrics, db: Session = Depends(get_db)):
    # ✅ 1) ML Prediction
    score, is_anomaly = predict_anomaly(metrics.cpu_usage, metrics.memory_usage)

    # ✅ 2) Save metric into DB
    record = MetricsDB(
        timestamp=metrics.timestamp,
        cpu_usage=metrics.cpu_usage,
        memory_usage=metrics.memory_usage,
        system_name=metrics.system_name,
        server_received_time=datetime.utcnow(),
        anomaly_score=score,
        is_anomaly=is_anomaly
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    # ✅ 3) Self-healing if anomaly detected (OPEN CMD ONLY ONCE)
    recovery_triggered = False
    recovery_message = None
    warning_message = None

    if is_anomaly:
        warning_message = "⚠️ Anomaly detected — restart your system else it may go down!"
        print(warning_message)

        ok, msg = start_demo_service_once()
        recovery_triggered = bool(ok)
        recovery_message = msg

        # store recovery log
        log = RecoveryLogDB(
            action="OPEN_CMD_ONCE",
            reason="ANOMALY_DETECTED",
            details=f"metric_id={record.id} score={score}"
        )
        db.add(log)
        db.commit()

    # ✅ 4) Return response
    return {
        "status": "success",
        "id": record.id,
        "anomaly_score": score,
        "is_anomaly": is_anomaly,
        "warning": warning_message,
        "recovery_triggered": recovery_triggered,
        "recovery_message": recovery_message
    }


@app.get("/metrics")
def get_metrics(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.query(MetricsDB).order_by(MetricsDB.id.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "cpu_usage": r.cpu_usage,
            "memory_usage": r.memory_usage,
            "system_name": r.system_name,
            "server_received_time": str(r.server_received_time),
            "anomaly_score": r.anomaly_score,
            "is_anomaly": r.is_anomaly
        }
        for r in rows
    ]


@app.get("/metrics/anomalies")
def get_anomalies(limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(MetricsDB)
        .filter(MetricsDB.is_anomaly == True)  # noqa: E712
        .order_by(MetricsDB.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "cpu_usage": r.cpu_usage,
            "memory_usage": r.memory_usage,
            "system_name": r.system_name,
            "server_received_time": str(r.server_received_time),
            "anomaly_score": r.anomaly_score,
            "is_anomaly": r.is_anomaly
        }
        for r in rows
    ]


@app.get("/recovery/logs")
def get_recovery_logs(limit: int = 20, db: Session = Depends(get_db)):
    rows = (
        db.query(RecoveryLogDB)
        .order_by(RecoveryLogDB.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "created_at": str(r.created_at),
            "action": r.action,
            "reason": r.reason,
            "details": r.details
        }
        for r in rows
    ]


@app.get("/export/csv")
def export_csv(limit: int = 1000, db: Session = Depends(get_db)):
    rows = db.query(MetricsDB).order_by(MetricsDB.id.asc()).limit(limit).all()

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id",
        "timestamp",
        "cpu_usage",
        "memory_usage",
        "system_name",
        "server_received_time",
        "anomaly_score",
        "is_anomaly"
    ])

    # Rows
    for r in rows:
        writer.writerow([
            r.id,
            r.timestamp,
            r.cpu_usage,
            r.memory_usage,
            r.system_name,
            str(r.server_received_time),
            r.anomaly_score,
            r.is_anomaly
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=metrics.csv"},
    )
