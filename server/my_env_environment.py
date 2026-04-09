# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Complaint-resolution environment implementation.

The environment presents a customer complaint, accepts agent replies, and
assigns reward based on simulated or explicit client feedback.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata

try:
    from ..models import MyAction, MyObservation, MyState
except ImportError:
    from models import MyAction, MyObservation, MyState

from tasks import TASK_INDEX, get_task_dicts


@dataclass(frozen=True)
class ComplaintScenario:
    complaint_id: str
    task_name: str
    task_description: str
    difficulty: str
    category: str
    customer_name: str
    complaint_text: str
    required_keywords: tuple[str, ...]
    resolution_keywords: tuple[str, ...]
    positive_feedback: tuple[str, ...]
    neutral_feedback: tuple[str, ...]
    negative_feedback: tuple[str, ...]
    max_steps: int
    success_threshold: float


SCENARIOS: tuple[ComplaintScenario, ...] = (
    ComplaintScenario(
        complaint_id="easy",
        task_name="Late Delivery Recovery",
        task_description=(
            "Handle an urgent late-delivery complaint, acknowledge the frustration, "
            "reference tracking details, and offer a concrete recovery path."
        ),
        difficulty="easy",
        category="delivery",
        customer_name="Maya",
        complaint_text=(
            "My package was supposed to arrive three days ago, and the tracking "
            "has not updated. I need it urgently and want to know what you will do."
        ),
        required_keywords=("tracking", "delivery", "delay", "urgent"),
        resolution_keywords=("refund", "replacement", "expedite", "escalate"),
        positive_feedback=(
            "Thanks, that helps.",
            "That sounds fair. Please go ahead with that.",
            "Okay, that resolves my issue.",
        ),
        neutral_feedback=(
            "I appreciate the response, but I still need the next steps clearly.",
            "That helps a little, but I need more detail.",
        ),
        negative_feedback=(
            "That does not solve the delay. I still need help.",
            "I am frustrated because you have not explained what happens next.",
        ),
        max_steps=5,
        success_threshold=0.72,
    ),
    ComplaintScenario(
        complaint_id="easy2",
        task_name="Wrong Item Exchange",
        task_description=(
            "Resolve a wrong-item shipment complaint with a correct exchange and "
            "a no-cost return process."
        ),
        difficulty="easy",
        category="product",
        customer_name="Kabir",
        complaint_text=(
            "I ordered a black medium jacket, but I received a blue small one "
            "instead. I need the correct item sent quickly and I should not be "
            "charged for returning your mistake."
        ),
        required_keywords=("wrong", "exchange", "return", "correct"),
        resolution_keywords=("replacement", "exchange", "pickup", "return label"),
        positive_feedback=(
            "An exchange with a prepaid return label works for me.",
            "Thank you, that fixes the wrong item issue.",
            "Okay, please send the correct jacket and the return label.",
        ),
        neutral_feedback=(
            "Please confirm when the correct item will ship.",
            "I need the exchange steps explained clearly.",
        ),
        negative_feedback=(
            "You still have not explained how I return the wrong item.",
            "I need the correct item, not another delay.",
        ),
        max_steps=5,
        success_threshold=0.71,
    ),
    ComplaintScenario(
        complaint_id="medium",
        task_name="Damaged Item Refund Or Replacement",
        task_description=(
            "Resolve a damaged-product complaint without charging return shipping, "
            "and propose a refund or replacement with clear logistics."
        ),
        difficulty="medium",
        category="product",
        customer_name="Rohan",
        complaint_text=(
            "The blender I received is cracked and unsafe to use. I want a quick "
            "replacement or refund, and I do not want to pay return shipping."
        ),
        required_keywords=("damaged", "replacement", "refund", "return"),
        resolution_keywords=("refund", "replacement", "pickup", "return label"),
        positive_feedback=(
            "A free replacement and pickup works for me.",
            "Thank you, that resolves it.",
            "That sounds good. Please process it.",
        ),
        neutral_feedback=(
            "I need confirmation about the return shipping.",
            "Please explain exactly how the replacement will happen.",
        ),
        negative_feedback=(
            "Why should I pay for returning a damaged product?",
            "That is not acceptable. I need a proper solution.",
        ),
        max_steps=6,
        success_threshold=0.75,
    ),
    ComplaintScenario(
        complaint_id="medium2",
        task_name="Service Outage Escalation",
        task_description=(
            "Handle a service outage complaint by acknowledging the disruption, "
            "sharing a restoration path, and offering escalation or compensation."
        ),
        difficulty="medium",
        category="service",
        customer_name="Neha",
        complaint_text=(
            "My home internet has been down since yesterday evening and I work "
            "remotely. I need service restored quickly and want to know what "
            "callback or service credit you can offer."
        ),
        required_keywords=("service", "outage", "restore", "callback"),
        resolution_keywords=("credit", "callback", "technician", "escalate"),
        positive_feedback=(
            "A same-day callback and service credit works for me.",
            "Thanks, that outage plan helps.",
            "Okay, please send the technician and apply the credit.",
        ),
        neutral_feedback=(
            "I still need a restoration timeframe.",
            "Please confirm when the technician or callback will happen.",
        ),
        negative_feedback=(
            "You still have not told me when service will be restored.",
            "This outage is affecting my work and I need a real solution.",
        ),
        max_steps=6,
        success_threshold=0.74,
    ),
    ComplaintScenario(
        complaint_id="hard",
        task_name="Duplicate Charge Resolution",
        task_description=(
            "Reverse a duplicate subscription charge, explain the next billing step, "
            "and give the customer confidence the issue will not recur."
        ),
        difficulty="hard",
        category="billing",
        customer_name="Aisha",
        complaint_text=(
            "I was charged twice for the same subscription renewal. I need the "
            "duplicate charge reversed and confirmation that it will not happen again."
        ),
        required_keywords=("charge", "billing", "refund", "duplicate"),
        resolution_keywords=("refund", "reverse", "billing team", "escalate"),
        positive_feedback=(
            "If you reverse the extra charge, that resolves it.",
            "Thanks for explaining the billing reversal.",
            "Okay, that is the resolution I needed.",
        ),
        neutral_feedback=(
            "I need a timeframe for the refund.",
            "Please confirm what happens next with the duplicate charge.",
        ),
        negative_feedback=(
            "You still have not addressed the duplicate charge.",
            "This is not helpful unless the billing issue is fixed.",
        ),
        max_steps=7,
        success_threshold=0.73,
    ),
)

