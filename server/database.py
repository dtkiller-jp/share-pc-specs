from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

engine = create_engine(settings.database.url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    oauth_provider = Column(String)
    oauth_id = Column(String)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    is_whitelisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    resource_limits = relationship("ResourceLimit", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")

class ResourceLimit(Base):
    __tablename__ = "resource_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    cpu_percent = Column(Integer)
    memory_mb = Column(Integer)
    gpu_memory_mb = Column(Integer)
    storage_mb = Column(Integer)
    
    user = relationship("User", back_populates="resource_limits")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    notebook_path = Column(String)
    kernel_id = Column(String, nullable=True)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    gpu_usage = Column(Float, default=0.0)
    storage_usage = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="sessions")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
