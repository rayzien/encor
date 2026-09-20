from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, User

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user. For phase 1, we accept any username/password 
    if the database has no users, effectively creating a dummy auth flow.
    """
    # Simple dummy auth logic for UI testing
    if req.username and req.password:
        return {"status": "success", "token": "dummy-jwt-token-123"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
