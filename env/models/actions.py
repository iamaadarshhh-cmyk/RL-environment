# env/models/actions.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


# ─── Action Types ───────────────────────────────────────────
class ActionType(Enum):
    READ = "read"               # Open and read an email
    REPLY = "reply"             # Reply to an email
    FORWARD = "forward"         # Forward to someone else
    DELETE = "delete"           # Delete the email
    ARCHIVE = "archive"         # Archive for later
    LABEL = "label"             # Add a label/tag
    MARK_SPAM = "mark_spam"     # Mark as spam
    ESCALATE = "escalate"       # Escalate to higher priority
    DEFER = "defer"             # Postpone handling
    SUMMARIZE = "summarize"     # Summarize the email


# ─── Single Action ──────────────────────────────────────────
@dataclass
class Action:
    action_type: ActionType            # What action to take
    email_id: str                      # Which email to act on
    parameters: Dict[str, Any] = field(default_factory=dict)  # Extra info
    # Examples of parameters:
    # reply    → {"message": "Thanks for your email!"}
    # forward  → {"to": "manager@company.com"}
    # label    → {"label_name": "urgent"}
    # defer    → {"defer_until": "2024-01-15"}


# ─── Action Result ──────────────────────────────────────────
@dataclass
class ActionResult:
    success: bool                      # Did the action succeed?
    action_type: ActionType            # What action was taken
    email_id: str                      # Which email was acted on
    reward: float = 0.0               # Reward earned from this action
    message: str = ""                  # Human readable result message
    is_correct: bool = False           # Was it the correct action?
    is_partial: bool = False           # Was it partially correct?
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extra info


# ─── Action Validator ───────────────────────────────────────
class ActionValidator:

    VALID_ACTIONS = [action.value for action in ActionType]

    @staticmethod
    def is_valid(action_type: str) -> bool:
        """Check if action type is valid."""
        return action_type in ActionValidator.VALID_ACTIONS

    @staticmethod
    def requires_parameters(action_type: ActionType) -> bool:
        """Check if action needs extra parameters."""
        return action_type in [
            ActionType.REPLY,
            ActionType.FORWARD,
            ActionType.LABEL,
            ActionType.DEFER,
        ]

    @staticmethod
    def validate_parameters(action: Action) -> bool:
        """Check if required parameters are provided."""
        required = {
            ActionType.REPLY: ["message"],
            ActionType.FORWARD: ["to"],
            ActionType.LABEL: ["label_name"],
            ActionType.DEFER: ["defer_until"],
        }
        if action.action_type in required:
            for key in required[action.action_type]:
                if key not in action.parameters:
                    return False
        return True




# ## What each part does

# ### 🎮 `ActionType` (Enum)
# Defines all **allowed actions** as a safe enumeration. Instead of using raw strings like `"read"` everywhere (which can have typos), you use `ActionType.READ` — Python will catch any mistakes. ✅

# ### 📦 `Action`
# Represents **one action the agent wants to take**. It has:
# - `action_type` → what to do (e.g. REPLY)
# - `email_id` → which email to do it on
# - `parameters` → extra details needed (e.g. reply message text)

# ### 📊 `ActionResult`
# Represents **what happened after** the agent took an action:
# - Did it succeed?
# - Was it correct?
# - How much reward was earned?

# ### 🔍 `ActionValidator`
# A helper class that **checks if an action is valid** before executing it:
# - Is the action type allowed?
# - Does it have the required parameters?

# ---

# ## How they connect together
# ```
# Agent decides → Action → ActionValidator checks → 
# Environment executes → ActionResult returned → Reward given