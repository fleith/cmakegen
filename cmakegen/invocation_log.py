"""Append/read compiler invocations to a JSONL log file."""

import json
import os


DEFAULT_LOG_PATH = ".cmakegen_log.jsonl"


def log_invocation(log_path: str, invocation: dict) -> None:
    """Append a parsed invocation as a JSON line to the log file."""
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(invocation) + "\n")


def read_invocations(log_path: str) -> list[dict]:
    """Read all logged invocations from the log file."""
    if not os.path.exists(log_path):
        return []
    invocations = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                invocations.append(json.loads(line))
    return invocations


def clear_log(log_path: str) -> None:
    """Reset the log file."""
    if os.path.exists(log_path):
        os.remove(log_path)
