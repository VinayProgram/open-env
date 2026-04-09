"""
Inference Script Example (validation-critical stdout format)
===========================================================
MANDATORY
- Define these env vars in your environment config:
    API_BASE_URL        The API endpoint for the LLM.
    MODEL_NAME          The model identifier to use for inference.
    HF_TOKEN            Your Hugging Face / API key.
    LOCAL_IMAGE_NAME    Local Docker image name for MyEnv.from_docker_image(), if used.

- Defaults are set only for API_BASE_URL and MODEL_NAME.
- Participants must use the OpenAI client for all LLM calls.

STDOUT FORMAT
- Emit exactly three line types to stdout, in this order, per task episode:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

Rules:
    - One [START] line at episode begin.
    - One [STEP] line per step, immediately after env.step() returns.
    - One [END] line per episode, always emitted (even on exception).
    - reward and rewards are formatted to 2 decimal places.
    - done and success are lowercase booleans: true or false.
    - error is the raw last_action_error string, or null if none (must be single-token).
    - All fields on a single line with no newlines within a line.
    - Each task must return score in [0, 1].
"""

import asyncio
import os
import textwrap
from typing import List, Optional
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from openai import OpenAI

from client import MyEnv
from models import MyAction
from tasks import TASKS

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

ENV_BASE_URL = os.getenv("ENV_BASE_URL") or os.getenv("MY_ENV_BASE_URL")
BENCHMARK = os.getenv("MY_ENV_BENCHMARK", "openenv-my-env")
MAX_STEPS = int(os.getenv("MAX_STEPS", "6"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a customer support agent working a complaint-resolution chat.
    Respond with one helpful support message that is empathetic, specific, and actionable.
    """
).strip()


def _normalize_env_base_url(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "http://localhost:8000"
    if not (value.startswith("http://") or value.startswith("https://")):
        value = f"http://{value}"
    parsed = urlparse(value)
    if not parsed.netloc:
        return "http://localhost:8000"
    if parsed.port is None:
        host = parsed.hostname or "localhost"
        netloc = f"{host}:8000"
        if parsed.username or parsed.password:
            auth = parsed.username or ""
            if parsed.password:
                auth = f"{auth}:{parsed.password}"
            netloc = f"{auth}@{netloc}"
        parsed = parsed._replace(netloc=netloc)
    return urlunparse(parsed._replace(path="", params="", query="", fragment="")).rstrip("/")


def _env_spec_mode(value: Optional[str]) -> str:
    value = (value or "").strip()
    if value.startswith("http://") or value.startswith("https://"):
        return "url"
    if value:
        return "image"
    return "default"


async def _resolve_env() -> MyEnv:
    mode = _env_spec_mode(ENV_BASE_URL)
    if mode == "url":
        return MyEnv(base_url=_normalize_env_base_url(ENV_BASE_URL or ""))
    if mode == "image":
        # Requested behavior: if mode == "image": return await MyEnv.from_docker_image(value)
        return await asyncio.to_thread(MyEnv.from_docker_image, (ENV_BASE_URL or "").strip())
    if LOCAL_IMAGE_NAME:
        return await asyncio.to_thread(MyEnv.from_docker_image, LOCAL_IMAGE_NAME.strip())
    return MyEnv(base_url=_normalize_env_base_url("http://localhost:8000"))


def _bool_str(value: bool) -> str:
    return str(bool(value)).lower()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    # Keep values parseable as key=value tokens (no spaces/newlines).
    action_val = (action or "").replace("\n", " ").strip() or "agent_message"
    action_val = action_val.replace(" ", "_")
    error_val = (error or "").replace("\n", " ").strip()
    error_val = error_val.replace(" ", "_") if error_val else "null"
    print(
        f"[STEP] step={step} action={action_val} reward={reward:.2f} done={_bool_str(done)} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    score = float(min(max(score, 0.0), 1.0))
    print(
        f"[END] success={_bool_str(success)} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def _score_from_observation(observation) -> Optional[float]:
    try:
        value = getattr(observation, "grader_score", None)
    except Exception:
        value = None
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _user_prompt_from_observation(observation) -> str:
    try:
        obs = observation.model_dump()
    except Exception:
        obs = {}
    return (
        f"Complaint: {obs.get('complaint_text')}\n"
        f"Customer: {obs.get('latest_customer_message')}\n"
        "Reply:"
    )


def _get_model_message(client: OpenAI, user_prompt: str) -> str:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=TEMPERATURE,
        stream=False,
    )
    text = (completion.choices[0].message.content or "").strip()
    return text if text else "I’m sorry about that — I’ll help fix this right away."


async def run_task(task_id: str, client: OpenAI) -> None:
    rewards: List[float] = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    env: MyEnv | None = None
    try:
        env = await _resolve_env()
        await env.connect()
        result = await env.reset(task_id=task_id)
        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            user_prompt = _user_prompt_from_observation(result.observation)
            reply = _get_model_message(client, user_prompt)

            result = await env.step(MyAction(agent_message=reply))
            reward = float(result.reward or 0.0)
            done = bool(result.done)
            error = getattr(result.observation, "last_action_error", None)

            rewards.append(reward)
            steps_taken = step

            log_step(step=step, action="agent_message", reward=reward, done=done, error=error)

            if done:
                break

        observed_score = _score_from_observation(result.observation)
        score = observed_score if observed_score is not None else (sum(rewards) / len(rewards) if rewards else 0.0)
        score = float(min(max(score, 0.0), 1.0))
        success = bool(result.done) and score > 0.0

    except Exception as exc:
        # Must still emit END line even on exception. Emit a final STEP as terminal.
        log_step(step=max(1, steps_taken + 1), action="agent_message", reward=0.0, done=True, error=str(exc))
        success = False
        score = 0.0
    finally:
        try:
            if env is not None:
                await env.close()
        except Exception:
            pass
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    for task in TASKS:
        await run_task(task.task_id, client)


if __name__ == "__main__":
    asyncio.run(main())
