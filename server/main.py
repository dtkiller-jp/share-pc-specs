import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from api.routes import router
from api.websocket import sio
from database import engine, Base
from config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Distributed Jupyter System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Socket.IO
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    print(f"Starting server on {settings.server.host}:{settings.server.port}")
    uvicorn.run(
        "main:socket_app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True
    )
