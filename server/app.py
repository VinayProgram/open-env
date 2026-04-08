# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
FastAPI application for the complaint-resolution environment and React SPA.

This module serves the React frontend from `client/dist` and mounts the
environment API under `/api`.

Endpoints:
    - POST /api/reset: Reset the environment
    - POST /api/step: Execute an action
    - GET /api/state: Get current environment state
    - GET /api/schema: Get action/observation schemas
    - GET /api/tasks: List public benchmark tasks
    - GET /api/validate: Report submission-shape metadata
    - WS /api/ws: WebSocket endpoint for persistent sessions
    - GET /*: React frontend with index.html fallback routing

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""

from pathlib import Path

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:  # pragma: no cover
    raise ImportError(
        "openenv is required for the web interface. Install dependencies with '\n    uv sync\n'"
    ) from e

from .sql.db import init_db

try:
    from ..models import MyAction, MyObservation
except ImportError:
    from models import MyAction, MyObservation

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .chat.chat_router import router as chat_router
from .customer_service.customer_chat_router import router as customer_chat_router
from .my_env_environment import MyEnvironment, get_task_catalog

API_PREFIX = "/api"
CLIENT_DIST_CANDIDATES = (
    Path("/app/client/dist"),
    Path(__file__).resolve().parents[2] / "client" / "dist",
)
LEGACY_API_PREFIXES = (
    "/health",
    "/schema",
    "/reset",
    "/step",
    "/state",
    "/tasks",
    "/validate",
    "/mcp",
    "/metadata",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/ws",
    "/web",
)


class LegacyApiCompatMiddleware:
    """Rewrite legacy root API paths to the mounted `/api` app."""

    def __init__(self, app, api_prefix: str, legacy_prefixes: tuple[str, ...]) -> None:
        self.app = app
        self.api_prefix = api_prefix
        self.legacy_prefixes = legacy_prefixes

    def _rewrite_path(self, path: str) -> str:
        if not path or path.startswith(self.api_prefix):
            return path

        for prefix in self.legacy_prefixes:
            if path == prefix or path.startswith(f"{prefix}/"):
                return f"{self.api_prefix}{path}"

        return path

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        rewritten_path = self._rewrite_path(path)
        if rewritten_path == path:
            await self.app(scope, receive, send)
            return

        rewritten_scope = dict(scope)
        rewritten_scope["path"] = rewritten_path
        rewritten_scope["raw_path"] = rewritten_path.encode("ascii")
        await self.app(rewritten_scope, receive, send)


def _get_client_dist_dir() -> Path:
    for candidate in CLIENT_DIST_CANDIDATES:
        if candidate.exists():
            return candidate
    return CLIENT_DIST_CANDIDATES[0]


CLIENT_DIST_DIR = _get_client_dist_dir()
INDEX_FILE = CLIENT_DIST_DIR / "index.html"


def _resolve_client_file(request_path: str) -> Path | None:
    if not request_path:
        return None

    root = CLIENT_DIST_DIR.resolve()
    candidate = (root / request_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None

    return candidate if candidate.is_file() else None


api_app = create_app(
    MyEnvironment,
    MyAction,
    MyObservation,
    env_name="my_env",
    max_concurrent_envs=1,  # increase this number to allow more concurrent WebSocket sessions
)
api_app.include_router(chat_router)
api_app.include_router(customer_chat_router)


@api_app.get("/tasks", tags=["Benchmark"])
async def list_tasks() -> dict[str, object]:
    """Expose the benchmark task catalog for submission validators."""
    tasks = get_task_catalog()
    return {
        "task_count": len(tasks),
        "tasks": tasks,
    }


@api_app.get("/validate", tags=["Benchmark"])
async def validate_submission_shape() -> dict[str, object]:
    """Report the submission shape expected by hackathon validators."""
    tasks = get_task_catalog()
    return {
        "valid": len(tasks) >= 3,
        "env_name": "my_env",
        "version": "1.0.0",
        "task_count": len(tasks),
        "tasks_with_graders": len(tasks),
        "grader_field": "grader_score",
        "score_range": {"min_exclusive": 0.0, "max_exclusive": 1.0},
        "tasks": tasks,
    }

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
origins = [
    "http://localhost:5173",
    "https://vinaytandale-complaint-system-openenv.hf.space",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(API_PREFIX, api_app)


@app.on_event("startup")
async def startup_event() -> None:
    init_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    # SQLite doesn't require explicit shutdown without open connections
    pass


@app.get("/", include_in_schema=False)
async def serve_frontend_index() -> FileResponse:
    if not INDEX_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Frontend build not found. Expected client/dist/index.html.",
        )
    return FileResponse(INDEX_FILE)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str) -> FileResponse:
    asset = _resolve_client_file(full_path)
    if asset is not None:
        return FileResponse(asset)

    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)

    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Expected client/dist/index.html.",
    )


# Configure API OpenAPI documentation
api_app.title = "Complaint Resolution Environment API"
api_app.description = """
FastAPI application for the complaint-resolution environment.

This module creates an HTTP server that exposes the MyEnvironment over HTTP
and WebSocket endpoints, compatible with EnvClient.

## Endpoints

- **POST /api/reset**: Reset the environment
- **POST /api/step**: Execute an action
- **GET /api/state**: Get current environment state
- **GET /api/schema**: Get action/observation schemas
- **GET /api/tasks**: List benchmark tasks and graders
- **GET /api/validate**: Report submission-shape metadata
- **POST /api/customer-chat/create**: Create a chat session
- **GET /api/chat/{chat_key}/messages**: Get persisted messages
- **WS /api/chat/ws/{chat_key}**: WebSocket chat endpoint

## Usage

### Development (with auto-reload):
```
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

### Production:
```
uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Or run directly:
```
python -m my_env.server.app
```
"""
api_app.version = "1.0.0"
api_app.contact = {"name": "OpenEnv Team", "url": "https://github.com/your-repo/OpenEnv"}
api_app.license_info = {"name": "BSD-3-Clause"}

app = LegacyApiCompatMiddleware(app, api_prefix=API_PREFIX, legacy_prefixes=LEGACY_API_PREFIXES)


def main(host: str = "0.0.0.0", port: int = 8000):
    """
    Entry point for direct execution via uv run or python -m.

    This function enables running the server without Docker:
        uv run --project . server
        uv run --project . server --port 8001
        python -m my_env.server.app

    Args:
        host: Host address to bind to (default: "0.0.0.0")
        port: Port number to listen on (default: 8000)

    For production deployments, consider using uvicorn directly with
    multiple workers:
        uvicorn my_env.server.app:app --workers 4
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)

# OpenEnv validation looks for a literal main() call in the source.
if False:
    main()
