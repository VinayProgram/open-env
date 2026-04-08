"""Deterministic grader helpers for the complaint-resolution tasks."""

from __future__ import annotations

from tasks import TASK_INDEX

TASK_SCORE_EPSILON = 0.05


def clamp_open_interval(score: float) -> float:
    """Clamp a score so it remains strictly inside the interval (0, 1)."""
    return round(
        max(TASK_SCORE_EPSILON, min(1.0 - TASK_SCORE_EPSILON, float(score))),
        4,
    )


def has_grader(task_id: str) -> bool:
    """Return whether the task has a registered grader."""
    return task_id in TASK_INDEX


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
