from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    is_banned: bool
    is_whitelisted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResourceLimitUpdate(BaseModel):
    cpu_percent: int
    memory_mb: int
    gpu_memory_mb: int
    storage_mb: int

class UserUpdate(BaseModel):
    is_banned: Optional[bool] = None
    is_whitelisted: Optional[bool] = None

class SessionResponse(BaseModel):
    id: int
    user_id: int
    notebook_path: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    storage_usage: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotebookExecuteRequest(BaseModel):
    code: str
    cell_id: str

class NotebookExecuteResponse(BaseModel):
    cell_id: str
    output: str
    error: Optional[str] = None
