# small helpers for local agent runs; keeps notebooks from duplicating glue code
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def new_session_id() -> str:
    # stable enough for filenames and db uuid columns
    return str(uuid.uuid4())


@dataclass
class RunPaths:
    root: Path

    def log_path(self, session: str) -> Path:
        d = self.root / "logs" / session
        d.mkdir(parents=True, exist_ok=True)
        return d / "events.jsonl"


def append_event(paths: RunPaths, session: str, event: Mapping[str, Any]) -> None:
    # jsonl so a crashed process does not corrupt the whole file
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **dict(event),
    }
    p = paths.log_path(session)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def read_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))


def rough_token_estimate(text: str) -> int:
    # cheap heuristic when you do not want to pull tiktoken in a tiny script
    if not text:
        return 0
    words = max(1, len(text.split()))
    return int(words * 1.3)


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    rp = RunPaths(base)
    sid = new_session_id()
    append_event(rp, sid, {"kind": "boot", "msg": "smoke test"})
    print("wrote", rp.log_path(sid))
