"""Submission-facing grader entrypoint."""

from __future__ import annotations

import json

from validate_submission import build_report


def grade() -> dict[str, object]:
    """Return the normalized task-grading report."""
    return build_report()


def main() -> int:
    """Print the grading report and exit successfully when valid."""
    report = grade()
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
