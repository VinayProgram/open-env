"""Inference runner for the complaint-resolution environment."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI
from tasks import TASKS, TASK_INDEX, build_grader_ref

load_dotenv()

if __package__:
    from . import MyAction, MyEnv
else:
    source_root = Path(__file__).resolve().parent
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    from client import MyEnv
    from models import MyAction

IMAGE_NAME = os.getenv("IMAGE_NAME")
ENV_BASE_URL = os.getenv("ENV_BASE_URL")
DEFAULT_ENV_BASE_URL = os.getenv("DEFAULT_ENV_BASE_URL", "http://127.0.0.1:8000")
API_KEY = (
    os.getenv("HF_TOKEN")
    or os.getenv("API_KEY")
    or os.getenv("OPENAI_API_KEY")
)
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = os.getenv("MY_ENV_TASK", "complaint-resolution")
BENCHMARK = os.getenv("MY_ENV_BENCHMARK", "my_env")
MAX_STEPS = int(os.getenv("MAX_STEPS", "6"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.6"))
STOP_ON_DONE = os.getenv("STOP_ON_DONE", "").strip().lower() in {"1", "true", "yes", "on"}
EXACT_TASK_SET = os.getenv("MY_ENV_EXACT_TASK_SET", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
DEFAULT_TASK_IDS = tuple(task.task_id for task in TASKS)
SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a customer support agent working a complaint-resolution chat.
    Read the complaint, latest customer feedback, and conversation history.
    Respond with one helpful support message that is empathetic, specific, and actionable.
    Prefer clear next steps, timelines, refunds, replacements, or escalation when appropriate.
    Reply with exactly one agent message string and no extra commentary.
    """
).strip()


def _one_line(value: str) -> str:
    return " ".join(value.split())


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={_one_line(action)} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def log_task_result(
    task_id: str,
    grader: str,
    score: float,
    result: int,
    success: bool,
    steps: int,
    resolution_status: str,
) -> None:
    print(
        (
            f"[TASK] task_id={task_id} grader={grader} result={result} score={score:.4f} "
            f"success={str(success).lower()} steps={steps} "
            f"resolution_status={resolution_status}"
        ),
        flush=True,
    )


def parse_task_ids() -> list[str]:
    requested: list[str]
    raw_multi = (
        os.getenv("MY_ENV_TASK_IDS")
        or os.getenv("MY_ENV_COMPLAINT_IDS")
        or ""
    ).strip()
    if raw_multi:
        requested = [part.strip() for part in raw_multi.split(",") if part.strip()]
    else:
        single_task = (
            os.getenv("MY_ENV_TASK_ID")
            or os.getenv("MY_ENV_COMPLAINT_ID")
            or ""
        ).strip()
        if single_task:
            requested = [single_task]
        else:
            requested = list(DEFAULT_TASK_IDS)

    if EXACT_TASK_SET:
        return list(dict.fromkeys(requested))

    expanded = [*requested, *DEFAULT_TASK_IDS]
    return list(dict.fromkeys(expanded))


def build_user_prompt(last_reward: float, observation_text: dict[str, object]) -> str:
    history = observation_text.get("chat_history", [])
    if isinstance(history, list):
        history_block = "\n".join(str(item) for item in history[-6:]) if history else "None"
    else:
        history_block = "None"

    return textwrap.dedent(
        f"""
        Complaint category: {observation_text.get("complaint_category", "")}
        Original complaint: {observation_text.get("complaint_text", "")}
        Latest customer message: {observation_text.get("latest_customer_message", "")}
        Customer sentiment: {observation_text.get("customer_sentiment", "neutral")}
        Satisfaction score: {observation_text.get("satisfaction_score", 0.0)}
        Resolution status: {observation_text.get("resolution_status", "open")}
        Last reward: {last_reward:.2f}
        Suggested next action: {observation_text.get("suggested_next_action", "")}
        Recent transcript:
        {history_block}
        Write the next support reply.
        """
    ).strip()


