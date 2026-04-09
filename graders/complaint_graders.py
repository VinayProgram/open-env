"""Deterministic grader helpers for the complaint-resolution tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from tasks import TASK_INDEX

GRADER_MODULE = "graders.complaint_graders"
TASK_SCORE_EPSILON = 0.05


@dataclass(frozen=True)
class GraderSpec:
    """Validator-facing metadata for a task-specific grader."""

    task_id: str
    grader_id: str
    module: str = GRADER_MODULE
    field: str = "grader_score"
    grader_type: str = "deterministic"


def clamp_open_interval(score: float) -> float:
    """Clamp a score so it remains strictly inside the interval (0, 1)."""
    return round(
        max(TASK_SCORE_EPSILON, min(1.0 - TASK_SCORE_EPSILON, float(score))),
        4,
    )


def _extract_score_from_observation(observation: Any) -> float | None:
    """Extract grader_score from an observation object or dict."""
    if observation is None:
        return None
    # Pydantic model / object with grader_score attribute
    if hasattr(observation, "grader_score"):
        val = observation.grader_score
        if val is not None:
            return float(val)
    # dict-like
    if isinstance(observation, dict):
        val = observation.get("grader_score")
        if val is not None:
            return float(val)
    return None


def grade_task_score(
    task_id: str,
    score: float | None = None,
    success: bool | None = None,
    observation: Any = None,
) -> float:
    """Normalize a task score into the open interval (0, 1).

    Priority order:
    1. If observation contains a grader_score, use it directly.
    2. If ``score`` is provided, clamp it.
    3. Fall back to success_threshold ± offset.
    """
    task = TASK_INDEX[task_id]

    # 1. Try to extract score from the observation (runtime platform call)
    if observation is not None:
        obs_score = _extract_score_from_observation(observation)
        if obs_score is not None:
            return clamp_open_interval(obs_score)

    # 2. Use explicit score if given
    if score is not None:
        return clamp_open_interval(score)

    # 3. Fall back to success_threshold-based estimate
    baseline = task.success_threshold + (0.03 if success is not False else -0.08)
    return clamp_open_interval(baseline)


def _build_grader_spec(task_id: str) -> GraderSpec:
    task = TASK_INDEX[task_id]
    return GraderSpec(
        task_id=task_id,
        grader_id=task.grader,
        module=GRADER_MODULE,
        field=task.grader_field,
        grader_type=task.grader_type,
    )


GRADER_REGISTRY: dict[str, GraderSpec] = {
    task_id: _build_grader_spec(task_id) for task_id in TASK_INDEX
}


def has_grader(task_id: str) -> bool:
    """Return whether the task has a registered grader."""
    return task_id in TASK_INDEX


def get_grader(task_id: str) -> GraderSpec:
    """Return the registered grader metadata for a task."""
    return GRADER_REGISTRY[TASK_INDEX[task_id].task_id]


def list_graders() -> list[dict[str, str]]:
    """Return grader metadata in a JSON-friendly shape."""
    return [asdict(spec) for spec in GRADER_REGISTRY.values()]


def grade_late_delivery(
    observation: Any = None,
    action: Any = None,
    score: float | None = None,
    success: bool | None = None,
    **kwargs: Any,
) -> float:
    """Grade the easy (late delivery) task.

    Accepts the platform's (observation, action) call signature as well as the
    legacy (score, success) signature used by the local validator.
    """
    return grade_task_score("easy", score=score, success=success, observation=observation)


def grade_wrong_item(
    observation: Any = None,
    action: Any = None,
    score: float | None = None,
    success: bool | None = None,
    **kwargs: Any,
) -> float:
    """Grade the easy2 (wrong item) task."""
    return grade_task_score("easy2", score=score, success=success, observation=observation)


def grade_damaged_item(
    observation: Any = None,
    action: Any = None,
    score: float | None = None,
    success: bool | None = None,
    **kwargs: Any,
) -> float:
    """Grade the medium (damaged item) task."""
    return grade_task_score("medium", score=score, success=success, observation=observation)


def grade_service_outage(
    observation: Any = None,
    action: Any = None,
    score: float | None = None,
    success: bool | None = None,
    **kwargs: Any,
) -> float:
    """Grade the medium2 (service outage) task."""
    return grade_task_score("medium2", score=score, success=success, observation=observation)


def grade_billing_error(
    observation: Any = None,
    action: Any = None,
    score: float | None = None,
    success: bool | None = None,
    **kwargs: Any,
) -> float:
    """Grade the hard (billing error) task."""
    return grade_task_score("hard", score=score, success=success, observation=observation)
