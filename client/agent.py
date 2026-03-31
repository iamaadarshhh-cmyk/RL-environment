# client/agent.py

import random
from typing import Dict, Any, List
from client.client import EmailTriageClient


# ─── Base Agent ─────────────────────────────────────────────
class BaseAgent:

    def __init__(self, client: EmailTriageClient):
        self.client = client

    def select_action(self, observation: Dict[str, Any]) -> str:
        """Select action based on observation."""
        raise NotImplementedError


# ─── Random Agent ───────────────────────────────────────────
class RandomAgent(BaseAgent):
    """Agent that selects random actions."""

    def select_action(self, observation: Dict[str, Any]) -> str:
        """Select a random action from available actions."""
        available = observation.get("available_actions", [])
        if not available:
            return "read"
        return random.choice(available)


# ─── Rule Based Agent ───────────────────────────────────────
class RuleBasedAgent(BaseAgent):
    """Agent that uses simple rules to select actions."""

    def select_action(self, observation: Dict[str, Any]) -> str:
        """Select action based on simple rules."""

        category_hint = observation.get("category_hint", "")
        subject = observation.get("subject", "").lower()
        available = observation.get("available_actions", [])

        # Rule 1 — suspicious email → mark spam
        if category_hint == "suspicious":
            if "mark_spam" in available:
                return "mark_spam"

        # Rule 2 — professional + urgent → escalate
        if category_hint == "professional":
            if any(word in subject for word in
                   ["urgent", "asap", "critical"]):
                if "escalate" in available:
                    return "escalate"

        # Rule 3 — professional + meeting → reply
        if category_hint == "professional":
            if any(word in subject for word in
                   ["meeting", "call", "presentation"]):
                if "reply" in available:
                    return "reply"

        # Rule 4 — casual → read
        if category_hint == "casual":
            if "read" in available:
                return "read"

        # Default → read
        if "read" in available:
            return "read"

        return available[0] if available else "read"


# ─── Agent Runner ───────────────────────────────────────────
class AgentRunner:

    def __init__(
        self,
        agent: BaseAgent,
        client: EmailTriageClient,
    ):
        self.agent = agent
        self.client = client

    def run(
        self,
        task_level: str = "easy",
        user_id: str = "agent",
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """Run a full episode."""

        # Reset environment
        data = self.client.reset(
            user_id=user_id,
            task_level=task_level,
        )
        observation = data["observation"]
        episode_id = data["episode_id"]

        if verbose:
            print(f"\n{'='*50}")
            print(f"Episode  : {episode_id}")
            print(f"Task     : {task_level}")
            print(f"{'='*50}")

        total_reward = 0.0
        step = 0
        done = False

        # Run episode
        while not done:
            # Select action

            if observation.get("is_done"):
                break
            
            action_type = self.agent.select_action(observation)
            email_id = observation.get("email_id", "")

            if verbose:
                print(f"\nStep {step + 1}")
                print(f"Email   : {observation.get('subject', '')}")
                print(f"Hint    : {observation.get('category_hint', '')}")
                print(f"Action  : {action_type}")

            # Take step
            result = self.client.step(
                action_type=action_type,
                email_id=email_id,
            )

            observation = result["observation"]
            reward = result["reward"]
            done = result["done"]
            info = result["info"]

            total_reward += reward
            step += 1

            if verbose:
                print(f"Reward  : {reward:.3f}")
                print(f"Correct : {info.get('is_correct', False)}")

        # Get final grade
        grade = self.client.grade()

        if verbose:
            print(f"\n{'='*50}")
            print(f"Episode Complete!")
            print(f"Steps        : {step}")
            print(f"Total Reward : {total_reward:.3f}")
            print(f"Final Score  : {grade['final_score']}")
            print(f"Passed       : {grade['passed']}")
            print(f"{'='*50}\n")

        return grade