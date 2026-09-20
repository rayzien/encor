from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import logging

from database import engine, Base, get_db, AutomationTask
from automation import run_automation_task
from routers import auth

# Initialize DB tables (redundant if database.py is run directly, but good practice here)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Encor API")

app.include_router(auth.router)

# Mount the pages directory to serve static files (CSS, JS, images)
pages_dir = os.path.join(os.path.dirname(__file__), "pages")

if os.path.exists(pages_dir):
    app.mount("/static", StaticFiles(directory=pages_dir), name="static")

@app.get("/login")
async def read_login():
    """Serve the login HTML page."""
    login_path = os.path.join(pages_dir, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"message": "Login page not found."}

@app.get("/")
async def read_index():
    """Serve the main HTML page."""
    index_path = os.path.join(pages_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Encor! (index.html not found)"}

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Simple API health check endpoint ensuring DB is accessible."""
    return {"status": "ok", "message": "Encor Backend is running efficiently."}

@app.post("/api/automation/start")
async def start_automation(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Starts a basic Playwright automation task in the background."""
    new_task = AutomationTask(task_type="default_run", status="pending")
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Run the actual automation in the background
    background_tasks.add_task(run_automation_task, "default_run")
    
    return {"status": "ok", "message": "Automation task queued.", "task_id": new_task.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5050, reload=True)
