import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from jupyter_client import KernelManager
import nbformat
from config import settings
from database import SessionLocal, Session as DBSession, User

logger = logging.getLogger(__name__)

class JupyterManager:
    def __init__(self):
        self.kernels: Dict[str, KernelManager] = {}
        self.user_sessions: Dict[int, list] = {}
        
        # Create notebooks directory
        Path(settings.storage.notebooks_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Jupyter Manager initialized. Notebooks path: {settings.storage.notebooks_path}")
    
    def get_user_notebook_path(self, user_id: int, notebook_name: str) -> Path:
        user_dir = Path(settings.storage.notebooks_path) / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / notebook_name
    
    async def get_or_create_kernel(self, user_id: int, notebook_path: str) -> KernelManager:
        key = f"{user_id}:{notebook_path}"
        
        if key not in self.kernels:
            logger.info(f"Creating new kernel for user {user_id}, notebook {notebook_path}")
            km = KernelManager(kernel_name='python3')
            try:
                km.start_kernel()
            except Exception as e:
                logger.warning(f"Failed to start python3 kernel, trying default: {e}")
                # Fallback to default kernel
                km = KernelManager()
                km.start_kernel()
            self.kernels[key] = km
            logger.info(f"Kernel started: {key}")
            
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
                logger.info(f"Session created in database for kernel {key}")
            finally:
                db.close()
        
        return self.kernels[key]
    
    async def execute_code(self, user_id: int, notebook_path: str, code: str, cell_id: str) -> dict:
        logger.info(f"Executing code for user {user_id}, cell {cell_id}")
        logger.info(f"Code: {code[:100]}...")  # Log first 100 chars
        
        try:
            km = await self.get_or_create_kernel(user_id, notebook_path)
            kc = km.client()
            kc.start_channels()
            
            # Execute code
            logger.info("Sending code to kernel...")
            msg_id = kc.execute(code)
            
            # Collect output
            output = []
            error = None
            
            logger.info("Waiting for execution results...")
            while True:
                try:
                    msg = kc.get_iopub_msg(timeout=30)
                    msg_type = msg['header']['msg_type']
                    content = msg['content']
                    
                    logger.info(f"Received message type: {msg_type}")
                    
                    if msg_type == 'stream':
                        output.append(content['text'])
                        logger.info(f"Stream output: {content['text']}")
                    elif msg_type == 'execute_result':
                        data = content.get('data', {})
                        if 'text/plain' in data:
                            output.append(data['text/plain'])
                            logger.info(f"Execute result: {data['text/plain']}")
                    elif msg_type == 'display_data':
                        data = content.get('data', {})
                        if 'text/plain' in data:
                            output.append(data['text/plain'])
                    elif msg_type == 'error':
                        error = '\n'.join(content['traceback'])
                        logger.error(f"Execution error: {error}")
                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        logger.info("Execution completed")
                        break
                except Exception as e:
                    logger.warning(f"Timeout or error waiting for message: {e}")
                    break
            
            kc.stop_channels()
            
            result = {
                'cell_id': cell_id,
                'output': '\n'.join(output) if output else '',
                'error': error
            }
            logger.info(f"Execution result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing code: {e}", exc_info=True)
            return {
                'cell_id': cell_id,
                'output': '',
                'error': str(e)
            }
    
    async def save_notebook(self, user_id: int, notebook_path: str, content: dict) -> dict:
        try:
            file_path = self.get_user_notebook_path(user_id, notebook_path)
            logger.info(f"Saving notebook to {file_path}")
            
            # Create notebook from content
            nb = nbformat.v4.new_notebook()
            nb['cells'] = content.get('cells', [])
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            
            logger.info(f"Notebook saved successfully: {file_path}")
            return {'success': True, 'message': 'Notebook saved'}
        except Exception as e:
            logger.error(f"Error saving notebook: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    async def cleanup_session(self, sid: str):
        logger.info(f"Cleaning up session: {sid}")
        # Stop kernels for this session
        keys_to_remove = []
        for key, km in self.kernels.items():
            if sid in key:
                km.shutdown_kernel()
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.kernels[key]
            logger.info(f"Kernel removed: {key}")
