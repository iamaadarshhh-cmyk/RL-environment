# server/schemas.py

from pydantic import BaseModel
from typing import Optional, Dict, Any


# ─── Request Schemas ────────────────────────────────────────
class ResetRequest(BaseModel):
    user_id: str = "agent"
    task_level: str = "easy"


class StepRequest(BaseModel):
    action_type: str
    email_id: str
    parameters: Dict[str, Any] = {}


class GradeRequest(BaseModel):
    episode_id: str


# ─── Response Schemas ───────────────────────────────────────
class ResetResponse(BaseModel):
    episode_id: str
    observation: Dict[str, Any]
    message: str = "Environment reset successfully"


class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any]


class GradeResponse(BaseModel):
    episode_id: str
    final_score: float
    passed: bool
    breakdown: Dict[str, Any]
    stats: Dict[str, Any]


class TaskInfoResponse(BaseModel):
    level: str
    description: str
    actions: list
    reward_threshold: float