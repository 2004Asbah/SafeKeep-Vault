"""
Authentication dependencies for FastAPI routes.
Extracts user information from JWT tokens.
"""
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import User
from auth import decode_token

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate user from JWT token.
    Returns the User object for the authenticated user.
    """
    if not authorization:
        raise HTTPException(401, "Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization header format")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        email = decode_token(token)
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(401, "User not found")
    
    return user
