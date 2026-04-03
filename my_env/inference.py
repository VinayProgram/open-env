"""Inference runner for the complaint-resolution environment."""

from __future__ import annotations

import asyncio
import os
import sys
import textwrap
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
if __package__:
    from . import MyAction, MyEnv
else:
    package_root = Path(__file__).resolve().parent.parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    from my_env import MyAction, MyEnv

IMAGE_NAME = os.getenv("IMAGE_NAME")
ENV_BASE_URL = os.getenv("ENV_BASE_URL")
API_KEY = (
    os.getenv("HF_TOKEN")
    or os.getenv("API_KEY")
    or os.getenv("OPENAI_API_KEY")
)
API_BASE_URL = "https://router.huggingface.co/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
TASK_NAME = os.getenv("MY_ENV_TASK", "complaint-resolution")
BENCHMARK = os.getenv("MY_ENV_BENCHMARK", "my_env")
DEFAULT_COMPLAINT_ID = os.getenv("MY_ENV_COMPLAINT_ID", "late-delivery")
MAX_STEPS = int(os.getenv("MAX_STEPS", "6"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
SUCCESS_SCORE_THRESHOLD = float(os.getenv("SUCCESS_SCORE_THRESHOLD", "0.6"))

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


def log_end(success: bool, steps: int, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True,
    )


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


def get_model_message(
    client: OpenAI,
    last_reward: float,
    observation_text: dict[str, object],
) -> str:
    user_prompt = build_user_prompt(last_reward, observation_text)
    fallback = (
        "I am sorry for the inconvenience. I will review your complaint and offer a concrete next step right away."
    )
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
        print(f"Raw model response: {completion}", flush=True)
        text = (completion.choices[0].message.content or "").strip()
        return text if text else fallback
    except Exception as exc:
        print(f"Model request failed: {type(exc).__name__}: {exc}", flush=True)
        return fallback


async def _connect_env() -> MyEnv:
    if ENV_BASE_URL:
        env = MyEnv(base_url=ENV_BASE_URL)
        await env.connect()
        return env
    if IMAGE_NAME:
        return await MyEnv.from_docker_image(IMAGE_NAME)
    raise RuntimeError("Set either ENV_BASE_URL or IMAGE_NAME before running inference.")


async def main() -> None:
    if not API_KEY:
        raise RuntimeError(
            "Missing API key. Set HF_TOKEN, API_KEY, or OPENAI_API_KEY before running inference."
        )

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = await _connect_env()

    rewards: list[float] = []
    steps_taken = 0
    success = False
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(complaint_id=DEFAULT_COMPLAINT_ID)
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if result.done:
                break

            observation_text = result.observation.model_dump()
            message = get_model_message(client, last_reward, observation_text)
            print(f"Model message:\n{message}\n", flush=True)
            result = await env.step(MyAction(agent_message=message))
            reward = float(result.reward or 0.0)
            rewards.append(reward)
            steps_taken = step
            last_reward = reward

            log_step(
                step=step,
                action=message,
                reward=reward,
                done=result.done,
                error=None,
            )

            if result.done:
                break

        average_reward = sum(rewards) / len(rewards) if rewards else 0.0
        resolution_status = result.observation.resolution_status
        success = resolution_status == "resolved" or average_reward >= SUCCESS_SCORE_THRESHOLD
    finally:
        try:
            await env.close()
        finally:
            log_end(success=success, steps=steps_taken, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
