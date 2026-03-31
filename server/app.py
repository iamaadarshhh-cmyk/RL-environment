# server/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.env_routes import router as env_router
from server.routes.task_routes import router as task_router
from server.routes.grader_routes import router as grader_router
from server.middleware import setup_middleware
from env.config import SERVER_HOST, SERVER_PORT


# ─── Create App ─────────────────────────────────────────────
app = FastAPI(
    title="Email Triage RL Environment",
    description="A reinforcement learning environment for email triage",
    version="1.0.0",
)

# ─── CORS Middleware ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Setup Middleware ───────────────────────────────────────
setup_middleware(app)

# ─── Include Routers ────────────────────────────────────────
app.include_router(env_router,    prefix="/env",    tags=["Environment"])
app.include_router(task_router,   prefix="/tasks",  tags=["Tasks"])
app.include_router(grader_router, prefix="/grader", tags=["Grader"])


# ─── Root Endpoint ──────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "Email Triage RL Environment",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "environment": "/env",
            "tasks": "/tasks",
            "grader": "/grader",
            "docs": "/docs",
        }
    }


# ─── Health Check ───────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "healthy"}