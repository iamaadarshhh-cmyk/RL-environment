# env/memory/history.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from env.models.actions import Action, ActionResult


# ─── Single Step Record ─────────────────────────────────────
@dataclass
class StepRecord:
    step_number: int                    # Which step this was
    email_id: str                       # Which email was acted on
    action: Action                      # What action was taken
    result: ActionResult                # What happened
    reward: float                       # Reward earned
    timestamp: datetime = field(default_factory=datetime.now)  # When it happened
    notes: str = ""                     # Optional notes


# ─── Episode History ────────────────────────────────────────
@dataclass
class EpisodeHistory:
    episode_id: str                     # Unique episode ID
    task_level: str                     # easy / medium / hard
    steps: List[StepRecord] = field(default_factory=list)  # All steps taken
    total_reward: float = 0.0          # Total reward accumulated
    is_complete: bool = False           # Is episode finished?
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def add_step(self, step: StepRecord):
        """Add a new step to history."""
        self.steps.append(step)
        self.total_reward += step.reward

    def get_last_step(self) -> Optional[StepRecord]:
        """Get the most recent step."""
        if self.steps:
            return self.steps[-1]
        return None

    def get_last_n_steps(self, n: int) -> List[StepRecord]:
        """Get last n steps."""
        return self.steps[-n:]

    def complete(self):
        """Mark episode as complete."""
        self.is_complete = True
        self.end_time = datetime.now()

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the episode."""
        return {
            "episode_id": self.episode_id,
            "task_level": self.task_level,
            "total_steps": len(self.steps),
            "total_reward": self.total_reward,
            "is_complete": self.is_complete,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }




# ## What each part does

# ### 📝 `StepRecord`
# Records **one single step** the agent took:
# ```
# Step 3 → agent read email_002 → got reward 1.0 → at 10:35am
# ```

# Think of it like **one row in a diary** of what the agent did.

# ---

# ### 📖 `EpisodeHistory`
# Records the **entire episode** from start to finish — a collection of all `StepRecord`s.

# Think of it like the **full diary** of one complete game session.

# It has 4 helper methods:

# | Method | What it does |
# |---|---|
# | `add_step()` | Adds a new step and updates total reward |
# | `get_last_step()` | Returns what the agent did most recently |
# | `get_last_n_steps(n)` | Returns last n steps (uses `OBSERVATION_HISTORY` from config) |
# | `complete()` | Marks episode as finished, records end time |
# | `summary()` | Returns a neat dictionary of episode stats |

# ---

# ## How it connects to other files
# ```
# environment.py
#      ↓
# Agent takes Action
#      ↓
# ActionResult returned
#      ↓
# StepRecord created  ←─ history.py
#      ↓
# Added to EpisodeHistory
#      ↓
# trajectory_logger.py saves it to disk