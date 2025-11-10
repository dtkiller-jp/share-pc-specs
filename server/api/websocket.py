import socketio
from jupyter.manager import JupyterManager
from resources.monitor import ResourceMonitor
from api.auth import verify_token
from database import SessionLocal, User

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['http://localhost:3000', 'http://localhost:5173']
)

jupyter_manager = JupyterManager()
resource_monitor = ResourceMonitor()

@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")
    
    # Verify token
    token = auth.get('token') if auth else None
    if not token:
        return False
    
    payload = verify_token(token)
    if not payload:
        return False
    
    user_id = payload.get('sub')
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or user.is_banned or not user.is_whitelisted:
            return False
        
        # Store user info in session
        async with sio.session(sid) as session:
            session['user_id'] = user_id
            session['email'] = user.email
    finally:
        db.close()
    
    return True

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    # Clean up user session
    await jupyter_manager.cleanup_session(sid)

@sio.event
async def execute_cell(sid, data):
    async with sio.session(sid) as session:
        user_id = session.get('user_id')
    
    if not user_id:
        await sio.emit('error', {'message': 'Unauthorized'}, room=sid)
        return
    
    # Check resource limits
    if not await resource_monitor.check_limits(user_id):
        await sio.emit('error', {'message': 'Resource limit exceeded. Waiting for session to end.'}, room=sid)
        return
    
    # Execute code
    result = await jupyter_manager.execute_code(
        user_id=user_id,
        notebook_path=data.get('notebook_path'),
        code=data.get('code'),
        cell_id=data.get('cell_id')
    )
    
    await sio.emit('cell_output', result, room=sid)

@sio.event
async def save_notebook(sid, data):
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
    
    await sio.emit('save_result', result, room=sid)
