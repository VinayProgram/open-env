#!/usr/bin/env python3
# /// script
# dependencies = [
#   "datasets",
#   "peft",
#   "pydantic",
#   "trackio",
#   "transformers",
#   "trl",
# ]
# ///
"""Ready-to-run GRPO training script for the complaint-resolution benchmark.

Usage:
    uv run train_grpo.py
    uv run train_grpo.py --task-ids easy,hard
    uv run train_grpo.py --hub-model-id your-username/complaint-grpo

This script trains directly against the local complaint environment via TRL's
environment_factory interface. It does not require a separate environment
server.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import types
import textwrap
from datetime import datetime
from pathlib import Path
from abc import ABC
from typing import Any, Generic, TypeVar

from datasets import Dataset
from peft import LoraConfig
from pydantic import BaseModel, ConfigDict, Field
from transformers import AutoTokenizer
from trl import GRPOConfig, GRPOTrainer

def _install_openenv_compat_shim() -> None:
    """Provide the minimal OpenEnv base types used by local modules.

    The repo ships environment/model code that expects the OpenEnv package
    layout, but the full upstream package pulls in optional dependencies that
    are not required for this training script. A small shim keeps those local
    modules importable without the heavyweight runtime.
    """

    if "openenv.core.env_server.types" in sys.modules:
        return

    class Action(BaseModel):
        model_config = ConfigDict(
            extra="forbid",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        metadata: dict[str, Any] = Field(default_factory=dict)

    class Observation(BaseModel):
        model_config = ConfigDict(
            extra="forbid",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        done: bool = Field(default=False)
        reward: bool | int | float | None = Field(default=None)
        metadata: dict[str, Any] = Field(default_factory=dict)

    class State(BaseModel):
        model_config = ConfigDict(
            extra="allow",
            validate_assignment=True,
            arbitrary_types_allowed=True,
        )

        episode_id: str | None = Field(default=None)
        step_count: int = Field(default=0, ge=0)

    class EnvironmentMetadata(BaseModel):
        model_config = ConfigDict(extra="forbid", validate_assignment=True)

        name: str
        description: str
        readme_content: str | None = None
        version: str | None = None
        author: str | None = None
        documentation_url: str | None = None

    ActT = TypeVar("ActT", bound=Action)
    ObsT = TypeVar("ObsT", bound=Observation)
    StateT = TypeVar("StateT", bound=State)

    class Environment(ABC, Generic[ActT, ObsT, StateT]):
        SUPPORTS_CONCURRENT_SESSIONS: bool = False

        def __init__(self, transform=None, rubric=None):
            self.transform = transform
            self.rubric = rubric

        def reset(self, seed=None, episode_id=None, **kwargs):
            raise NotImplementedError

        async def reset_async(self, seed=None, episode_id=None, **kwargs):
            return self.reset(seed=seed, episode_id=episode_id, **kwargs)

        def step(self, action, timeout_s=None, **kwargs):
            raise NotImplementedError

        async def step_async(self, action, timeout_s=None, **kwargs):
            return self.step(action, timeout_s=timeout_s, **kwargs)

        @property
        def state(self):
            raise NotImplementedError

        def get_metadata(self):
            return EnvironmentMetadata(
                name=self.__class__.__name__,
                description=f"{self.__class__.__name__} environment",
                version="1.0.0",
            )

    openenv_mod = types.ModuleType("openenv")
    openenv_mod.__path__ = []
    core_mod = types.ModuleType("openenv.core")
    core_mod.__path__ = []
    env_server_mod = types.ModuleType("openenv.core.env_server")
    env_server_mod.__path__ = []
    types_mod = types.ModuleType("openenv.core.env_server.types")
    interfaces_mod = types.ModuleType("openenv.core.env_server.interfaces")

    types_mod.Action = Action
    types_mod.Observation = Observation
    types_mod.State = State
    types_mod.EnvironmentMetadata = EnvironmentMetadata
    interfaces_mod.Action = Action
    interfaces_mod.Observation = Observation
    interfaces_mod.State = State
    interfaces_mod.Environment = Environment
    interfaces_mod.EnvironmentMetadata = EnvironmentMetadata

    sys.modules["openenv"] = openenv_mod
    sys.modules["openenv.core"] = core_mod
    sys.modules["openenv.core.env_server"] = env_server_mod
    sys.modules["openenv.core.env_server.types"] = types_mod
    sys.modules["openenv.core.env_server.interfaces"] = interfaces_mod
    openenv_mod.core = core_mod
    core_mod.env_server = env_server_mod
    env_server_mod.types = types_mod
    env_server_mod.interfaces = interfaces_mod


_install_openenv_compat_shim()

from models import MyAction
from server.my_env_environment import MyEnvironment
from tasks import TASKS, TASK_INDEX

DEFAULT_MODEL_ID = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")
DEFAULT_PROJECT = "complaint-resolution-grpo"
DEFAULT_TRACKIO_SPACE_ID = "complaint-resolution-grpo"
DEFAULT_OUTPUT_ROOT = Path("outputs")
DEFAULT_USER_PROMPT = textwrap.dedent(
    """
    You are a customer support agent.
    Resolve the complaint with empathy, specificity, and one concrete next step.
    Use the `reply` tool to send your support response.
    Keep the answer concise, natural, and helpful.
    """
).strip()


def sanitize_name(name: str) -> str:
    """Convert a model or project name into a filesystem-friendly slug."""
    cleaned = [
        char if char.isalnum() or char in {"-", "_"} else "-"
        for char in name.strip()
    ]
    slug = "".join(cleaned).strip("-")
    return slug or "run"


def parse_task_ids(raw: str | None) -> list[str]:
    """Resolve the selected task IDs from CLI args or benchmark-style env vars."""
    candidate = (raw or "").strip()
    if not candidate:
        candidate = (
            os.getenv("MY_ENV_TASK_IDS")
            or os.getenv("MY_ENV_COMPLAINT_IDS")
            or os.getenv("MY_ENV_TASK_ID")
            or os.getenv("MY_ENV_COMPLAINT_ID")
            or ""
        ).strip()

    if candidate:
        task_ids: list[str] = []
        for part in candidate.split(","):
            raw_task_id = part.strip()
            if not raw_task_id:
                continue
            if raw_task_id in TASK_INDEX:
                resolved = TASK_INDEX[raw_task_id].task_id
            else:
                resolved = raw_task_id
            if resolved not in task_ids:
                task_ids.append(resolved)
    else:
        task_ids = [task.task_id for task in TASKS]

    unknown = [task_id for task_id in task_ids if task_id not in TASK_INDEX]
    if unknown:
        valid = ", ".join(sorted(TASK_INDEX))
        raise ValueError(f"Unknown task_id(s): {', '.join(unknown)}. Valid ids: {valid}")
    return task_ids


def build_dataset(task_ids: list[str], examples_per_task: int, seed: int) -> Dataset:
    """Create a prompt-only GRPO dataset with one row per task episode."""
    rows: list[dict[str, object]] = []
    for task_id in task_ids:
        for _ in range(examples_per_task):
            rows.append(
                {
                    "prompt": [{"role": "user", "content": DEFAULT_USER_PROMPT}],
                    "task_id": task_id,
                }
            )

    random.Random(seed).shuffle(rows)
    return Dataset.from_list(rows)


def format_reset_message(observation) -> str:
    """Turn the initial observation into the prompt the model sees."""
    customer_name = str(observation.metadata.get("customer_name", "Customer"))
    return textwrap.dedent(
        f"""
        Task: {observation.task_name} ({observation.task_id})
        Difficulty: {observation.task_difficulty}
        Customer: {customer_name}
        Complaint: {observation.complaint_text}
        Latest customer message: {observation.latest_customer_message}
        Resolution status: {observation.resolution_status}
        Suggested next action: {observation.suggested_next_action}
        """
    ).strip()


def format_step_message(observation) -> str:
    """Summarize the next environment state for the model after a reply."""
    return textwrap.dedent(
        f"""
        Customer reply: {observation.latest_customer_message}
        Customer sentiment: {observation.customer_sentiment}
        Resolution status: {observation.resolution_status}
        Suggested next action: {observation.suggested_next_action}
        """
    ).strip()


class ComplaintToolEnv:
    """Small GRPO wrapper that exposes the complaint environment as a tool."""

    def __init__(self) -> None:
        self.env = MyEnvironment()
        self.reward = 0.0
        self.grader_score = 0.0
        self.done = False
        self.task_id = ""

    def reset(
        self,
        task_id: str | None = None,
        complaint_id: str | None = None,
        **kwargs,
    ) -> str | None:
        """Reset the underlying environment.

        Args:
            task_id: Benchmark task identifier.
            complaint_id: Alias for task_id, kept for compatibility.
            **kwargs: Any additional dataset columns forwarded by TRL.

        Returns:
            A compact complaint summary appended to the user's prompt.
        """
        selected_task_id = (task_id or complaint_id or "").strip()
        if not selected_task_id:
            raise ValueError("reset requires a task_id or complaint_id")

        observation = self.env.reset(
            task_id=selected_task_id,
            complaint_id=selected_task_id,
            **kwargs,
        )
        self.task_id = selected_task_id
        self.reward = 0.0
        self.grader_score = 0.0
        self.done = False
        return format_reset_message(observation)

    def reply(self, message: str) -> str:
        """Send one support reply to the complaint environment.

        Args:
            message: The next customer-support response to evaluate.

        Returns:
            A concise description of the updated customer state.
        """
        if self.done:
            raise ValueError("Episode already finished.")

        observation = self.env.step(MyAction(agent_message=message))
        self.reward = float(observation.reward or 0.0)
        self.grader_score = float(
            observation.grader_score
            if observation.grader_score is not None
            else observation.metadata.get("grader_score", 0.0)
        )
        self.done = bool(observation.done)
        return format_step_message(observation)


def reward_func(environments, **kwargs) -> list[float]:
    """Reward each rollout using the benchmark's normalized task score."""
    return [float(getattr(env, "grader_score", 0.0)) for env in environments]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run GRPO training on the complaint-resolution benchmark."
    )
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Base model to fine-tune.",
    )
    parser.add_argument(
        "--task-ids",
        default=None,
        help="Comma-separated task IDs. Defaults to all benchmark tasks.",
    )
    parser.add_argument(
        "--examples-per-task",
        type=int,
        default=32,
        help="How many synthetic prompt rows to create for each task.",
    )
    parser.add_argument(
        "--num-train-epochs",
        type=float,
        default=1.0,
        help="Training epochs.",
    )
    parser.add_argument(
        "--per-device-train-batch-size",
        type=int,
        default=1,
        help="Per-device batch size.",
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=8,
        help="Gradient accumulation steps.",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=5e-6,
        help="Optimizer learning rate.",
    )
    parser.add_argument(
        "--num-generations",
        type=int,
        default=4,
        help="Number of rollouts generated per prompt.",
    )
    parser.add_argument(
        "--max-completion-length",
        type=int,
        default=256,
        help="Maximum tokens across the full multi-turn episode.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Nucleus sampling probability.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=50,
        help="Top-k sampling cutoff.",
    )
    parser.add_argument(
        "--save-steps",
        type=int,
        default=50,
        help="Checkpoint save interval.",
    )
    parser.add_argument(
        "--save-total-limit",
        type=int,
        default=2,
        help="Maximum number of checkpoints to keep.",
    )
    parser.add_argument(
        "--logging-steps",
        type=int,
        default=1,
        help="Logging interval.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for checkpoints and logs.",
    )
    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT,
        help="Trackio project name.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help="Optional run name.",
    )
    parser.add_argument(
        "--trackio-space-id",
        default=DEFAULT_TRACKIO_SPACE_ID,
        help="Trackio space ID.",
    )
    parser.add_argument(
        "--hub-model-id",
        default=None,
        help="Optional Hub repo to push the final model to.",
    )
    parser.add_argument(
        "--use-vllm",
        action="store_true",
        help="Enable vLLM-backed generation if you have it installed.",
    )
    parser.add_argument(
        "--vllm-mode",
        choices=("colocate", "server"),
        default="colocate",
        help="vLLM mode when --use-vllm is set.",
    )
    parser.add_argument(
        "--vllm-server-base-url",
        default="http://localhost:8000",
        help="vLLM server URL when --vllm-mode=server.",
    )
    return parser.parse_args()


