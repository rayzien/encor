"""
Authentication router for admin dashboard login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import hashlib

from database import get_db, User
from logger import auth_logger

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate dashboard administrator.
    If database contains no admin users yet, automatically initializes first admin account.
    """
    clean_username = req.username.strip().lower()
    
    if not clean_username or not req.password:
        auth_logger.warning("Login attempt with empty credentials.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    # Check existing users
    user_count = db.query(User).count()
    hashed_pwd = hash_password(req.password)

    if user_count == 0:
        # First time setup: create admin user automatically
        new_admin = User(username=clean_username, hashed_password=hashed_pwd)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        auth_logger.info(f"Initialized first admin user @{clean_username}")
        return {"status": "success", "token": f"token-{new_admin.id}-{clean_username}", "username": clean_username}

    user = db.query(User).filter(User.username == clean_username).first()
    
    if not user:
        auth_logger.warning(f"Failed login attempt for non-existent user @{clean_username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if user.hashed_password != hashed_pwd:
        auth_logger.warning(f"Invalid password provided for user @{clean_username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    auth_logger.info(f"User @{clean_username} authenticated successfully.")
    return {"status": "success", "token": f"token-{user.id}-{clean_username}", "username": user.username}
