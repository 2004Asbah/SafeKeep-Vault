from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("")
def list_audit(db: Session = Depends(get_db), limit: int = 100):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [{
        "timestamp": l.timestamp.isoformat(),
        "user": l.user,
        "action": l.action,
        "target": l.target,
        "status": l.status,
        "ip": l.ip
    } for l in logs]
