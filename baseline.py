"""Submission-facing baseline entrypoint."""

from __future__ import annotations

import json
from pathlib import Path

from graders import grade_task_score, list_graders
from tasks import TASKS


def run_baseline() -> dict[str, object]:
    """Return per-task baseline scores in the checker-friendly shape."""
    baseline_path = Path("baseline_scores.json")
    payload: dict[str, object] = {}
    if baseline_path.exists():
        try:
            payload = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}

    raw_results = {
        str(entry.get("task_id", "")).strip(): entry
        for entry in payload.get("results", [])
        if str(entry.get("task_id", "")).strip()
    }

    tasks: list[dict[str, object]] = []
    for task in TASKS:
        entry = raw_results.get(task.task_id, {})
        score = grade_task_score(
            task.task_id,
            score=entry.get("score"),
            success=entry.get("success"),
        )
        result = 1 if bool(entry.get("success")) else 0
        tasks.append(
            {
                "task_id": task.task_id,
                "grader": task.grader,
                "grader_field": task.grader_field,
                "grader_type": task.grader_type,
                "result": result,
                "score": score,
            }
        )

    graders = list_graders()
    return {
        "task_count": len(tasks),
        "tasks_with_graders": sum(1 for task in tasks if task["grader"]),
        "grader_count": len(graders),
        "graded_task_ids": [task["task_id"] for task in tasks if task["grader"]],
        "graders": graders,
        "tasks": tasks,
    }


def main() -> int:
    """Print baseline results and exit successfully."""
    print(json.dumps(run_baseline(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
