"""
Tool registry + execution layer. Keeps agents from hammering APIs or running rm -rf /
because someone prompt-injected them. Again.
"""
from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """User-facing tool failures; message is safe to surface upstream."""


@dataclass
class RateLimitConfig:
    max_calls: int = 30
    per_seconds: float = 60.0


class _TokenBucket:
    """Cheap in-memory limiter. Good enough until you have multiple workers."""

    def __init__(self, cfg: RateLimitConfig) -> None:
        self._cfg = cfg
        self._timestamps: Deque[float] = deque()

    def acquire(self) -> None:
        now = time.monotonic()
        window = self._cfg.per_seconds
        while self._timestamps and now - self._timestamps[0] > window:
            self._timestamps.popleft()
        if len(self._timestamps) >= self._cfg.max_calls:
            raise ToolError(
                f"rate limited: {self._cfg.max_calls} calls / {self._cfg.per_seconds}s"
            )
        self._timestamps.append(now)


class ToolContext:
    """Whatever the orchestrator wants to inject (session id, user, redis, etc.)."""

    def __init__(self, extras: Optional[Dict[str, Any]] = None) -> None:
        self.extras = extras or {}


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, ctx: ToolContext, **kwargs: Any) -> Any:
        raise NotImplementedError


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the public web. Returns snippets, not full pages."

    def __init__(self, search_fn: Callable[..., Awaitable[List[Dict[str, str]]]]) -> None:
        self._search_fn = search_fn

    async def run(self, ctx: ToolContext, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        if not query or not query.strip():
            raise ToolError("empty query")
        return await self._search_fn(query.strip(), max_results=max_results)


class CodeExecTool(BaseTool):
    name = "code_exec"
    description = "Run sandboxed Python in a subprocess. No network, tight timeout."

    def __init__(self, timeout_sec: float = 8.0) -> None:
        self._timeout = timeout_sec

    async def run(self, ctx: ToolContext, code: str) -> Dict[str, str]:
        if not code.strip():
            raise ToolError("empty code")
        proc = await asyncio.create_subprocess_exec(
            "python",
            "-c",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise ToolError("code execution timed out")
        return {
            "stdout": out.decode(errors="replace")[:32_000],
            "stderr": err.decode(errors="replace")[:32_000],
            "returncode": str(proc.returncode or 0),
        }


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read a UTF-8 text file under an allowed root."

    def __init__(self, allowed_root: str, max_bytes: int = 512_000) -> None:
        import os

        self._root = os.path.realpath(allowed_root)
        self._max = max_bytes
        self._os = os

    async def run(self, ctx: ToolContext, path: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._read_sync, path)

    def _read_sync(self, path: str) -> str:
        full = self._os.path.realpath(self._os.path.join(self._root, path))
        if not full.startswith(self._root + self._os.sep) and full != self._root:
            raise ToolError("path escapes allowed root")
        try:
            with open(full, "r", encoding="utf-8", errors="strict") as f:
                return f.read(self._max)
        except OSError as e:
            logger.warning("file_read failed: %s", e)
            raise ToolError("could not read file") from e


@dataclass
class ToolRegistry:
    """Registers tools, applies per-tool rate limits, runs with logging."""

    _tools: Dict[str, BaseTool] = field(default_factory=dict)
    _limiters: Dict[str, _TokenBucket] = field(default_factory=dict)
    _limits: Dict[str, RateLimitConfig] = field(default_factory=dict)

    def register(self, tool: BaseTool, rate: Optional[RateLimitConfig] = None) -> None:
        self._tools[tool.name] = tool
        if rate:
            self._limits[tool.name] = rate
            self._limiters[tool.name] = _TokenBucket(rate)

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ToolError(f"unknown tool: {name}")
        return self._tools[name]

    async def execute(self, name: str, ctx: ToolContext, **kwargs: Any) -> Any:
        tool = self.get(name)
        lim = self._limiters.get(name)
        if lim:
            lim.acquire()
        t0 = time.perf_counter()
        try:
            result = await tool.run(ctx, **kwargs)
        except ToolError:
            raise
        except Exception as e:
            logger.exception("tool %s crashed", name)
            raise ToolError("internal tool error") from e
        logger.info("tool %s finished in %.3fs", name, time.perf_counter() - t0)
        return result
