# tasks/definitions/hard.py

import uuid
from typing import Optional
from env.models.state import Email
from env.models.actions import ActionType


class HardTask:

    level = "hard"

    def __init__(self, task_id: Optional[str] = None):
        self.task_id = task_id or f"hard_{uuid.uuid4().hex[:6]}"
        self.description = "Handle complex multi step email workflows"

    def get_expected_action(self, email: Email) -> ActionType:
        """Return expected action for given email."""

        if email.category == "spam":
            return ActionType.MARK_SPAM

        elif email.category == "work":
            subject = email.subject.lower()
            body = email.body.lower()

            if any(word in subject for word in
                   ["urgent", "critical", "asap"]):
                return ActionType.ESCALATE

            elif any(word in body for word in
                     ["summarize", "summary", "brief", "overview"]):
                return ActionType.SUMMARIZE

            elif any(word in subject for word in
                     ["deadline", "overdue", "pending"]):
                return ActionType.DEFER

            elif any(word in subject for word in
                     ["meeting", "presentation", "review"]):
                return ActionType.REPLY

            else:
                return ActionType.FORWARD

        elif email.category == "personal":
            subject = email.subject.lower()
            body = email.body.lower()

            if any(word in subject for word in
                   ["urgent", "emergency", "help"]):
                return ActionType.REPLY

            elif any(word in body for word in
                     ["summary", "update", "news"]):
                return ActionType.SUMMARIZE

            else:
                return ActionType.DEFER

        return ActionType.READ  # default