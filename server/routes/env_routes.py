# server/routes/env_routes.py

from fastapi import APIRouter, HTTPException
from server.schemas import ResetRequest, ResetResponse
from server.schemas import StepRequest, StepResponse
from env.core.environment import EmailTriageEnvironment
from env.models.actions import Action, ActionType
from tasks.task_factory import TaskFactory

router = APIRouter()

# Store active environments
environments: dict = {}


@router.post("/reset", response_model=ResetResponse)
def reset(request: ResetRequest):
    """Reset environment and start new episode."""
    try:
        task = TaskFactory.create(request.task_level)
        env = EmailTriageEnvironment(task=task)
        observation = env.reset(user_id=request.user_id)

        # Store environment
        episode_id = env.episode_id
        environments[episode_id] = env

        return ResetResponse(
            episode_id=episode_id,
            observation=observation,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/step", response_model=StepResponse)
def step(episode_id: str, request: StepRequest):
    """Take one step in the environment."""
    env = environments.get(episode_id)
    if not env:
        raise HTTPException(
            status_code=404,
            detail=f"Episode {episode_id} not found"
        )
    try:
        action = Action(
            action_type=ActionType(request.action_type),
            email_id=request.email_id,
            parameters=request.parameters,
        )
        observation, reward, done, info = env.step(action)

        # Clean up if done
        if done:
            del environments[episode_id]

        return StepResponse(
            observation=observation,
            reward=reward,
            done=done,
            info=info,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/render/{episode_id}")
def render(episode_id: str):
    """Render current environment state."""
    env = environments.get(episode_id)
    if not env:
        raise HTTPException(
            status_code=404,
            detail=f"Episode {episode_id} not found"
        )
    return {"render": env.render()}