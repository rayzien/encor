"""
API Router for System Settings and Configuration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from database import get_db, GlobalSetting

router = APIRouter(prefix="/api/settings", tags=["Settings"])

DEFAULT_SETTINGS = {
    "headless_mode": "false",
    "global_delay_min": "3.0",
    "global_delay_max": "8.0",
    "max_concurrent_accounts": "3",
    "auto_save_cookies": "true",
    "stealth_mode": "true",
    "log_level": "INFO"
}

@router.get("/")
def get_all_settings(db: Session = Depends(get_db)):
    settings_records = db.query(GlobalSetting).all()
    result = DEFAULT_SETTINGS.copy()
    for rec in settings_records:
        result[rec.key] = rec.value
    return result

@router.post("/")
def update_settings(settings_data: Dict[str, Any], db: Session = Depends(get_db)):
    for key, val in settings_data.items():
        rec = db.query(GlobalSetting).filter(GlobalSetting.key == key).first()
        if rec:
            rec.value = str(val)
        else:
            rec = GlobalSetting(key=key, value=str(val))
            db.add(rec)
    db.commit()
    return {"message": "Settings updated successfully."}
