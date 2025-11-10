import socketio
import logging
from jupyter.manager import JupyterManager
from resources.monitor import ResourceMonitor
from api.auth import verify_token
from database import SessionLocal, User

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # 開発用：すべてのオリジンを許可
    logger=True,
    engineio_logger=True
)

jupyter_manager = JupyterManager()
resource_monitor = ResourceMonitor()

@sio.event
async def connect(sid, environ, auth):
    logger.info(f"[WebSocket] Client connecting: {sid}")
    logger.info(f"[WebSocket] Auth data: {auth}")
    
    # Verify token
    token = auth.get('token') if auth else None
    if not token:
        logger.warning(f"[WebSocket] No token provided for {sid}")
        return False
    
    payload = verify_token(token)
    if not payload:
        logger.warning(f"[WebSocket] Invalid token for {sid}")
        return False
    
    user_id = payload.get('sub')
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or user.is_banned or not user.is_whitelisted:
            logger.warning(f"[WebSocket] User {user_id} not authorized")
            return False
        
        # Store user info in session
        async with sio.session(sid) as session:
            session['user_id'] = user_id
            session['email'] = user.email
        
        logger.info(f"[WebSocket] Client connected successfully: {sid} (user: {user.email})")
    finally:
        db.close()
    
    return True

@sio.event
async def disconnect(sid):
    logger.info(f"[WebSocket] Client disconnected: {sid}")
    # Clean up user session
    await jupyter_manager.cleanup_session(sid)

@sio.event
async def execute_cell(sid, data):
    logger.info(f"[WebSocket] Execute cell request from {sid}")
    logger.info(f"[WebSocket] Cell data: {data}")
    
    async with sio.session(sid) as session:
        user_id = session.get('user_id')
    
    if not user_id:
        logger.error(f"[WebSocket] Unauthorized execute request from {sid}")
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    # Check resource limits
    if not await resource_monitor.check_limits(user_id):
        logger.warning(f"[WebSocket] Resource limit exceeded for user {user_id}")
        await sio.emit('error', {'message': 'Resource limit exceeded. Waiting for session to end.'}, room=sid)
        return
    
    # Execute code
    logger.info(f"[WebSocket] Executing code for user {user_id}")
    result = await jupyter_manager.execute_code(
        user_id=user_id,
        notebook_path=data.get('notebook_path'),
        code=data.get('code'),
        cell_id=data.get('cell_id')
    )
    
    logger.info(f"[WebSocket] Execution result: {result}")
    await sio.emit('cell_output', result, room=sid)

@sio.event
async def save_notebook(sid, data):
    logger.info(f"[WebSocket] Save notebook request from {sid}")
    
    async with sio.session(sid) as session:
        user_id = session.get('user_id')
    
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    result = await jupyter_manager.save_notebook(
        user_id=user_id,
        notebook_path=data.get('notebook_path'),
        content=data.get('content')
    )
    
    logger.info(f"[WebSocket] Save result: {result}")
    await sio.emit('save_result', result, room=sid)
