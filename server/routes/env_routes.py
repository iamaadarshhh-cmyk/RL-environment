# server/routes/env_routes.py

from fastapi import APIRouter, HTTPException
from server.schemas import ResetRequest, ResetResponse
from server.schemas import StepRequest, StepResponse
from env.core.environment import EmailTriageEnvironment
from env.models.actions import Action, ActionType
from tasks.task_factory import TaskFactory

import traceback  # 🔥 important for debugging

router = APIRouter()

# Store active environments
environments: dict = {}

# Store completed histories (for grading fix)
completed_episodes: dict = {}


@router.post("/reset", response_model=ResetResponse)
def reset(request: ResetRequest):
    """Reset environment and start new episode."""
    try:
        task = TaskFactory.create(request.task_level)
        env = EmailTriageEnvironment(task=task)
        observation = env.reset(user_id=request.user_id)

        episode_id = env.episode_id
        environments[episode_id] = env

        return ResetResponse(
            episode_id=episode_id,
            observation=observation,
        )

    except Exception as e:
        traceback.print_exc()
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
        # 🔍 DEBUG INPUT
        print("\n=== STEP REQUEST ===")
        print("Episode:", episode_id)
        print("Request:", request.dict())

        # 🔧 FIX 1: Normalize action type
        action_type_str = request.action_type.lower()

        # 🔧 FIX 2: Safe enum conversion
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action type: {request.action_type}"
            )

        # Build action
        action = Action(
            action_type=action_type,
            email_id=request.email_id,
            parameters=request.parameters,
        )

        print("Parsed Action:", action)

        # Execute step
        observation, reward, done, info = env.step(action)

        print("Step Success → Reward:", reward)

        # 🔧 FIX 3: Preserve history before deleting env
        if done:
            completed_episodes[episode_id] = env.history
            env.is_finished = True

        return StepResponse(
            observation=observation,
            reward=reward,
            done=done,
            info=info,
        )

    except Exception as e:
        print("\n🔥 ERROR IN STEP:")
        traceback.print_exc()
        print("ERROR MESSAGE:", str(e))

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