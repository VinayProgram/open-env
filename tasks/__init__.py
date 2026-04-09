"""Public benchmark task catalog for submission validators."""

from .catalog import (
    GRADER_MODULE,
    TASKS,
    TASK_INDEX,
    TASK_ID_ALIASES,
    TaskSpec,
    build_grader_ref,
    get_task_dicts,
    get_task_spec,
    resolve_task_id,
)

__all__ = [
    "GRADER_MODULE",
    "TASKS",
    "TASK_INDEX",
    "TASK_ID_ALIASES",
    "TaskSpec",
    "build_grader_ref",
    "get_task_dicts",
    "get_task_spec",
    "resolve_task_id",
]
