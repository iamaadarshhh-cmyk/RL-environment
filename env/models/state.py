# env/models/state.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─── Single Email ───────────────────────────────────────────
@dataclass
class Email:
    email_id: str                          # Unique ID e.g. "email_001"
    subject: str                           # Email subject line
    sender: str                            # Sender email address
    recipient: str                         # Recipient email address
    body: str                              # Email body text
    timestamp: datetime                    # When it was received
    category: Optional[str] = None        # spam / work / personal
    is_read: bool = False                  # Has it been read?
    is_replied: bool = False               # Has it been replied to?
    is_deleted: bool = False               # Has it been deleted?
    labels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ─── Inbox ──────────────────────────────────────────────────
@dataclass
class Inbox:
    inbox_id: str                          # Unique inbox ID
    owner: str                             # Owner of the inbox
    emails: List[Email] = field(default_factory=list)
    total_emails: int = 0                  # Total email count
    unread_count: int = 0                  # Unread email count


# ─── Agent's Current State ──────────────────────────────────
@dataclass
class AgentState:
    inbox: Inbox                           # Current inbox
    current_email: Optional[Email] = None # Email agent is looking at
    step_count: int = 0                    # Steps taken so far
    total_reward: float = 0.0             # Accumulated reward
    is_done: bool = False                  # Is episode finished?
    action_history: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)


# ─── Observation (what agent sees) ──────────────────────────
@dataclass
class Observation:
    email_id: str                          # Which email
    subject: str                           # Subject of email
    sender: str                            # Who sent it
    body_preview: str                      # First 200 chars of body
    available_actions: List[str] = field(default_factory=list)
    step_count: int = 0                    # Current step number
    unread_count: int = 0                  # Remaining unread emails
    last_action: Optional[str] = None     # What agent did last
    last_reward: float = 0.0              # Reward from last action