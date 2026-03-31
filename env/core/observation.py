# env/core/observation.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from env.models.state import Email, AgentState
from env.models.actions import ActionType
from env.config import VALID_ACTIONS, OBSERVATION_HISTORY


# ─── Observation Builder ────────────────────────────────────
class ObservationBuilder:

    @staticmethod
    def build(state: AgentState) -> Dict[str, Any]:
        """Build observation from current agent state."""

        email = state.current_email

        if email is None:
            return ObservationBuilder._empty_observation(state)

        return {
            # ─── Current Email Info ─────────────────────────
            "email_id": email.email_id,
            "subject": email.subject,
            "sender": email.sender,
            "body_preview": email.body[:200],         # First 200 chars only
            "category_hint": ObservationBuilder._category_hint(email),

            # ─── Inbox Status ───────────────────────────────
            "unread_count": state.inbox.unread_count,
            "total_emails": state.inbox.total_emails,

            # ─── Agent Status ───────────────────────────────
            "step_count": state.step_count,
            "total_reward": state.total_reward,
            "is_done": state.is_done,

            # ─── Available Actions ──────────────────────────
            "available_actions": ObservationBuilder._get_available_actions(email),

            # ─── Recent History ─────────────────────────────
            "recent_actions": state.action_history[-OBSERVATION_HISTORY:],
        }

    @staticmethod
    def _empty_observation(state: AgentState) -> Dict[str, Any]:
        """Return observation when inbox is empty."""
        return {
            "email_id": None,
            "subject": "No emails",
            "sender": None,
            "body_preview": "Your inbox is empty.",
            "category_hint": None,
            "unread_count": 0,
            "total_emails": state.inbox.total_emails,
            "step_count": state.step_count,
            "total_reward": state.total_reward,
            "is_done": True,
            "available_actions": [],
            "recent_actions": state.action_history[-OBSERVATION_HISTORY:],
        }

    @staticmethod
    def _get_available_actions(email: Email) -> List[str]:
        """Get available actions based on email status."""
        actions = VALID_ACTIONS.copy()

        # Remove actions that don't make sense
        if email.is_read:
            actions = [a for a in actions if a != "read"]
        if email.is_replied:
            actions = [a for a in actions if a != "reply"]
        if email.is_deleted:
            actions = [a for a in actions if a != "delete"]

        return actions

    @staticmethod
    def _category_hint(email: Email) -> Optional[str]:
        """Give agent a subtle hint about email category."""
        hints = {
            "spam": "suspicious",
            "work": "professional",
            "personal": "casual",
        }
        return hints.get(email.category, None)