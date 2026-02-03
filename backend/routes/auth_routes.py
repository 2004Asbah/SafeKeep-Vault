from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, AuditLog
from schemas import LoginRequest, RegisterRequest
from auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        db.add(AuditLog(
            user=req.email,
            ngo_name=user.ngo_name if user else "Unknown",  # Fix: Check if user exists
            action="LOGIN_FAILED",
            target="System",
            status="Failed",
            ip=request.client.host if request.client else None
        ))
        db.commit()
        raise HTTPException(401, "Invalid credentials")

    token = create_token(req.email)
    db.add(AuditLog(
        user=req.email,
        ngo_name=user.ngo_name,  # Tenant isolation
        action="LOGIN",
        target="System",
        status="Success",
        ip=request.client.host if request.client else None
    ))
    db.commit()

    return {"token": token, "email": user.email, "name": user.ngo_name, "ngo": user.ngo_name, "role": user.role}

@router.post("/register")
def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    user = User(
        ngo_name=req.ngo_name,
        email=req.email,
        password_hash=hash_password(req.password),
        role="admin"
    )
    db.add(user)
    db.add(AuditLog(
        user=req.email,
        ngo_name=req.ngo_name,  # Tenant isolation
        action="REGISTER",
        target="System",
        status="Success",
        ip=request.client.host if request.client else None
    ))
    db.commit()

    return {"ok": True}
