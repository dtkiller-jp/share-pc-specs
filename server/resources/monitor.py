import psutil
import os
from typing import Optional
from database import SessionLocal, User, ResourceLimit, Session as DBSession

try:
    import GPUtil
    GPU_AVAILABLE = True
except:
    GPU_AVAILABLE = False

class ResourceMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    async def check_limits(self, user_id: int) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            limits = db.query(ResourceLimit).filter(ResourceLimit.user_id == user_id).first()
            if not limits:
                return True
            
            # Check CPU
            cpu_percent = self.process.cpu_percent()
            if cpu_percent > limits.cpu_percent:
                return False
            
            # Check Memory
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            if memory_mb > limits.memory_mb:
                return False
            
            # Check Storage
            storage_usage = await self.get_user_storage(user_id)
            if storage_usage > limits.storage_mb:
                return False
            
            return True
        finally:
            db.close()
    
    async def get_user_storage(self, user_id: int) -> float:
        from pathlib import Path
        from config import settings
        
        user_dir = Path(settings.storage.notebooks_path) / str(user_id)
        if not user_dir.exists():
            return 0.0
        
        total_size = 0
        for file in user_dir.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    async def get_system_stats(self) -> dict:
        stats = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': psutil.disk_usage('/')._asdict()
        }
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                stats['gpus'] = [
                    {
                        'id': gpu.id,
                        'name': gpu.name,
                        'load': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal
                    }
                    for gpu in gpus
                ]
            except:
                stats['gpus'] = []
        else:
            stats['gpus'] = []
        
        return stats
    
    async def get_user_usage(self, user_id: int) -> dict:
        db = SessionLocal()
        try:
            sessions = db.query(DBSession).filter(
                DBSession.user_id == user_id,
                DBSession.is_active == True
            ).all()
            
            total_cpu = sum(s.cpu_usage for s in sessions)
            total_memory = sum(s.memory_usage for s in sessions)
            total_gpu = sum(s.gpu_usage for s in sessions)
            storage = await self.get_user_storage(user_id)
            
            return {
                'cpu_usage': total_cpu,
                'memory_usage': total_memory,
                'gpu_usage': total_gpu,
                'storage_usage': storage
            }
        finally:
            db.close()