SCENARIO_INDEX = {scenario.complaint_id: scenario for scenario in SCENARIOS}
TASK_IDS = tuple(scenario.complaint_id for scenario in SCENARIOS)
EMPATHY_TERMS = (
    "sorry",
    "apologize",
    "apologise",
    "understand",
    "frustrating",
    "inconvenience",
)
CLARIFYING_TERMS = ("could you", "can you", "please share", "confirm", "order number")
DISMISSIVE_TERMS = ("calm down", "not our fault", "policy says no", "nothing we can do")
COMMON_POSITIVE_FEEDBACK = ("thanks", "helpful", "resolved", "works for me", "sounds good")
COMMON_NEGATIVE_FEEDBACK = (
    "not helpful",
    "still need help",
    "not acceptable",
    "frustrated",
    "does not solve",
    "doesn't solve",
)
COMMON_NEUTRAL_FEEDBACK = ("need more detail", "next steps", "timeframe", "please explain")
DEFAULT_RESOLUTION_KEYWORDS = ("refund", "replacement", "escalate", "follow up", "reverse")
DEFAULT_REQUIRED_KEYWORDS = {
    "billing": ("charge", "refund", "invoice", "billing"),
    "delivery": ("delivery", "tracking", "delay", "package"),
    "product": ("replacement", "refund", "damaged", "return"),
    "service": ("callback", "appointment", "escalate", "support"),
}
TASK_SCORE_EPSILON = 0.05


def get_task_catalog() -> list[dict[str, object]]:
    """Return the public benchmark task list for submission validation."""
    task_dicts = {task["task_id"]: task for task in get_task_dicts()}
    catalog: list[dict[str, object]] = []
    for scenario in SCENARIOS:
        task = TASK_INDEX[scenario.complaint_id]
        task_dict = dict(task_dicts[scenario.complaint_id])
        task_dict.update(
            {
                "id": scenario.complaint_id,
                "task_id": scenario.complaint_id,
                "name": scenario.task_name,
                "difficulty": scenario.difficulty,
                "description": scenario.task_description,
                "max_steps": scenario.max_steps,
                "success_threshold": scenario.success_threshold,
                "grader_metadata": {
                    "type": task.grader_type,
                    "field": task.grader_field,
                    "score_range": {"min_exclusive": 0.0, "max_exclusive": 1.0},
                },
            }
        )
        catalog.append(task_dict)
    return catalog