def build_heuristic_reply(observation_text: dict[str, object]) -> str:
    category = str(observation_text.get("complaint_category", "")).strip().lower()
    latest_customer_message = str(observation_text.get("latest_customer_message", "")).lower()
    resolution_status = str(observation_text.get("resolution_status", "open")).lower()

    if resolution_status == "resolved":
        return (
            "I am glad we could resolve this. I have documented the resolution, "
            "confirmed the promised follow-up, and you will receive a final confirmation shortly."
        )

    if category == "delivery":
        return (
            "I am sorry for the delivery delay and I understand this is urgent. "
            "I am checking the tracking now, escalating the shipment with our delivery team, "
            "and if the package does not move today I can arrange an expedited replacement or refund."
        )
    if category == "product":
        return (
            "I am sorry the item arrived damaged. I will process either a replacement or a refund "
            "right away, and I will send a prepaid return label so you do not pay any return shipping."
        )
    if category == "billing":
        return (
            "I am sorry about the duplicate charge. I am escalating this to our billing team, "
            "reversing the extra subscription charge, and I will confirm the refund timeframe "
            "and follow-up so this does not happen again."
        )
    if category == "service":
        return (
            "I am sorry for the service outage and I understand how disruptive this is. "
            "I am escalating the issue now, arranging a technician callback with a restoration "
            "timeframe, and I will also review an appropriate service credit."
        )

    if "refund" in latest_customer_message or "replacement" in latest_customer_message:
        return (
            "I am sorry for the inconvenience. I will review the complaint, confirm the next step, "
            "and provide a concrete refund or replacement path with a clear timeline."
        )
    return (
        "I am sorry for the inconvenience. I understand the frustration, and I will review the issue "
        "now, explain the next step clearly, and provide a concrete resolution path."
    )


def get_model_message(
    client: OpenAI | None,
    last_reward: float,
    observation_text: dict[str, object],
) -> str:
    user_prompt = build_user_prompt(last_reward, observation_text)
    fallback = build_heuristic_reply(observation_text)
    if client is None:
        return fallback

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else fallback
    except Exception as exc:
        print(f"Model request failed: {type(exc).__name__}: {exc}", flush=True)
        return fallback


def _normalize_base_url(base_url: str) -> str:
    base_url = base_url.strip()
    if not base_url:
        return "http://127.0.0.1:8000"
    if "://" not in base_url:
        return f"http://{base_url}"
    return base_url


def _looks_like_base_url(value: str) -> bool:
    candidate = value.strip().lower()
    if not candidate:
        return False
    if candidate.startswith(("http://", "https://", "ws://", "wss://")):
        return True
    if candidate.startswith(("localhost", "127.0.0.1", "0.0.0.0")):
        return True
    return "." in candidate and "/" not in candidate


async def _connect_env() -> MyEnv:
    attempts: list[tuple[str, str]] = []

    if ENV_BASE_URL:
        if _looks_like_base_url(ENV_BASE_URL):
            attempts.append(("base_url", ENV_BASE_URL))
        else:
            attempts.append(("image", ENV_BASE_URL))
    if IMAGE_NAME and IMAGE_NAME != ENV_BASE_URL:
        attempts.append(("image", IMAGE_NAME))
    attempts.append(("base_url", DEFAULT_ENV_BASE_URL))

    errors: list[str] = []
    for mode, value in attempts:
        try:
            if mode == "image":
                return await MyEnv.from_docker_image(value)
            env = MyEnv(base_url=_normalize_base_url(value))
            await env.connect()
            return env
        except Exception as exc:
            errors.append(f"{mode}={value}: {type(exc).__name__}: {exc}")
            print(
                f"[WARN] Failed to connect using {mode}={value}: {type(exc).__name__}: {exc}",
                flush=True,
            )

    raise RuntimeError(
        "Unable to connect to the complaint environment. Tried:\n- "
        + "\n- ".join(errors)
        + "\nSet ENV_BASE_URL to a real http(s) URL, or set IMAGE_NAME to a valid Docker image, "
        "or start the local server with `uvicorn server.app:app --host 0.0.0.0 --port 8000`."
    )


