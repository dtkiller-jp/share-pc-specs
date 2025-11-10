from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db, User, ResourceLimit, Session as DBSession
from api.auth import get_current_user, require_admin
from api.schemas import UserResponse, ResourceLimitUpdate, UserUpdate, SessionResponse
from datetime import datetime

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users

@router.put("/admin/users/{user_id}/limits")
async def update_user_limits(
    user_id: int,
    limits: ResourceLimitUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resource_limit = db.query(ResourceLimit).filter(ResourceLimit.user_id == user_id).first()
    if not resource_limit:
        resource_limit = ResourceLimit(user_id=user_id)
        db.add(resource_limit)
    
    resource_limit.cpu_percent = limits.cpu_percent
    resource_limit.memory_mb = limits.memory_mb
    resource_limit.gpu_memory_mb = limits.gpu_memory_mb
    resource_limit.storage_mb = limits.storage_mb
    
    db.commit()
    db.refresh(resource_limit)
    return {"message": "Limits updated successfully"}

@router.put("/admin/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.is_banned is not None:
        user.is_banned = user_update.is_banned
    if user_update.is_whitelisted is not None:
        user.is_whitelisted = user_update.is_whitelisted
    
    db.commit()
    return {"message": "User updated successfully"}

@router.get("/admin/sessions", response_model=List[SessionResponse])
async def list_sessions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    sessions = db.query(DBSession).filter(DBSession.is_active == True).all()
    return sessions

@router.delete("/admin/sessions/{session_id}")
async def terminate_session(
    session_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Session terminated"}
