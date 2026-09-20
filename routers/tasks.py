"""
API Router for Automation Tasks and Targeted Discovery.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json

from database import get_db, AutomationTask, TaskLog, Account
from engine.core.task_runner import execute_task

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

class TaskCreate(BaseModel):
    account_id: Optional[int] = None
    task_type: str
    config: Dict[str, Any]

@router.get("/")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(AutomationTask).order_by(AutomationTask.id.desc()).all()
    return tasks

@router.post("/")
def create_and_queue_task(task_data: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if task_data.account_id:
        acc = db.query(Account).filter(Account.id == task_data.account_id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Specified account not found.")

    new_task = AutomationTask(
        account_id=task_data.account_id,
        task_type=task_data.task_type,
        config_json=json.dumps(task_data.config),
        status="pending",
        progress=0,
        total_target=task_data.config.get("amount", 10)
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Queue execution in background
    background_tasks.add_task(execute_task, new_task.id)

    return new_task

@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task

@router.get("/{task_id}/logs")
def get_task_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    logs = db.query(TaskLog).filter(TaskLog.task_id == task_id).all()
    return {"task_id": task_id, "log_output": task.log_output, "structured_logs": logs}

@router.post("/{task_id}/stop")
def stop_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    task.status = "stopped"
    db.commit()
    return {"message": f"Task {task_id} marked as stopped."}

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully."}
