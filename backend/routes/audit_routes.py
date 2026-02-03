from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import AuditLog, User
from dependencies import get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("")
def list_audit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 100
):
    # Filter audit logs by NGO
    logs = db.query(AuditLog)\
        .filter(AuditLog.ngo_name == current_user.ngo_name)\
        .order_by(AuditLog.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return [{
        "timestamp": l.timestamp.isoformat(),
        "user": l.user,
        "action": l.action,
        "target": l.target,
        "status": l.status,
        "ip_address": l.ip
    } for l in logs]
