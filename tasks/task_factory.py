# tasks/task_factory.py

from typing import Optional
from tasks.definitions.easy import EasyTask
from tasks.definitions.medium import MediumTask
from tasks.definitions.hard import HardTask
from env.config import TASK_LEVELS


# ─── Task Factory ───────────────────────────────────────────
class TaskFactory:

    @staticmethod
    def create(level: str, task_id: Optional[str] = None):
        """
        Create and return a task based on difficulty level.
        """

        # Validate level
        if level not in TASK_LEVELS:
            raise ValueError(
                f"Invalid task level '{level}'. "
                f"Choose from: {TASK_LEVELS}"
            )

        # Create task based on level
        if level == "easy":
            return EasyTask(task_id=task_id)

        elif level == "medium":
            return MediumTask(task_id=task_id)

        elif level == "hard":
            return HardTask(task_id=task_id)

    @staticmethod
    def get_all_levels():
        """Return all available task levels."""
        return TASK_LEVELS

    @staticmethod
    def get_task_info(level: str) -> dict:
        """Return info about a specific task level."""
        info = {
            "easy": {
                "description": "Simple email classification",
                "actions": ["read", "delete", "mark_spam"],
                "reward_threshold": 0.6,
            },
            "medium": {
                "description": "Context aware email handling",
                "actions": ["reply", "forward", "archive", "label"],
                "reward_threshold": 0.7,
            },
            "hard": {
                "description": "Multi step email workflows",
                "actions": ["escalate", "defer", "summarize"],
                "reward_threshold": 0.8,
            },
        }
        return info.get(level, {})