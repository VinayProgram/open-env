"""Task metadata for the complaint-resolution benchmark."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass

GRADER_MODULE = "graders.complaint_graders"
TASK_ID_ALIASES = {
    "late-delivery": "easy",
    "easy1": "easy",
    "wrong-item": "easy2",
    "damaged-item": "medium",
    "service-outage": "medium2",
    "billing-error": "hard",
}


@dataclass(frozen=True)
class TaskSpec:
    """Submission-facing task metadata."""

    task_id: str
    name: str
    difficulty: str
    description: str
    max_steps: int
    success_threshold: float
    grader: str
    grader_field: str = "grader_score"
    grader_type: str = "deterministic"


class TaskIndex(Mapping[str, TaskSpec]):
    """Mapping that resolves legacy task IDs to canonical benchmark IDs."""

    def __init__(self, tasks: Mapping[str, TaskSpec], aliases: Mapping[str, str]):
        self._tasks = dict(tasks)
        self._aliases = dict(aliases)

    def _canonical_id(self, task_id: str) -> str:
        return self._aliases.get(task_id, task_id)

    def __getitem__(self, task_id: str) -> TaskSpec:
        return self._tasks[self._canonical_id(task_id)]

    def __iter__(self) -> Iterator[str]:
        return iter(self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __contains__(self, task_id: object) -> bool:
        if not isinstance(task_id, str):
            return False
        return self._canonical_id(task_id) in self._tasks


def build_grader_ref(grader: str) -> dict[str, str]:
    """Return the structured grader reference expected by submission validators."""
    return {
        "module": GRADER_MODULE,
        "function": grader,
    }


TASKS: tuple[TaskSpec, ...] = (
    TaskSpec(
        task_id="easy",
        name="Late Delivery Recovery",
        difficulty="easy",
        description=(
            "Acknowledge an urgent shipment delay, reference tracking, and offer a "
            "concrete recovery path such as expedite, refund, or escalation."
        ),
        max_steps=5,
        success_threshold=0.72,
        grader="grade_late_delivery",
    ),
    TaskSpec(
        task_id="easy2",
        name="Wrong Item Exchange",
        difficulty="easy",
        description=(
            "Resolve a wrong-item shipment with a correct exchange and a prepaid "
            "return process."
        ),
        max_steps=5,
        success_threshold=0.71,
        grader="grade_wrong_item",
    ),
    TaskSpec(
        task_id="medium",
        name="Damaged Item Refund Or Replacement",
        difficulty="medium",
        description=(
            "Resolve a damaged-product complaint without charging return shipping, "
            "and propose a refund or replacement with clear logistics."
        ),
        max_steps=6,
        success_threshold=0.75,
        grader="grade_damaged_item",
    ),
    TaskSpec(
        task_id="medium2",
        name="Service Outage Escalation",
        difficulty="medium",
        description=(
            "Handle a service outage complaint by acknowledging the disruption, "
            "sharing a restoration path, and offering escalation or compensation."
        ),
        max_steps=6,
        success_threshold=0.74,
        grader="grade_service_outage",
    ),
    TaskSpec(
        task_id="hard",
        name="Duplicate Charge Resolution",
        difficulty="hard",
        description=(
            "Reverse a duplicate subscription charge, explain the billing follow-up, "
            "and reassure the customer that the issue will not recur."
        ),
        max_steps=7,
        success_threshold=0.73,
        grader="grade_billing_error",
    ),
)

TASK_INDEX: TaskIndex = TaskIndex(
    {task.task_id: task for task in TASKS},
    TASK_ID_ALIASES,
)


def resolve_task_id(task_id: str) -> str:
    """Map a legacy task ID to its canonical difficulty-based ID."""
    normalized = task_id.strip()
    return TASK_ID_ALIASES.get(normalized, normalized)


def get_task_spec(task_id: str) -> TaskSpec:
    """Return the canonical task spec for a task ID or legacy alias."""
    return TASK_INDEX[task_id]


def get_task_dicts() -> list[dict[str, object]]:
    """Return JSON-serializable task dictionaries."""
    task_dicts: list[dict[str, object]] = []
    for task in TASKS:
        task_dicts.append(
            {
                **asdict(task),
                "grader_id": task.grader,
                "grader": build_grader_ref(task.grader),
                "has_grader": True,
            }
        )
    return task_dicts
