# server/routes/task_routes.py

from fastapi import APIRouter, HTTPException
from tasks.task_factory import TaskFactory

router = APIRouter()


@router.get("/levels")
def get_levels():
    """Get all available task levels."""
    return {"levels": TaskFactory.get_all_levels()}


@router.get("/{level}")
def get_task_info(level: str):
    """Get info about a specific task level."""
    info = TaskFactory.get_task_info(level)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Task level '{level}' not found"
        )
    return info