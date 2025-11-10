from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db, User
from config import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.server.secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    # モックトークンを許可（開発用）
    if token and token.startswith("mock-token-"):
        logger.info(f"Mock token accepted: {token}")
        return {"sub": "1", "email": "mock@example.com"}
    
    try:
        payload = jwt.decode(token, settings.server.secret_key, algorithms=["HS256"])
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")
    
    if not user.is_whitelisted:
        raise HTTPException(status_code=403, detail="User is not whitelisted")
    
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
