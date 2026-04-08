"""Task metadata for the complaint-resolution benchmark."""

from __future__ import annotations

from dataclasses import asdict, dataclass


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


TASKS: tuple[TaskSpec, ...] = (
    TaskSpec(
        task_id="late-delivery",
        name="Late Delivery Recovery",
        difficulty="easy",
        description=(
            "Acknowledge an urgent shipment delay, reference tracking details, and "
            "offer a concrete recovery path."
        ),
        max_steps=5,
        success_threshold=0.72,
        grader="grade_late_delivery",
    ),
    TaskSpec(
        task_id="damaged-item",
        name="Damaged Item Refund Or Replacement",
        difficulty="medium",
        description=(
            "Resolve a damaged-product complaint with a refund or replacement and "
            "make it clear the customer will not pay return shipping."
        ),
        max_steps=6,
        success_threshold=0.75,
        grader="grade_damaged_item",
    ),
    TaskSpec(
        task_id="billing-error",
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
    TaskSpec(
        task_id="service-outage",
        name="Service Outage Escalation",
        difficulty="medium",
        description=(
            "Acknowledge a service outage, provide a restoration path, and offer "
            "a callback, technician visit, or service credit."
        ),
        max_steps=6,
        success_threshold=0.74,
        grader="grade_service_outage",
    ),
    TaskSpec(
        task_id="wrong-item",
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
)

TASK_INDEX = {task.task_id: task for task in TASKS}


def get_task_dicts() -> list[dict[str, object]]:
    """Return JSON-serializable task dictionaries."""
    return [asdict(task) for task in TASKS]