def detect_precision_settings() -> tuple[bool, bool, bool]:
    """Pick a CPU- or GPU-safe precision setup for TRL/Transformers."""
    try:
        import torch
    except ModuleNotFoundError:
        return True, False, False

    if not torch.cuda.is_available():
        return True, False, False

    return False, bool(torch.cuda.is_bf16_supported()), not bool(torch.cuda.is_bf16_supported())


def main() -> int:
    args = parse_args()
    task_ids = parse_task_ids(args.task_ids)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    model_slug = sanitize_name(args.model_id)
    output_dir = Path(args.output_dir or DEFAULT_OUTPUT_ROOT / f"complaint-grpo-{model_slug}-{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = build_dataset(task_ids=task_ids, examples_per_task=args.examples_per_task, seed=args.seed)

    tokenizer = AutoTokenizer.from_pretrained(args.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token
    tokenizer.padding_side = "left"

    use_cpu, bf16, fp16 = detect_precision_settings()
    if use_cpu:
        print("[WARN] CUDA is not available; training will run on CPU.", flush=True)
    elif bf16:
        print("[INFO] Using bf16 precision on GPU.", flush=True)
    else:
        print("[INFO] Using fp16 precision on GPU.", flush=True)

    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        target_modules="all-linear",
        task_type="CAUSAL_LM",
    )

    grpo_kwargs: dict[str, object] = {
        "output_dir": str(output_dir),
        "num_train_epochs": args.num_train_epochs,
        "learning_rate": args.learning_rate,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "num_generations": args.num_generations,
        "max_completion_length": args.max_completion_length,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "top_k": args.top_k,
        "logging_steps": args.logging_steps,
        "save_strategy": "steps",
        "save_steps": args.save_steps,
        "save_total_limit": args.save_total_limit,
        "remove_unused_columns": False,
        "report_to": ["trackio"],
        "seed": args.seed,
        "gradient_checkpointing": True,
        "log_completions": True,
        "use_cpu": use_cpu,
        "bf16": bf16,
        "fp16": fp16,
    }

    effective_use_vllm = args.use_vllm and not use_cpu
    if args.use_vllm and use_cpu:
        print("[WARN] --use-vllm ignored because CUDA is not available.", flush=True)

    if effective_use_vllm:
        grpo_kwargs["use_vllm"] = True
        grpo_kwargs["vllm_mode"] = args.vllm_mode
        if args.vllm_mode == "server":
            grpo_kwargs["vllm_server_base_url"] = args.vllm_server_base_url

    if args.hub_model_id:
        grpo_kwargs["push_to_hub"] = True
        grpo_kwargs["hub_model_id"] = args.hub_model_id
        grpo_kwargs["hub_strategy"] = "every_save"

    training_args = GRPOConfig(**grpo_kwargs)
    training_args.project = args.project
    training_args.run_name = args.run_name or f"complaint-grpo-{timestamp}"
    training_args.trackio_space_id = args.trackio_space_id

    if args.hub_model_id and not (
        os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    ):
        print(
            "[WARN] hub_model_id was provided but no HF_TOKEN/HUGGINGFACE_HUB_TOKEN is set.",
            flush=True,
        )

    print("[CONFIG] training complaint-resolution GRPO", flush=True)
    print(f"[CONFIG] model={args.model_id}", flush=True)
    print(f"[CONFIG] tasks={','.join(task_ids)}", flush=True)
    print(f"[CONFIG] examples_per_task={args.examples_per_task}", flush=True)
    print(f"[CONFIG] output_dir={output_dir}", flush=True)
    print(f"[CONFIG] use_vllm={args.use_vllm} mode={args.vllm_mode}", flush=True)

    trainer = GRPOTrainer(
        model=args.model_id,
        processing_class=tokenizer,
        reward_funcs=reward_func,
        train_dataset=dataset,
        peft_config=peft_config,
        args=training_args,
        environment_factory=ComplaintToolEnv,
    )

    trainer.train()
    trainer.save_model()

    if args.hub_model_id:
        trainer.push_to_hub()

    print(f"[DONE] model saved to {output_dir}", flush=True)
    if args.hub_model_id:
        print(f"[DONE] pushed to {args.hub_model_id}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
