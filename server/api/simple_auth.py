from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import SessionLocal, User, ResourceLimit
from api.auth import create_access_token
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr

class LoginResponse(BaseModel):
    user: dict
    token: str

@router.post('/auth/login', response_model=LoginResponse)
async def login(request: LoginRequest):
    email = request.email.lower()
    
    # Check whitelist
    if email not in settings.whitelist_emails:
        logger.warning(f"Login attempt from non-whitelisted email: {email}")
        raise HTTPException(
            status_code=403,
            detail="このメールアドレスはホワイトリストに登録されていません。管理者に連絡してください。"
        )
    
    # Check if admin
    is_admin = email in settings.admin_emails
    
    db = SessionLocal()
    try:
        # Get or create user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.info(f"Creating new user: {email}")
            user = User(
                email=email,
                oauth_provider='email',
                oauth_id=email,
                is_admin=is_admin,
                is_whitelisted=True,
                is_banned=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create default resource limits
            limits = ResourceLimit(
                user_id=user.id,
                cpu_percent=settings.default_limits.cpu_percent,
                memory_mb=settings.default_limits.memory_mb,
                gpu_memory_mb=settings.default_limits.gpu_memory_mb,
                storage_mb=settings.default_limits.storage_mb
            )
            db.add(limits)
            db.commit()
            logger.info(f"User created with default limits: {email}")
        
        # Check if banned
        if user.is_banned:
            logger.warning(f"Banned user attempted login: {email}")
            raise HTTPException(
                status_code=403,
                detail="このアカウントは停止されています。"
            )
        
        # Update whitelist status if needed
        if not user.is_whitelisted:
            user.is_whitelisted = True
            db.commit()
        
        # Update admin status if needed
        if user.is_admin != is_admin:
            user.is_admin = is_admin
            db.commit()
        
        # Create JWT token
        token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        logger.info(f"User logged in successfully: {email}")
        
        return LoginResponse(
            user={
                "id": user.id,
                "email": user.email,
                "is_admin": user.is_admin,
                "is_banned": user.is_banned,
                "is_whitelisted": user.is_whitelisted
            },
            token=token
        )
        
    finally:
        db.close()