class MyEnvironment(Environment[MyAction, MyObservation, MyState]):
    """Complaint-resolution environment with step-wise reward."""

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        super().__init__()
        self._rng = random.Random()
        self._scenario = SCENARIOS[0]
        self._max_turns = self._scenario.max_steps
        self._chat_history: list[str] = []
        self._state = MyState(
            episode_id=str(uuid4()),
            step_count=0,
            complaint_id="",
            complaint_category="",
            satisfaction_score=0.0,
            resolution_status="open",
            last_customer_sentiment="negative",
            awaiting_customer_response=False,
            pending_agent_message="",
            pending_judge_score=0.0,
        )

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        complaint_id: Optional[str] = None,
        complaint_text: Optional[str] = None,
        complaint_category: Optional[str] = None,
        customer_name: Optional[str] = None,
        **kwargs: object,
    ) -> MyObservation:
        """Reset the environment with either a canned or custom complaint."""
        del kwargs
        if seed is not None:
            self._rng.seed(seed)

        self._scenario = self._select_scenario(
            complaint_id=complaint_id or task_id,
            complaint_text=complaint_text,
            complaint_category=complaint_category,
            customer_name=customer_name,
        )
        self._max_turns = self._scenario.max_steps
        self._chat_history = [
            f"Customer: {self._scenario.customer_name}: {self._scenario.complaint_text}"
        ]
        self._state = MyState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            complaint_id=self._scenario.complaint_id,
            complaint_category=self._scenario.category,
            satisfaction_score=0.0,
            resolution_status="open",
            last_customer_sentiment="negative",
            awaiting_customer_response=False,
            pending_agent_message="",
            pending_judge_score=0.0,
        )
        return self._build_observation(
            latest_customer_message=(
                f"{self._scenario.customer_name}: {self._scenario.complaint_text}"
            ),
            latest_agent_message="",
            customer_sentiment="negative",
            reward=0.0,
            done=False,
            metadata={
                "customer_name": self._scenario.customer_name,
                "feedback_source": "environment",
            },
            suggested_next_action=(
                "Acknowledge the complaint, show empathy, and offer a concrete next step."
            ),
        )

    def get_metadata(self) -> EnvironmentMetadata:
        """Return human-friendly metadata for discovery surfaces."""
        return EnvironmentMetadata(
            name="Complaint Resolution Benchmark",
            description=(
                "A five-task customer-support benchmark where an agent resolves "
                "delivery, product, billing, and service complaints and receives a "
                "deterministic grader_score in the open interval (0, 1)."
            ),
            version="1.0.0",
            author="hackathon-submission",
        )

    def step(
        self,
        action: MyAction,
        timeout_s: Optional[float] = None,
        **kwargs: object,
    ) -> MyObservation:  # type: ignore[override]
        """Process either an agent reply or a real customer message."""
        del timeout_s, kwargs
        self._state.step_count += 1

        agent_message = (action.agent_message or "").strip()
        customer_message = self._extract_customer_message(action)

        if agent_message and action.await_customer_response and not customer_message:
            judge_reward, reasons, _, _ = self._evaluate_agent_message(agent_message)
            self._chat_history.append(f"Agent: {agent_message}")
            self._state.pending_agent_message = agent_message
            self._state.pending_judge_score = judge_reward
            self._state.awaiting_customer_response = True
            self._state.resolution_status = "in_progress"
            return self._build_observation(
                latest_customer_message=self._latest_message_for_role("Customer"),
                latest_agent_message=agent_message,
                customer_sentiment=self._state.last_customer_sentiment,
                reward=0.0,
                done=False,
                metadata={
                    "customer_name": self._scenario.customer_name,
                    "feedback_source": "pending",
                    "reward_reason": "; ".join(reasons)
                    + "; awaiting real customer response before final reward",
                    "step": self._state.step_count,
                },
                suggested_next_action=(
                    "Collect the real customer reply and send it as customer_message."
                ),
            )

        if not agent_message and customer_message:
            if self._state.awaiting_customer_response and self._state.pending_agent_message:
                return self._finalize_customer_feedback(
                    agent_message=self._state.pending_agent_message,
                    customer_message=customer_message,
                    feedback_score=action.feedback_score,
                    mark_resolved=action.mark_resolved,
                    feedback_source="customer",
                    append_agent_history=False,
                )
            return self._record_customer_context(
                customer_message=customer_message,
                feedback_score=action.feedback_score,
                mark_resolved=action.mark_resolved,
            )

        if agent_message and customer_message:
            return self._finalize_customer_feedback(
                agent_message=agent_message,
                customer_message=customer_message,
                feedback_score=action.feedback_score,
                mark_resolved=action.mark_resolved,
                feedback_source="customer",
                append_agent_history=True,
            )

        if agent_message:
            return self._finalize_simulated_turn(agent_message=agent_message)

        raise ValueError("Action did not contain a supported turn payload.")

    @property
    def state(self) -> MyState:
        """Get the current environment state."""
        return self._state

    def _select_scenario(
        self,
        complaint_id: Optional[str],
        complaint_text: Optional[str],
        complaint_category: Optional[str],
        customer_name: Optional[str],
    ) -> ComplaintScenario:
        if complaint_text:
            category = (complaint_category or "service").strip().lower()
            required_keywords = DEFAULT_REQUIRED_KEYWORDS.get(
                category, ("help", "support", "issue")
            )
            return ComplaintScenario(
                complaint_id=complaint_id or "custom-complaint",
                task_name="Custom Complaint Resolution",
                task_description=(
                    "Resolve a custom complaint with empathy, specificity, and a "
                    "clear next step."
                ),
                difficulty="medium",
                category=category,
                customer_name=customer_name or "Customer",
                complaint_text=complaint_text.strip(),
                required_keywords=required_keywords,
                resolution_keywords=DEFAULT_RESOLUTION_KEYWORDS,
                positive_feedback=(
                    "Thanks, that addresses my complaint.",
                    "That sounds like the right fix.",
                ),
                neutral_feedback=(
                    "I still need more detail before I am satisfied.",
                    "Please explain the next step more clearly.",
                ),
                negative_feedback=(
                    "That does not solve my complaint.",
                    "I still need proper support for this issue.",
                ),
                max_steps=6,
                success_threshold=0.72,
            )

        if complaint_id:
            task = TASK_INDEX.get(complaint_id)
            scenario = SCENARIO_INDEX.get(task.task_id if task is not None else "")
            if scenario is None:
                available = ", ".join(sorted(SCENARIO_INDEX))
                raise ValueError(
                    f"Unknown complaint_id '{complaint_id}'. Available ids: {available}"
                )
            return scenario

        return self._rng.choice(SCENARIOS)

    def _evaluate_agent_message(
        self, message: str
    ) -> tuple[float, list[str], str, bool]:
        stripped = message.strip()
        if not stripped:
            return -1.0, ["agent reply was empty"], "negative", False

        lowered = stripped.lower()
        reward = 0.0
        reasons: list[str] = []
        word_count = len(stripped.split())

        if word_count >= 14:
            reward += 0.2
            reasons.append("reply was substantive")
        elif word_count >= 7:
            reward += 0.1
            reasons.append("reply had enough detail to move the conversation forward")
        else:
            reward -= 0.2
            reasons.append("reply was too short")

        if any(term in lowered for term in EMPATHY_TERMS):
            reward += 0.25
            reasons.append("reply showed empathy")
        else:
            reward -= 0.1
            reasons.append("reply lacked empathy")

        keyword_hits = [
            keyword for keyword in self._scenario.required_keywords if keyword in lowered
        ]
        if keyword_hits:
            reward += min(0.45, 0.16 * len(keyword_hits))
            reasons.append(
                "reply addressed complaint details: " + ", ".join(sorted(keyword_hits))
            )
        else:
            reward -= 0.2
            reasons.append("reply did not address the complaint details directly")

        has_resolution = any(
            keyword in lowered for keyword in self._scenario.resolution_keywords
        )
        if has_resolution:
            reward += 0.25
            reasons.append("reply offered a concrete resolution path")
        elif "?" in stripped and any(term in lowered for term in CLARIFYING_TERMS):
            reward += 0.1
            reasons.append("reply asked a useful clarifying question")

        if any(term in lowered for term in DISMISSIVE_TERMS):
            reward -= 0.7
            reasons.append("reply used dismissive language")

        reward = self._clamp(reward)
        if reward >= 0.65:
            sentiment = "positive"
        elif reward <= 0.0:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return reward, reasons, sentiment, has_resolution

    def _score_client_feedback(
        self,
        feedback_text: Optional[str],
        feedback_score: Optional[float],
    ) -> tuple[float, str]:
        if feedback_score is not None:
            score = self._clamp(float(feedback_score))
        else:
            lowered = (feedback_text or "").strip().lower()
            if any(term in lowered for term in COMMON_POSITIVE_FEEDBACK):
                score = 1.0
            elif any(term in lowered for term in COMMON_NEGATIVE_FEEDBACK):
                score = -1.0
            elif any(term in lowered for term in COMMON_NEUTRAL_FEEDBACK):
                score = 0.0
            elif any(term in lowered for term in self._scenario.required_keywords):
                score = 0.25
            else:
                score = 0.0

        if score >= 0.5:
            sentiment = "positive"
        elif score <= -0.25:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        return score, sentiment

    def _extract_customer_message(self, action: MyAction) -> str:
        return (action.customer_message or action.client_feedback or "").strip()

    def _record_customer_context(
        self,
        customer_message: str,
        feedback_score: Optional[float],
        mark_resolved: Optional[bool],
    ) -> MyObservation:
        _, customer_sentiment = self._score_client_feedback(customer_message, feedback_score)
        self._chat_history.append(f"Customer: {customer_message}")
        self._state.last_customer_sentiment = customer_sentiment
        self._state.awaiting_customer_response = False
        if mark_resolved or self._looks_resolved(customer_message):
            self._state.resolution_status = "resolved"
            done = True
            suggested_next_action = (
                "Summarize the resolution and close the conversation politely."
            )
        else:
            self._state.resolution_status = "in_progress"
            done = False
            suggested_next_action = (
                "Address the customer's latest message directly and provide a concrete next step."
            )
        return self._build_observation(
            latest_customer_message=customer_message,
            latest_agent_message=self._latest_message_for_role("Agent"),
            customer_sentiment=customer_sentiment,
            reward=0.0,
            done=done,
            metadata={
                "customer_name": self._scenario.customer_name,
                "feedback_source": "customer_context",
                "reward_reason": (
                    "Customer message recorded. Reward will be assigned when the next agent "
                    "reply is evaluated."
                ),
                "step": self._state.step_count,
            },
            suggested_next_action=suggested_next_action,
        )

    def _finalize_customer_feedback(
        self,
        agent_message: str,
        customer_message: str,
        feedback_score: Optional[float],
        mark_resolved: Optional[bool],
        feedback_source: str,
        append_agent_history: bool,
    ) -> MyObservation:
        judge_reward, reasons, _, has_resolution = self._evaluate_agent_message(agent_message)
        feedback_reward, customer_sentiment = self._score_client_feedback(
            customer_message, feedback_score
        )
        reward = self._clamp((judge_reward * 0.35) + (feedback_reward * 0.65))
        reasons.append("reward blended with explicit customer message")
        return self._apply_feedback_result(
            agent_message=agent_message,
            customer_message=customer_message,
            customer_sentiment=customer_sentiment,
            reward=reward,
            has_resolution=has_resolution,
            reasons=reasons,
            feedback_source=feedback_source,
            mark_resolved=mark_resolved,
            append_agent_history=append_agent_history,
        )

    def _finalize_simulated_turn(self, agent_message: str) -> MyObservation:
        judge_reward, reasons, heuristic_sentiment, has_resolution = (
            self._evaluate_agent_message(agent_message)
        )
        reasons.append("environment simulated the customer feedback")
        customer_message = self._simulate_customer_reply(judge_reward, has_resolution)
        return self._apply_feedback_result(
            agent_message=agent_message,
            customer_message=customer_message,
            customer_sentiment=heuristic_sentiment,
            reward=judge_reward,
            has_resolution=has_resolution,
            reasons=reasons,
            feedback_source="environment",
            mark_resolved=False,
            append_agent_history=True,
        )

    def _apply_feedback_result(
        self,
        agent_message: str,
        customer_message: str,
        customer_sentiment: str,
        reward: float,
        has_resolution: bool,
        reasons: list[str],
        feedback_source: str,
        mark_resolved: Optional[bool],
        append_agent_history: bool,
    ) -> MyObservation:
        if append_agent_history:
            self._chat_history.append(f"Agent: {agent_message}")

        self._state.satisfaction_score = round(
            self._clamp(
                self._state.satisfaction_score + reward,
                low=-2.0,
                high=3.0,
            ),
            3,
        )

        resolved = bool(mark_resolved) or self._looks_resolved(customer_message) or (
            reward >= 0.7
            and (has_resolution or customer_sentiment == "positive")
            and self._state.satisfaction_score >= 0.6
        )
        escalated = (
            not resolved
            and (
                self._state.step_count >= self._max_turns
                or self._state.satisfaction_score <= -1.25
            )
        )

        if resolved:
            self._state.resolution_status = "resolved"
            done = True
            customer_message = self._positive_resolution_message(customer_message)
        elif escalated:
            self._state.resolution_status = "escalated"
            done = True
            customer_message = (
                "I still do not feel this is resolved. Please escalate this complaint."
            )
            customer_sentiment = "negative"
        else:
            self._state.resolution_status = "in_progress"
            done = False

        self._state.last_customer_sentiment = customer_sentiment
        self._state.awaiting_customer_response = False
        self._state.pending_agent_message = ""
        self._state.pending_judge_score = 0.0
        self._chat_history.append(f"Customer: {customer_message}")

        return self._build_observation(
            latest_customer_message=customer_message,
            latest_agent_message=agent_message,
            customer_sentiment=customer_sentiment,
            reward=reward,
            done=done,
            metadata={
                "customer_name": self._scenario.customer_name,
                "feedback_source": feedback_source,
                "reward_reason": "; ".join(reasons) if reasons else "Conversation continues.",
                "step": self._state.step_count,
            },
        )

    def _simulate_customer_reply(self, reward: float, has_resolution: bool) -> str:
        if reward >= 0.75 or (reward >= 0.45 and has_resolution):
            return self._rng.choice(self._scenario.positive_feedback)
        if reward >= 0.2:
            return self._rng.choice(self._scenario.neutral_feedback)
        return self._rng.choice(self._scenario.negative_feedback)

    def _positive_resolution_message(self, customer_message: str) -> str:
        if "resolve" in customer_message.lower() or "works" in customer_message.lower():
            return customer_message
        return "Thanks, that resolves my complaint."

    def _feedback_message_from_sentiment(self, sentiment: str) -> str:
        if sentiment == "positive":
            return self._rng.choice(self._scenario.positive_feedback)
        if sentiment == "negative":
            return self._rng.choice(self._scenario.negative_feedback)
        return self._rng.choice(self._scenario.neutral_feedback)

    def _build_observation(
        self,
        latest_customer_message: str,
        latest_agent_message: str,
        customer_sentiment: str,
        reward: float,
        done: bool,
        metadata: dict[str, object],
        suggested_next_action: Optional[str] = None,
    ) -> MyObservation:
        grader_score, score_breakdown = self._calculate_grader_score(latest_agent_message)
        full_metadata = {
            **metadata,
            "task_id": self._scenario.complaint_id,
            "task_name": self._scenario.task_name,
            "task_difficulty": self._scenario.difficulty,
            "success_threshold": self._scenario.success_threshold,
            "grader_score": grader_score,
            "score_breakdown": score_breakdown,
        }
        return MyObservation(
            task_id=self._scenario.complaint_id,
            task_name=self._scenario.task_name,
            task_difficulty=self._scenario.difficulty,
            complaint_id=self._scenario.complaint_id,
            complaint_category=self._scenario.category,
            complaint_text=self._scenario.complaint_text,
            latest_customer_message=latest_customer_message,
            latest_agent_message=latest_agent_message,
            customer_sentiment=customer_sentiment,
            satisfaction_score=self._state.satisfaction_score,
            resolution_status=self._state.resolution_status,
            suggested_next_action=(
                suggested_next_action
                or self._suggest_next_action(
                    resolution_status=self._state.resolution_status,
                    customer_sentiment=customer_sentiment,
                )
            ),
            chat_history=list(self._chat_history),
            awaiting_customer_response=self._state.awaiting_customer_response,
            done=done,
            reward=reward,
            metadata=full_metadata,
            grader_score=grader_score,
        )

    def _latest_message_for_role(self, role: str) -> str:
        prefix = f"{role}: "
        for line in reversed(self._chat_history):
            if line.startswith(prefix):
                return line[len(prefix) :]
        return ""

    @staticmethod
    def _looks_resolved(customer_message: str) -> bool:
        lowered = customer_message.lower()

        return any(
            phrase in lowered
            for phrase in (
                "resolved",
                "works for me",
                "thank you",
                "thanks, that resolves",
                "that resolves my complaint",
                "go ahead with that",
            )
        )

    def _suggest_next_action(self, resolution_status: str, customer_sentiment: str) -> str:
        if resolution_status == "resolved":
            return "Summarize the resolution and confirm any promised follow-up."
        if resolution_status == "escalated":
            return "Acknowledge the escalation and provide the next ownership handoff."
        if customer_sentiment == "negative":
            return (
                "Acknowledge the frustration, address the missing detail directly, "
                "and offer a concrete action such as refund, replacement, or escalation."
            )
        return "Clarify the next step and give a concrete timeline or resolution path."

    @staticmethod
    def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def _calculate_grader_score(
        self, latest_agent_message: str
    ) -> tuple[float, dict[str, float | str]]:
        """Compute a deterministic task score that always stays inside (0, 1)."""
        agent_messages = self._all_agent_messages()
        latest_message = latest_agent_message.strip() or (
            agent_messages[-1] if agent_messages else ""
        )

        quality_raw = 0.0
        if latest_message:
            quality_raw, _, _, _ = self._evaluate_agent_message(latest_message)

        satisfaction_score = self._normalize_to_unit_interval(
            self._state.satisfaction_score,
            low=-2.0,
            high=3.0,
        )
        quality_score = self._normalize_to_unit_interval(
            quality_raw,
            low=-1.0,
            high=1.0,
        )
        coverage_score = self._keyword_coverage_ratio(agent_messages)

        if self._state.resolution_status == "resolved":
            status_score = 0.92
        elif self._state.resolution_status == "escalated":
            status_score = 0.18
        elif self._state.resolution_status == "in_progress":
            status_score = 0.48
        else:
            status_score = 0.32

        if self._scenario.max_steps <= 1:
            efficiency_score = 1.0
        else:
            step_ratio = min(self._state.step_count, self._scenario.max_steps) / float(
                self._scenario.max_steps
            )
            efficiency_score = 1.0 - (0.35 * step_ratio)

        score = (
            (0.35 * status_score)
            + (0.25 * coverage_score)
            + (0.20 * quality_score)
            + (0.15 * satisfaction_score)
            + (0.05 * efficiency_score)
        )

        if self._state.resolution_status == "resolved" and coverage_score >= 0.75:
            score += 0.04
        elif self._state.resolution_status == "escalated":
            score -= 0.08

        score = self._clamp(
            score,
            low=TASK_SCORE_EPSILON,
            high=1.0 - TASK_SCORE_EPSILON,
        )
        score = round(float(score), 4)
        return score, {
            "status": self._state.resolution_status,
            "status_score": round(status_score, 4),
            "coverage_score": round(coverage_score, 4),
            "quality_score": round(quality_score, 4),
            "satisfaction_score": round(satisfaction_score, 4),
            "efficiency_score": round(efficiency_score, 4),
        }

    def _all_agent_messages(self) -> list[str]:
        prefix = "Agent: "
        return [line[len(prefix) :] for line in self._chat_history if line.startswith(prefix)]

    def _keyword_coverage_ratio(self, agent_messages: list[str]) -> float:
        if not self._scenario.required_keywords:
            return 0.5

        transcript = " ".join(agent_messages).lower()
        hits = sum(1 for keyword in self._scenario.required_keywords if keyword in transcript)
        return hits / float(len(self._scenario.required_keywords))

    @staticmethod
    def _normalize_to_unit_interval(value: float, low: float, high: float) -> float:
        if high <= low:
            return 0.5
        clipped = max(low, min(high, value))
        return (clipped - low) / (high - low)
