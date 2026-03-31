# server/routes/grader_routes.py

from fastapi import APIRouter, HTTPException
from grader.grader import Grader
from server.routes.env_routes import environments

router = APIRouter()
grader = Grader()


@router.get("/grade/{episode_id}")
def grade(episode_id: str):
    """Grade a completed episode."""
    env = environments.get(episode_id)
    if not env:
        raise HTTPException(
            status_code=404,
            detail=f"Episode {episode_id} not found"
        )
    if not env.history:
        raise HTTPException(
            status_code=400,
            detail="No history found for this episode"
        )

    result = grader.grade(env.history)
    return result





## What each file does in short

### `app.py` — Main Server
# ```
# Creates FastAPI app
# Adds CORS middleware      ← allows client to connect
# Registers 3 routers       ← env, tasks, grader
# Root endpoint /           ← server info
# Health check /health      ← is server running?
# ```

# ### `middleware.py` — Request Logger
# Logs every request:
# ```
# POST /env/reset → 200 (0.0234s)
# POST /env/step  → 200 (0.0123s)
# GET  /health    → 200 (0.0001s)
# ```

# ### `schemas.py` — Data Shapes
# Defines exactly what data goes **in** and **out** of every endpoint:
# ```
# ResetRequest  → user_id, task_level
# ResetResponse → episode_id, observation
# StepRequest   → action_type, email_id, parameters
# StepResponse  → observation, reward, done, info
# ```

# ### `env_routes.py` — Environment Endpoints
# ```
# POST /env/reset        → start new episode
# POST /env/step         → take one action
# GET  /env/render/{id}  → see current state
# ```

# ### `task_routes.py` — Task Endpoints
# ```
# GET /tasks/levels    → ["easy", "medium", "hard"]
# GET /tasks/{level}   → info about that level
# ```

# ### `grader_routes.py` — Grader Endpoints
# ```
# GET /grader/grade/{episode_id} → final score