# env/core/transition.py

from typing import Tuple, Optional
from env.models.state import AgentState, Email
from env.models.actions import Action, ActionResult, ActionType, ActionValidator
from env.config import (
    MAX_STEPS,
    REWARD_CORRECT_ACTION,
    REWARD_WRONG_ACTION,
    REWARD_PARTIAL_CREDIT,
    REWARD_STEP_PENALTY,
)


# ─── Transition Engine ──────────────────────────────────────
class TransitionEngine:

    def step(
        self,
        state: AgentState,
        action: Action,
        expected_action: ActionType,
    ) -> Tuple[AgentState, ActionResult]:
        """
        Take one step in the environment.
        Returns updated state and action result.
        """

        # ─── Validate Action ────────────────────────────────
        if not ActionValidator.is_valid(action.action_type.value):
            result = self._invalid_action_result(action)
            return state, result

        if not ActionValidator.validate_parameters(action):
            result = self._missing_params_result(action)
            return state, result

        # ─── Execute Action ─────────────────────────────────
        state, result = self._execute_action(state, action, expected_action)

        # ─── Apply Step Penalty ─────────────────────────────
        result.reward += REWARD_STEP_PENALTY

        # ─── Update State ───────────────────────────────────
        state.step_count += 1
        state.total_reward += result.reward
        state.action_history.append(action.action_type.value)

        # ─── Check if Done ──────────────────────────────────
        if state.step_count >= MAX_STEPS:
            state.is_done = True

        if state.inbox.unread_count <= 0:
            state.is_done = True

        return state, result

    # ─── Execute Action ─────────────────────────────────────
    def _execute_action(
        self,
        state: AgentState,
        action: Action,
        expected_action: ActionType,
    ) -> Tuple[AgentState, ActionResult]:
        """Execute action and return updated state + result."""

        email = state.current_email
        is_correct = action.action_type == expected_action
        is_partial = self._is_partial(action.action_type, expected_action)

        # ─── Calculate Reward ────────────────────────────────
        if is_correct:
            reward = REWARD_CORRECT_ACTION
        elif is_partial:
            reward = REWARD_PARTIAL_CREDIT
        else:
            reward = REWARD_WRONG_ACTION

        # ─── Update Email Status ─────────────────────────────
        if action.action_type == ActionType.READ:
            email.is_read = True

        elif action.action_type == ActionType.REPLY:
            email.is_replied = True
            email.is_read = True

        elif action.action_type == ActionType.DELETE:
            email.is_deleted = True
            state.inbox.unread_count -= 1

        elif action.action_type == ActionType.ARCHIVE:
            email.is_read = True
            state.inbox.unread_count -= 1

        elif action.action_type == ActionType.MARK_SPAM:
            email.is_deleted = True
            state.inbox.unread_count -= 1

        elif action.action_type == ActionType.FORWARD:
            email.is_read = True

        elif action.action_type == ActionType.LABEL:
            label = action.parameters.get("label_name", "unlabeled")
            email.labels.append(label)

        elif action.action_type == ActionType.ESCALATE:
            email.is_read = True
            email.labels.append("escalated")

        elif action.action_type == ActionType.DEFER:
            email.is_read =True
            email.labels.append("deferred")

        elif action.action_type == ActionType.SUMMARIZE:
            email.is_read = True

        # ─── Move to Next Email ──────────────────────────────
        state.current_email = self._next_email(state)

        result = ActionResult(
            success=True,
            action_type=action.action_type,
            email_id=action.email_id,
            reward=reward,
            message=f"{action.action_type.value} executed successfully",
            is_correct=is_correct,
            is_partial=is_partial,
        )

        return state, result

    # ─── Partial Credit Check ───────────────────────────────
    def _is_partial(
        self,
        taken: ActionType,
        expected: ActionType
    ) -> bool:
        """Check if action deserves partial credit."""
        partial_matches = {
            ActionType.DELETE: [ActionType.MARK_SPAM, ActionType.ARCHIVE],
            ActionType.MARK_SPAM: [ActionType.DELETE, ActionType.ARCHIVE],
            ActionType.ARCHIVE: [ActionType.DELETE, ActionType.MARK_SPAM],
            ActionType.REPLY: [ActionType.FORWARD, ActionType.SUMMARIZE],
            ActionType.FORWARD: [ActionType.REPLY, ActionType.ESCALATE],
        }
        return taken in partial_matches.get(expected, [])

    # ─── Next Email ─────────────────────────────────────────
    def _next_email(self, state: AgentState) -> Optional[Email]:
        """Move to next unread email in inbox."""
        for email in state.inbox.emails:
            if not email.is_read and not email.is_deleted:
                return email
        return None

    # ─── Invalid Action Result ──────────────────────────────
    def _invalid_action_result(self, action: Action) -> ActionResult:
        return ActionResult(
            success=False,
            action_type=action.action_type,
            email_id=action.email_id,
            reward=REWARD_WRONG_ACTION,
            message="Invalid action type",
            is_correct=False,
        )

    # ─── Missing Params Result ──────────────────────────────
    def _missing_params_result(self, action: Action) -> ActionResult:
        return ActionResult(
            success=False,
            action_type=action.action_type,
            email_id=action.email_id,
            reward=REWARD_WRONG_ACTION,
            message="Missing required parameters",
            is_correct=False,
        )


## What it does in one line
# > `TransitionEngine` is the **engine of the environment** — it takes an action, updates the state, and returns the result. ⚙️

# ---

# ## Flow
# ```
# Agent sends Action
#       ↓
# Validate action        ← is it allowed? has parameters?
#       ↓
# Execute action         ← update email status
#       ↓
# Calculate reward       ← correct / partial / wrong
#       ↓
# Apply step penalty     ← -0.01 every step
#       ↓
# Update state           ← step count, total reward, history
#       ↓
# Move to next email     ← pick next unread email
#       ↓
# Return new State + ActionResult