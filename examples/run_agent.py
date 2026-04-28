"""
Minimal wiring: registry + memory + fake search. Swap fake_search for your provider.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time
from typing import Any, Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# package root: examples/ -> repo root
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.memory import ConversationMemory, MemoryConfig
from src.tools import (
    CodeExecTool,
    FileReadTool,
    RateLimitConfig,
    ToolContext,
    ToolError,
    ToolRegistry,
    WebSearchTool,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("run_agent")


async def fake_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    await asyncio.sleep(0.05)
    return [
        {"title": f"result-{i}", "snippet": f"{query} … synthetic hit {i}"}
        for i in range(min(max_results, 3))
    ]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo multi-step agent with tools + sliding memory.")
    p.add_argument("--model", default="gpt-4o-mini", help="Chat model name")
    p.add_argument(
        "--allow-code-exec",
        action="store_true",
        help="Register code_exec (subprocess). Off by default because nobody trusts demos.",
    )
    return p.parse_args()


async def main() -> None:
    args = parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        log.error("Set OPENAI_API_KEY")
        raise SystemExit(2)

    registry = ToolRegistry()
    registry.register(WebSearchTool(fake_search), rate=RateLimitConfig(max_calls=20, per_seconds=60))
    registry.register(
        FileReadTool(allowed_root=os.getcwd()),
        rate=RateLimitConfig(max_calls=100, per_seconds=60),
    )
    if args.allow_code_exec:
        registry.register(CodeExecTool(timeout_sec=6.0), rate=RateLimitConfig(max_calls=5, per_seconds=300))

    mem = ConversationMemory(MemoryConfig(model=args.model))
    llm = ChatOpenAI(model=args.model, temperature=0.3)
    ctx = ToolContext(extras={"run_id": "demo-1"})

    user_msg = "Search for python asyncio best practices and mention one file in this repo."
    mem.add_user(user_msg)

    tools_desc = (
        "Tools: web_search(query), file_read(path relative to cwd)."
        + (" code_exec(code) runs local python -c in a subprocess." if args.allow_code_exec else "")
    )
    messages = [
        SystemMessage(
            content=(
                "You are a careful assistant. Use tools when needed. "
                + tools_desc
            )
        ),
        *mem.build_context(user_msg),
    ]

    t0 = time.perf_counter()
    first = await llm.ainvoke(messages)
    log.info("assistant (plan): %s", first.content[:200])

    try:
        hits = await registry.execute("web_search", ctx, query="asyncio gather vs create_task")
    except ToolError as e:
        log.warning("web_search tool failed: %s", e)
        hits = []
    mem.add_ai(f"Search results: {hits}")

    messages = [
        SystemMessage(content="Answer succinctly using the search results."),
        *mem.build_context("summarize"),
    ]
    final = await llm.ainvoke(messages + [HumanMessage(content="Give 3 bullet takeaways.")])
    log.info("final: %s", final.content)
    mem.add_ai(str(final.content))

    if args.allow_code_exec:
        try:
            snippet = "print(sum(range(10)))"
            out = await registry.execute("code_exec", ctx, code=snippet)
            log.info("code_exec smoke: %s", out)
        except ToolError as e:
            log.warning("code_exec demo skipped: %s", e)

    log.info(
        "done in %.2fs, memory turns=%s, summary_chars=%s",
        time.perf_counter() - t0,
        mem.message_count,
        mem.running_summary_chars,
    )


if __name__ == "__main__":
    asyncio.run(main())
