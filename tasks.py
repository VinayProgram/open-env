from dataclasses import dataclass, asdict

@dataclass
class Task:
    task_id: str
    name: str
    difficulty: str
    description: str
    max_steps: int = 6
    success_threshold: float = 0.70
    grader_type: str = "deterministic"
    grader_field: str = "grader_score"

TASKS = [
    Task("easy", "Late Delivery Recovery", "easy", "Acknowledge an urgent shipment delay, reference tracking, and offer a concrete recovery path such as expedite, refund, or escalation.", max_steps=5, success_threshold=0.72),
    Task("easy2", "Wrong Item Exchange", "easy", "Resolve a wrong-item shipment with a correct exchange and a prepaid return process.", max_steps=5, success_threshold=0.71),
    Task("medium", "Damaged Item Refund Or Replacement", "medium", "Resolve a damaged-product complaint without charging return shipping, and propose a refund or replacement with clear logistics.", max_steps=6, success_threshold=0.75),
    Task("medium2", "Service Outage Escalation", "medium", "Handle a service outage complaint by acknowledging the disruption, sharing a restoration path, and offering escalation or compensation.", max_steps=6, success_threshold=0.74),
    Task("hard", "Duplicate Charge Resolution", "hard", "Reverse a duplicate subscription charge, explain the billing follow-up, and reassure the customer that the issue will not recur.", max_steps=7, success_threshold=0.73),
]

TASK_INDEX = {t.task_id: t for t in TASKS}

def get_task_dicts() -> list[dict]:
    # This matches the shape expected by server/app.py and my_env_environment.py
    return [
        {
            **asdict(task),
            "grader": {
                "module": "grader",
                "function": "grade"
            },
            "grader_id": "grade",
            "has_grader": True
        }
        for task in TASKS
    ]
