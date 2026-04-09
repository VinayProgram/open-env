"""Public benchmark task catalog for submission validators."""

from .catalog import GRADER_MODULE, TASKS, TASK_INDEX, TaskSpec, build_grader_ref, get_task_dicts

__all__ = [
    "GRADER_MODULE",
    "TASKS",
    "TASK_INDEX",
    "TaskSpec",
    "build_grader_ref",
    "get_task_dicts",
]
