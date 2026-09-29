"""Saved outputs. Every search/ask/chat turn is appended to a JSONL run log,
and `wiki eval` writes one Markdown evidence card per test question.
"""

import datetime as dt
import json
import socket
import uuid

from . import config

_runtime = None


def runtime():
    """Model/runtime identity, fetched once per process."""
    global _runtime
    if _runtime is None:
        from . import llm
        _runtime = llm.runtime_info()
    return _runtime


def internet_reachable():
    """Recorded with each run as proof of offline execution (False = offline)."""
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=1.5).close()
        return True
    except OSError:
        return False


def log_run(mode, **fields):
    now = dt.datetime.now()
    record = {
        "run_id": now.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6],
        "time": now.isoformat(timespec="seconds"),
        "mode": mode,
        "execution": "local",
        "internet_reachable": internet_reachable(),
        **({"runtime": runtime()} if mode != "search" else {}),
        **fields,
    }
    if "passages" in record:
        record["passages"] = [
            {k: p.get(k) for k in ("id", "path", "location", "score", "terms", "text")}
            for p in record["passages"]]
    config.RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.RUN_LOG_DIR / f"{now:%Y-%m-%d}.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
