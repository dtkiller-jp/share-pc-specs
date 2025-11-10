import os
import json
from pathlib import Path
from typing import Dict, Optional
from jupyter_client import KernelManager
import nbformat
from config import settings
from database import SessionLocal, Session as DBSession, User

class JupyterManager:
    def __init__(self):
        self.kernels: Dict[str, KernelManager] = {}
        self.user_sessions: Dict[int, list] = {}
        
        # Create notebooks directory
        Path(settings.storage.notebooks_path).mkdir(parents=True, exist_ok=True)
    
    def get_user_notebook_path(self, user_id: int, notebook_name: str) -> Path:
        user_dir = Path(settings.storage.notebooks_path) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / notebook_name
    
    async def get_or_create_kernel(self, user_id: int, notebook_path: str) -> KernelManager:
        key = f"{user_id}:{notebook_path}"
        
        if key not in self.kernels:
            km = KernelManager()
            km.start_kernel()
            self.kernels[key] = km
            
            # Create session in database
            db = SessionLocal()
            try:
                session = DBSession(
                    user_id=user_id,
                    notebook_path=notebook_path,
                    kernel_id=key
                )
                db.add(session)
                db.commit()
            finally:
                db.close()
        
        return self.kernels[key]
    
    async def execute_code(self, user_id: int, notebook_path: str, code: str, cell_id: str) -> dict:
        try:
            km = await self.get_or_create_kernel(user_id, notebook_path)
            kc = km.client()
            kc.start_channels()
            
            # Execute code
            msg_id = kc.execute(code)
            
            # Collect output
            output = []
            error = None
            
            while True:
                try:
                    msg = kc.get_iopub_msg(timeout=10)
                    msg_type = msg['header']['msg_type']
                    content = msg['content']
                    
                    if msg_type == 'stream':
                        output.append(content['text'])
                    elif msg_type == 'execute_result':
                        output.append(str(content['data']))
                    elif msg_type == 'error':
                        error = '\n'.join(content['traceback'])
                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        break
                except:
                    break
            
            kc.stop_channels()
            
            return {
                'cell_id': cell_id,
                'output': '\n'.join(output),
                'error': error
            }
        except Exception as e:
            return {
                'cell_id': cell_id,
                'output': '',
                'error': str(e)
            }
    
    async def save_notebook(self, user_id: int, notebook_path: str, content: dict) -> dict:
        try:
            file_path = self.get_user_notebook_path(user_id, notebook_path)
            
            # Create notebook from content
            nb = nbformat.v4.new_notebook()
            nb['cells'] = content.get('cells', [])
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            
            return {'success': True, 'message': 'Notebook saved'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def cleanup_session(self, sid: str):
        # Stop kernels for this session
        keys_to_remove = []
        for key, km in self.kernels.items():
            if sid in key:
                km.shutdown_kernel()
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.kernels[key]
