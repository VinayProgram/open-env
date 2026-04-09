"""Inference runner for the complaint-resolution environment."""

import asyncio
import os
import textwrap
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv
from openai import OpenAI
from client import MyEnv
from models import MyAction
from tasks import TASKS

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME") or "Qwen/Qwen2.5-72B-Instruct"
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")
ENV_BASE_URL = os.getenv("ENV_BASE_URL") or os.getenv("MY_ENV_BASE_URL") or "http://localhost:8000"
MAX_STEPS = 6

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


def _env_spec_mode(value: str) -> str:
    """
    Infer how to interpret ENV_BASE_URL.

    - "url": value looks like an http(s) URL (including localhost)
    - "image": value is treated as a Docker image name
    """
    value = (value or "").strip()
    if value.startswith("http://") or value.startswith("https://"):
        return "url"
    return "image"


async def _resolve_env(env_spec: str) -> MyEnv:
    mode = _env_spec_mode(env_spec)
    value = (env_spec or "").strip()
    print(f"Resolved ENV_BASE_URL='{env_spec}' to mode='{mode}' with value='{value}'")
    if mode == "image":
        return await MyEnv.from_docker_image(value)
    return MyEnv(base_url=_normalize_env_base_url(value))

async def run_task(env: MyEnv, client: OpenAI | None, task_id: str) -> dict:
    result = await env.reset(task_id=task_id)
    steps = 0
    rewards = []
    for step in range(MAX_STEPS):
        if result.done:
            break
            
        obs = result.observation.model_dump()
        user_prompt = f"Complaint: {obs.get('complaint_text')}\nCustomer: {obs.get('latest_customer_message')}\nReply:"
        
        reply = "I apologize for the issue. I will look into this immediately."
        if client:
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1
                )
                reply = response.choices[0].message.content or reply
            except Exception as e:
                print(f"Model failed: {e}")
                
        print(f"Step {step+1}: Agent: {reply}")
        result = await env.step(MyAction(agent_message=reply))
        rewards.append(float(result.reward or 0.0))
        steps += 1
        
    score = getattr(result.observation, 'grader_score', None)
    if score is None:
        score = sum(rewards)/len(rewards) if rewards else 0.5
        
    return {
        "task_id": task_id,
        "score": max(0.01, min(0.99, float(score))),
        "steps": steps,
        "grader": {"module": "grader", "function": "grade"}
    }

async def main():
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL) if API_KEY else None
    
    results = []
    env = await _resolve_env(ENV_BASE_URL)
    
    try:
        await env.connect()
    except Exception as e:
        mode = _env_spec_mode(ENV_BASE_URL)
        normalized_url = _normalize_env_base_url(ENV_BASE_URL) if mode == "url" else ""
        print(
            "Failed to connect to env.\n"
            f"- ENV_BASE_URL: {ENV_BASE_URL}\n"
            f"- mode: {mode}\n"
            + (f"- base_url: {normalized_url}\n" if mode == "url" else "")
            + (
                "- If mode=url: ensure the FastAPI server is running (e.g. `uvicorn server.app:app --host 0.0.0.0 --port 8000`).\n"
                "- If mode=image: ensure Docker is running and the image exists (e.g. set ENV_BASE_URL=my_env_v4).\n"
            )
            + f"Error: {e}"
        )
        return
    
    for task in TASKS:
        print(f"\n--- Running Task: {task.task_id} ---")
        res = await run_task(env, client, task.task_id)
        results.append(res)
        print(f"Finished {task.task_id} with score {res['score']}")
        
    await env.close()
    
    avg_score = sum(r['score'] for r in results) / len(results) if results else 0.0
    print(f"\nBaseline Average Score: {avg_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
