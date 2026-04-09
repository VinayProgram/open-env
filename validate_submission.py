"""Local submission-shape validator for the complaint benchmark."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from graders import GRADER_MODULE, grade_task_score, has_grader, list_graders
from tasks import TASKS, build_grader_ref


def build_report() -> dict[str, object]:
    """Build a machine-readable summary of task/grader coverage."""
    baseline_path = Path("baseline_scores.json")
    baseline_results: dict[str, dict[str, object]] = {}
    if baseline_path.exists():
        try:
            payload = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        for entry in payload.get("results", []):
            task_id = str(entry.get("task_id", "")).strip()
            if task_id:
                baseline_results[task_id] = entry

    task_reports: list[dict[str, object]] = []
    for task in TASKS:
        baseline_entry = baseline_results.get(task.task_id, {})
        raw_score = baseline_entry.get("score")
        success = baseline_entry.get("success")
        normalized_score = grade_task_score(
            task.task_id,
            score=float(raw_score) if raw_score is not None else None,
            success=bool(success) if success is not None else None,
        )
        result_int = 1 if bool(success) else 0
        task_reports.append(
            {
                "task_id": task.task_id,
                "name": task.name,
                "difficulty": task.difficulty,
                "grader_id": task.grader,
                "grader": build_grader_ref(task.grader),
                "grader_field": task.grader_field,
                "grader_type": task.grader_type,
                "grader_module": GRADER_MODULE,
                "has_grader": has_grader(task.task_id),
                "result": result_int,
                "score": normalized_score,
                "score_in_open_interval": 0.0 < normalized_score < 1.0,
            }
        )

    tasks_with_graders = sum(1 for task in task_reports if task["has_grader"])
    graded_task_ids = [str(task["task_id"]) for task in task_reports if task["has_grader"]]
    graders = list_graders()
    out_of_range = [task["task_id"] for task in task_reports if not task["score_in_open_interval"]]
    return {
        "valid": tasks_with_graders >= 3 and not out_of_range,
        "tasks_with_graders": tasks_with_graders,
        "task_count": len(task_reports),
        "grader_count": len(graders),
        "graded_task_ids": graded_task_ids,
        "graders": graders,
        "out_of_range_scores": out_of_range,
        "tasks": task_reports,
    }


def main() -> int:
    """Print the validation report and return an appropriate exit code."""
    report = build_report()
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
