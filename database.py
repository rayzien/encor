from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./encor.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """Model representing a dashboard administrator."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Account(Base):
    """Model representing an Instagram automation account."""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)
    cookies_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    safety_status = Column(String, default="safe")  # safe, warning, action_required
    bio = Column(Text, default="")
    profile_pic = Column(String, default="")
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    daily_likes_limit = Column(Integer, default=100)
    daily_follows_limit = Column(Integer, default=50)
    daily_comments_limit = Column(Integer, default=20)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("AutomationTask", back_populates="account")

class AutomationTask(Base):
    """Model representing a queued, running, or completed automation task."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    task_type = Column(String, index=True)  # like_by_tags, follow_by_tags, etc.
    config_json = Column(Text, default="{}")  # JSON string of params (tags, amount, skip_top_posts, etc.)
    status = Column(String, default="pending")  # pending, running, completed, failed, stopped
    progress = Column(Integer, default=0)
    total_target = Column(Integer, default=0)
    log_output = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account", back_populates="tasks")
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")

class TaskLog(Base):
    """Model representing an individual action log entry."""
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    action = Column(String)  # like, follow, comment, story_view
    target = Column(String)  # username, post_url, hashtag, location
    status = Column(String)  # success, skipped, failed
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("AutomationTask", back_populates="logs")

class GlobalSetting(Base):
    """Model for system-wide configurations."""
    __tablename__ = "global_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

