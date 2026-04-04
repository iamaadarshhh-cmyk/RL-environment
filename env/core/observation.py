# env/core/observation.py
 
from typing import List
from env.models.state import Email, AgentState, Observation
from env.config import VALID_ACTIONS, OBSERVATION_HISTORY
 
 
class ObservationBuilder:
    """Builds structured Observation objects from AgentState."""
 
    @staticmethod
    def build(state: AgentState) -> Observation:
        """Build observation from current agent state."""
        email = state.current_email
 
        if email is None:
            return ObservationBuilder._empty_observation(state)
 
        return Observation(
            email_id=email.email_id,
            subject=email.subject,
            sender=email.sender,
            body_preview=email.body[:200],
            unread_count=state.inbox.unread_count,
            total_emails=state.inbox.total_emails,
            step_count=state.step_count,
            total_reward=state.total_reward,
            is_done=state.is_done,
            available_actions=ObservationBuilder._get_available_actions(email),
            recent_actions=state.action_history[-OBSERVATION_HISTORY:],
            signals={
                "urgency": ObservationBuilder._urgency_score(email),
                "spam_score": ObservationBuilder._spam_score(email),
            },
        )
 
    @staticmethod
    def _empty_observation(state: AgentState) -> Observation:
        """Return observation when inbox is empty or episode is done.
        Shape is identical to normal observation — no extra/missing keys.
        """
        return Observation(
            email_id=None,
            subject="No emails",
            sender=None,
            body_preview="Your inbox is empty.",
            unread_count=0,
            total_emails=state.inbox.total_emails,
            step_count=state.step_count,
            total_reward=state.total_reward,
            is_done=True,
            available_actions=[],
            recent_actions=state.action_history[-OBSERVATION_HISTORY:],
            # FIX: signals was missing from _empty_observation —
            # caused inconsistent observation shape between empty and non-empty inbox
            signals={"urgency": 0.0, "spam_score": 0.0},
        )
 
    @staticmethod
    def _get_available_actions(email: Email) -> List[str]:
        """Get available actions based on email status."""
        actions = VALID_ACTIONS.copy()

        if getattr(email, "is_read", False):
            actions = [a for a in actions if a != "read"]
        if getattr(email, "is_replied", False):
            actions = [a for a in actions if a != "reply"]
        if getattr(email, "is_deleted", False):
            actions = [a for a in actions if a != "delete"]
        if getattr(email, "is_archived", False):
            actions = [a for a in actions if a != "archive"]
        if getattr(email, "is_spam", False):
            actions = [a for a in actions if a != "mark_spam"]

        return actions
 
    @staticmethod
    def _urgency_score(email: Email) -> float:
        """Score 0-1 based on urgency keyword presence."""
        text = (email.subject + " " + email.body).lower()
        urgency_words = [
            "urgent", "asap", "immediately", "critical",
            "deadline", "today", "now", "important",
        ]
        # FIX: was checking `if w in words` (tokenized list) which missed
        # "urgent," or "important!" due to punctuation. Check substring
        # in raw text instead — consistent with _spam_score behaviour.
        matches = sum(1 for w in urgency_words if w in text)
        return min(matches / 2, 1.0)
 
    @staticmethod
    def _spam_score(email: Email) -> float:
        """Score 0-1 based on spam pattern presence."""
        text = (email.subject + " " + email.body).lower()
        spam_patterns = [
            "win", "winner", "free", "click", "prize", "offer",
            "urgent", "verify", "account", "suspended",
            "lottery", "work from home", "earn", "income",
            "limited time", "act now", "guaranteed",
            "back taxes", "owe", "penalty",
            "medication", "cheap", "pharmacy", "pills",
        ]
        matches = sum(1 for p in spam_patterns if p in text)
        return min(matches / 3, 1.0)