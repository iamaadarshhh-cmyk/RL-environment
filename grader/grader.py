# grader/grader.py

from typing import Dict, Any
from env.memory.history import EpisodeHistory
from env.config import PASS_THRESHOLD


# ─── Grader ─────────────────────────────────────────────────
class Grader:

    def grade(self, history: EpisodeHistory) -> Dict[str, Any]:
        """
        Grade a completed episode.
        Returns final score and detailed breakdown.
        """

        if not history.steps:
            return self._empty_grade()

        # ─── Calculate Metrics ───────────────────────────────
        total_steps = len(history.steps)
        correct_steps = sum(1 for s in history.steps if s.result.is_correct)
        partial_steps = sum(1 for s in history.steps if s.result.is_partial)
        wrong_steps = total_steps - correct_steps - partial_steps

        # ─── Calculate Scores ────────────────────────────────
        accuracy = correct_steps / total_steps
        partial_credit = (partial_steps * 0.3) / total_steps
        efficiency = self._efficiency_score(history)
        safety = self._safety_score(history)

        # ─── Final Score ─────────────────────────────────────
        final_score = round(
            (accuracy * 0.5) +        # 50% weight on accuracy
            (partial_credit * 0.2) +  # 20% weight on partial
            (efficiency * 0.2) +      # 20% weight on efficiency
            (safety * 0.1),           # 10% weight on safety
            3
        )

        # ─── Pass or Fail ────────────────────────────────────
        passed = final_score >= PASS_THRESHOLD

        return {
            "episode_id": history.episode_id,
            "task_level": history.task_level,
            "final_score": final_score,
            "passed": passed,
            "breakdown": {
                "accuracy": round(accuracy, 3),
                "partial_credit": round(partial_credit, 3),
                "efficiency": round(efficiency, 3),
                "safety": round(safety, 3),
            },
            "stats": {
                "total_steps": total_steps,
                "correct_steps": correct_steps,
                "partial_steps": partial_steps,
                "wrong_steps": wrong_steps,
                "total_reward": round(history.total_reward, 3),
            },
        }

    # ─── Efficiency Score ────────────────────────────────────
    def _efficiency_score(self, history: EpisodeHistory) -> float:
        """Score based on how efficiently agent solved the task."""
        from env.config import MAX_STEPS
        steps_used = len(history.steps)
        return round(1.0 - (steps_used / MAX_STEPS), 3)

    # ─── Safety Score ────────────────────────────────────────
    def _safety_score(self, history: EpisodeHistory) -> float:
        """Score based on how safely agent handled emails."""
        from env.models.actions import ActionType

        if not history.steps:
            return 1.0

        unsafe_actions = 0
        for step in history.steps:
            action_type = step.action.action_type
            email = step.result.metadata.get("email_category", "")

            # Penalize replying or forwarding spam
            if action_type in [ActionType.REPLY, ActionType.FORWARD]:
                if email == "spam":
                    unsafe_actions += 1

        safety = 1.0 - (unsafe_actions / len(history.steps))
        return round(safety, 3)

    # ─── Empty Grade ─────────────────────────────────────────
    def _empty_grade(self) -> Dict[str, Any]:
        """Return empty grade if no steps recorded."""
        return {
            "episode_id": None,
            "task_level": None,
            "final_score": 0.0,
            "passed": False,
            "breakdown": {
                "accuracy": 0.0,
                "partial_credit": 0.0,
                "efficiency": 0.0,
                "safety": 0.0,
            },
            "stats": {
                "total_steps": 0,
                "correct_steps": 0,
                "partial_steps": 0,
                "wrong_steps": 0,
                "total_reward": 0.0,
            },
        }





## What it does in one line
# > `Grader` gives the **final report card** at the end of an episode — a score from 0 to 1. 📊

# ---

# ## How final score is calculated
# ```
# final_score =
#     accuracy      × 50%   ← most important
#     partial_credit × 20%  ← some credit for close answers
#     efficiency     × 20%  ← how fast was the agent?
#     safety         × 10%  ← how safe were the decisions?