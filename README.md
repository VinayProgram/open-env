---
title: Complaint Resolution Benchmark
emoji: "🎧"
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - benchmark
  - customer-support
---

# Complaint Resolution Benchmark

This environment is a small customer-support benchmark with three explicit tasks
and a deterministic `grader_score` for submission validation.

The agent receives a complaint, sends support replies, and the environment
tracks:

- shaped step rewards in `[-1, 1]`
- a running customer satisfaction score
- a task-level `grader_score` strictly inside `(0, 1)`

## Tasks

| Task ID | Name | Difficulty | Max Steps | Grader |
|---|---|---|---:|---|
| `late-delivery` | Late Delivery Recovery | easy | 5 | `grader_score` |
| `damaged-item` | Damaged Item Refund Or Replacement | medium | 6 | `grader_score` |
| `billing-error` | Duplicate Charge Resolution | hard | 7 | `grader_score` |

Every task uses the same output contract: when the episode advances, the
observation includes `grader_score`, and terminal scores are clamped to remain
strictly greater than `0.0` and strictly less than `1.0`.

## API Notes

- `POST /reset` accepts either `task_id` or `complaint_id`
- `POST /step` submits `agent_message` and returns the next observation
- `GET /tasks` returns the benchmark task catalog
- `GET /validate` returns submission-shape metadata for validators
- `GET /metadata` returns the environment description

## Submission Files

The repo now also includes explicit submission-facing metadata:

- `tasks/` contains the three benchmark task definitions
- `graders/` contains deterministic score normalization helpers
- `validate_submission.py` prints a machine-readable report with task/grader coverage
- `baseline_scores.json` stores the latest multi-task baseline scores

## Baseline Runner

`inference.py` now runs all three tasks by default and writes per-task scores to
`baseline_scores.json`.

Environment variables:

- `MY_ENV_TASK_IDS` or `MY_ENV_COMPLAINT_IDS`: comma-separated task list
- `MY_ENV_TASK_ID` or `MY_ENV_COMPLAINT_ID`: run a single task
- `STOP_ON_DONE=true`: stop early when the environment signals `done`

If no API key is available, the runner falls back to a built-in heuristic
baseline so the benchmark can still emit non-edge task scores.

## Local Run

```bash
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

```bash
python inference.py
```
