"""Append-only audit trail of agent-loop activity.

Every chat turn appends entries to output/audit_trail.json: one per tool the
agent called (time, tool name, short args, short result) and the stop reason for
the turn. The file is never truncated or wiped between runs; it is loaded,
extended, and rewritten under a lock, so the history survives server restarts.

Entry shape:
    {
      "timestamp": ISO-8601 UTC,
      "turn_id":   short id grouping one shopper message's activity,
      "user":      user id, or "guest",
      "tool_name": the tool called, or null for the turn-end summary,
      "args":      short string of the call arguments, or null,
      "result":    short string of the tool result or the final reply,
      "stop_reason": "tool_use" | "completed" | "content_filter" | "error"
    }
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"

# PydanticAI's structured-output tool; a call to it means the loop is finishing.
_OUTPUT_TOOL = "final_result"
_MAX = 200  # truncate args/results to keep the log readable

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _short(value: Any, limit: int = _MAX) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def new_turn_id() -> str:
    return uuid.uuid4().hex[:8]


def _append(entries: list[dict]) -> None:
    if not entries:
        return
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        existing: list = []
        if AUDIT_PATH.exists():
            try:
                existing = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            except json.JSONDecodeError:
                existing = []
        existing.extend(entries)
        AUDIT_PATH.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


def record_run(turn_id: str, user: str, new_messages: list, final_reply: str) -> None:
    """Walk one run's messages and append an entry per tool call plus a summary.

    `new_messages` is the PydanticAI message list from this run
    (result.new_messages()). Tool calls and their returns are paired by id.
    """
    returns: dict[str, Any] = {}
    calls: list[tuple[str, Any, str | None]] = []  # (tool_name, args, call_id)

    for message in new_messages:
        for part in getattr(message, "parts", []):
            kind = getattr(part, "part_kind", None)
            if kind == "tool-return":
                returns[getattr(part, "tool_call_id", "")] = getattr(part, "content", "")
            elif kind == "tool-call":
                calls.append(
                    (
                        getattr(part, "tool_name", "?"),
                        getattr(part, "args", None),
                        getattr(part, "tool_call_id", None),
                    )
                )

    entries = []
    for tool_name, args, call_id in calls:
        is_output = tool_name == _OUTPUT_TOOL
        entries.append(
            {
                "timestamp": _now(),
                "turn_id": turn_id,
                "user": user,
                "tool_name": tool_name,
                "args": _short(args) if args is not None else None,
                "result": _short(returns.get(call_id, "")) if not is_output else None,
                "stop_reason": "completed" if is_output else "tool_use",
            }
        )

    # Turn-end summary carries the final reply and the completed stop reason.
    entries.append(
        {
            "timestamp": _now(),
            "turn_id": turn_id,
            "user": user,
            "tool_name": None,
            "args": None,
            "result": _short(final_reply),
            "stop_reason": "completed",
        }
    )
    _append(entries)


def record_event(turn_id: str, user: str, stop_reason: str, detail: str) -> None:
    """Append a single entry for a turn that ended without a normal result
    (e.g. a content-filter block or an error)."""
    _append(
        [
            {
                "timestamp": _now(),
                "turn_id": turn_id,
                "user": user,
                "tool_name": None,
                "args": None,
                "result": _short(detail),
                "stop_reason": stop_reason,
            }
        ]
    )
