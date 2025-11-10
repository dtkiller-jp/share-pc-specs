import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import socketio
import logging
import os
from pathlib import Path
from api.routes import router
from api.websocket import sio
from database import engine, Base
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Distributed Jupyter System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include simple auth routes first
try:
    from api.simple_auth import router as auth_router
    app.include_router(auth_router, prefix="/api", tags=["auth"])
    logger.info("Simple auth routes registered")
    logger.info(f"Auth routes: {[route.path for route in auth_router.routes]}")
except Exception as e:
    logger.error(f"Failed to register auth routes: {e}")
    import traceback
    traceback.print_exc()

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])
logger.info(f"API routes: {[route.path for route in router.routes]}")

# Check if client build exists
client_dist = Path(__file__).parent.parent / "client" / "dist"
if client_dist.exists():
    logger.info(f"Serving client from: {client_dist}")
    # Serve static files
    app.mount("/assets", StaticFiles(directory=str(client_dist / "assets")), name="assets")
    
    @app.get("/")
    async def serve_spa():
        return FileResponse(str(client_dist / "index.html"))
    
    @app.get("/{full_path:path}")
    async def serve_spa_routes(full_path: str):
        # Don't intercept API or socket.io routes
        if full_path.startswith("api/") or full_path.startswith("socket.io/"):
            return {"error": "Not found"}
        
        file_path = client_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(client_dist / "index.html"))
else:
    logger.warning("Client build not found. Run 'npm run build' in client directory.")
    
    @app.get("/")
    async def root():
        return {
            "message": "Distributed Jupyter Server is running",
            "note": "Client not built. Run 'cd client && npm install && npm run build'"
        }

# Socket.IO
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Distributed Jupyter Server")
    logger.info("=" * 60)
    logger.info(f"Starting server on {settings.server.host}:{settings.server.port}")
    logger.info("")
    logger.info("Access the application at:")
    logger.info(f"  → http://localhost:{settings.server.port}")
    if settings.server.host == "0.0.0.0":
        logger.info(f"  → http://YOUR_LOCAL_IP:{settings.server.port}")
    logger.info("")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 60)
    
    uvicorn.run(
        "main:socket_app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True,
        log_level="info"
    )
