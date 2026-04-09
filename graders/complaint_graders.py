"""Deterministic grader helpers for the complaint-resolution tasks."""

from __future__ import annotations

from dataclasses import asdict, dataclass

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


def grade_task_score(
    task_id: str,
    score: float | None = None,
    success: bool | None = None,
) -> float:
    """Normalize a task score into the open interval (0, 1)."""
    task = TASK_INDEX[task_id]
    if score is None:
        baseline = task.success_threshold + (0.03 if success is not False else -0.08)
        score = baseline
    return clamp_open_interval(score)


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


def grade_late_delivery(score: float | None = None, success: bool | None = None) -> float:
    """Normalize the easy task score."""
    return grade_task_score("easy", score=score, success=success)


def grade_damaged_item(score: float | None = None, success: bool | None = None) -> float:
    """Normalize the medium task score."""
    return grade_task_score("medium", score=score, success=success)


def grade_billing_error(score: float | None = None, success: bool | None = None) -> float:
    """Normalize the hard task score."""
    return grade_task_score("hard", score=score, success=success)


def grade_service_outage(score: float | None = None, success: bool | None = None) -> float:
    """Normalize the medium2 task score."""
    return grade_task_score("medium2", score=score, success=success)


def grade_wrong_item(score: float | None = None, success: bool | None = None) -> float:
    """Normalize the easy2 task score."""
    return grade_task_score("easy2", score=score, success=success)