async def run_task(
    env: MyEnv,
    client: OpenAI | None,
    task_id: str,
) -> dict[str, Any]:
    rewards: list[float] = []
    steps_taken = 0
    reached_resolved_state = False
    result = await env.reset(task_id=task_id)
    last_reward = 0.0

    for step in range(1, MAX_STEPS + 1):
        if STOP_ON_DONE and result.done:
            break

        observation_text = result.observation.model_dump()
        message = get_model_message(client, last_reward, observation_text)
        print(f"Model message:\n{message}\n", flush=True)
        result = await env.step(MyAction(agent_message=message))
        reward = float(result.reward or 0.0)
        rewards.append(reward)
        steps_taken = step
        last_reward = reward
        reached_resolved_state = (
            reached_resolved_state
            or result.observation.resolution_status == "resolved"
        )
        log_step(
            step=step,
            action=message,
            reward=reward,
            done=result.done,
            error=None,
        )

        if STOP_ON_DONE and result.done:
            break

    average_reward = sum(rewards) / len(rewards) if rewards else 0.0
    resolution_status = result.observation.resolution_status
    grader_score = float(
        result.observation.grader_score
        if result.observation.grader_score is not None
        else result.observation.metadata.get("grader_score", average_reward)
    )
    if grader_score <= 0.0:
        grader_score = 0.01
    elif grader_score >= 1.0:
        grader_score = 0.99

    success_threshold = float(
        result.observation.metadata.get("success_threshold", SUCCESS_SCORE_THRESHOLD)
    )
    success = (
        reached_resolved_state
        or resolution_status == "resolved"
        or grader_score >= success_threshold
    )
    result_int = 1 if success else 0
    log_end(success=success, steps=steps_taken, score=grader_score, rewards=rewards)
    log_task_result(
        task_id=task_id,
        grader=TASK_INDEX[task_id].grader,
        score=grader_score,
        result=result_int,
        success=success,
        steps=steps_taken,
        resolution_status=resolution_status,
    )
    return {
        "task_id": task_id,
        "grader_id": TASK_INDEX[task_id].grader,
        "grader": build_grader_ref(TASK_INDEX[task_id].grader),
        "grader_field": TASK_INDEX[task_id].grader_field,
        "grader_type": TASK_INDEX[task_id].grader_type,
        "result": result_int,
        "score": grader_score,
        "success": success,
        "steps": steps_taken,
        "resolution_status": resolution_status,
        "average_reward": round(average_reward, 4),
        "rewards": rewards,
    }


async def main() -> None:
    client: OpenAI | None = None
    if API_KEY:
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    else:
        print(
            "API key not found. Falling back to the built-in heuristic baseline.",
            flush=True,
        )

    env: MyEnv | None = None
    results: list[dict[str, Any]] = []
    try:
        env = await _connect_env()
        task_ids = parse_task_ids()
        log_start(
            task=TASK_NAME,
            env=BENCHMARK,
            model=MODEL_NAME if client else "heuristic-baseline",
        )
        print(f"[CONFIG] task_ids={','.join(task_ids)} max_steps={MAX_STEPS}", flush=True)

        for task_id in task_ids:
            print(f"\n=== Running task: {task_id} ===", flush=True)
            results.append(await run_task(env=env, client=client, task_id=task_id))
    finally:
        if env is not None:
            await env.close()

    average_score = (
        sum(float(result["score"]) for result in results) / len(results)
        if results
        else 0.0
    )
    grader_ids = {
        str(result["grader_id"])
        for result in results
        if result.get("grader_id")
    }
    summary = {
        "valid": all(0.0 < float(result["score"]) < 1.0 for result in results),
        "tasks_with_graders": sum(1 for result in results if result.get("grader")),
        "grader_count": len(grader_ids),
        "graded_task_ids": [
            str(result["task_id"]) for result in results if result.get("grader")
        ],
        "graders": [
            {
                "task_id": task.task_id,
                "grader_id": task.grader,
                "grader": build_grader_ref(task.grader),
                "field": task.grader_field,
                "grader_type": task.grader_type,
            }
            for task in TASKS
        ],
        "results_binary": [int(result["result"]) for result in results],
        "results": results,
        "average_score": round(average_score, 4),
        "task_count": len(results),
    }
    Path("baseline_scores.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(
        f"[SUMMARY] average_score={average_score:.4f} task_count={len(results)}",
        flush=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
