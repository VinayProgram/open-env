# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Complaint-resolution environment client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult

try:
    from .models import MyAction, MyObservation, MyState
except ImportError:
    from models import MyAction, MyObservation, MyState


class MyEnv(
    EnvClient[MyAction, MyObservation, MyState]
):
    """
    Client for the My Env Environment.

    This client maintains a persistent WebSocket connection to the environment server,
    enabling efficient multi-step interactions with lower latency.
    Each client instance has its own dedicated environment session on the server.

    Example:
        >>> # Connect to a running server
        >>> with MyEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset(complaint_id="easy")
        ...     print(result.observation.complaint_text)
        ...
        ...     result = client.step(
        ...         MyAction(
        ...             agent_message="I am sorry for the delay. I can check tracking and escalate this order."
        ...         )
        ...     )
        ...     print(result.observation.latest_customer_message)

    Example with Docker:
        >>> # Automatically start container and connect
        >>> client = MyEnv.from_docker_image("my_env-env:latest")
        >>> try:
        ...     result = client.reset(complaint_id="hard")
        ...     result = client.step(MyAction(agent_message="I am sorry about the duplicate charge."))
        ... finally:
        ...     client.close()
    """

    def _step_payload(self, action: MyAction) -> Dict:
        """
        Convert MyAction to JSON payload for step message.

        Args:
            action: MyAction instance

        Returns:
            Dictionary representation suitable for JSON encoding
        """
        payload: Dict[str, object] = {
            "metadata": action.metadata,
            "await_customer_response": action.await_customer_response,
        }
        if action.agent_message is not None:
            payload["agent_message"] = action.agent_message
        if action.customer_message is not None:
            payload["customer_message"] = action.customer_message
        if action.client_feedback is not None:
            payload["client_feedback"] = action.client_feedback
        if action.feedback_score is not None:
            payload["feedback_score"] = action.feedback_score
        if action.mark_resolved is not None:
            payload["mark_resolved"] = action.mark_resolved
        return payload

    def _parse_result(self, payload: Dict) -> StepResult[MyObservation]:
        """
        Parse server response into StepResult[MyObservation].

        Args:
            payload: JSON response data from server

        Returns:
            StepResult with MyObservation
        """
        obs_data = payload.get("observation", {})
        observation = MyObservation(
            task_id=obs_data.get("task_id", obs_data.get("complaint_id", "")),
            task_name=obs_data.get("task_name", ""),
            task_difficulty=obs_data.get("task_difficulty", "medium"),
            complaint_id=obs_data.get("complaint_id", ""),
            complaint_category=obs_data.get("complaint_category", ""),
            complaint_text=obs_data.get("complaint_text", ""),
            latest_customer_message=obs_data.get("latest_customer_message", ""),
            latest_agent_message=obs_data.get("latest_agent_message", ""),
            customer_sentiment=obs_data.get("customer_sentiment", "neutral"),
            satisfaction_score=obs_data.get("satisfaction_score", 0.0),
            resolution_status=obs_data.get("resolution_status", "open"),
            suggested_next_action=obs_data.get("suggested_next_action", ""),
            chat_history=obs_data.get("chat_history", []),
            awaiting_customer_response=obs_data.get("awaiting_customer_response", False),
            grader_score=obs_data.get("grader_score"),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> MyState:
        """
        Parse server response into State object.

        Args:
            payload: JSON response from state request

        Returns:
            State object with episode_id and step_count
        """
        return MyState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            complaint_id=payload.get("complaint_id", ""),
            complaint_category=payload.get("complaint_category", ""),
            satisfaction_score=payload.get("satisfaction_score", 0.0),
            resolution_status=payload.get("resolution_status", "open"),
            last_customer_sentiment=payload.get("last_customer_sentiment", "neutral"),
            awaiting_customer_response=payload.get("awaiting_customer_response", False),
            pending_agent_message=payload.get("pending_agent_message", ""),
            pending_judge_score=payload.get("pending_judge_score", 0.0),
        )
