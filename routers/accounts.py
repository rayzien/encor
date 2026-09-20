"""
API Router for Instagram Account Management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db, Account

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])

class AccountCreate(BaseModel):
    username: str
    password: Optional[str] = None
    daily_likes_limit: Optional[int] = 100
    daily_follows_limit: Optional[int] = 50
    daily_comments_limit: Optional[int] = 20

class AccountUpdate(BaseModel):
    is_active: Optional[bool] = None
    safety_status: Optional[str] = None
    daily_likes_limit: Optional[int] = None
    daily_follows_limit: Optional[int] = None
    daily_comments_limit: Optional[int] = None

@router.get("/")
def get_all_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts

@router.post("/")
def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    existing = db.query(Account).filter(Account.username == account_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account with this username already exists.")
    
    new_acc = Account(
        username=account_data.username.lstrip("@").strip(),
        password=account_data.password,
        daily_likes_limit=account_data.daily_likes_limit,
        daily_follows_limit=account_data.daily_follows_limit,
        daily_comments_limit=account_data.daily_comments_limit,
        safety_status="safe"
    )
    db.add(new_acc)
    db.commit()
    db.refresh(new_acc)
    return new_acc

@router.get("/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc

@router.put("/{account_id}")
def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if data.is_active is not None:
        acc.is_active = data.is_active
    if data.safety_status is not None:
        acc.safety_status = data.safety_status
    if data.daily_likes_limit is not None:
        acc.daily_likes_limit = data.daily_likes_limit
    if data.daily_follows_limit is not None:
        acc.daily_follows_limit = data.daily_follows_limit
    if data.daily_comments_limit is not None:
        acc.daily_comments_limit = data.daily_comments_limit

    db.commit()
    db.refresh(acc)
    return acc

@router.post("/{account_id}/toggle")
def toggle_account_status(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    acc.is_active = not acc.is_active
    db.commit()
    db.refresh(acc)
    return {"id": acc.id, "username": acc.username, "is_active": acc.is_active}

@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(acc)
    db.commit()
    return {"message": "Account deleted successfully."}
