from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ALLOWED_SPLITS = {"train", "validation", "test"}
ALLOWED_TASKS = {"sft", "tool_calling", "agent_trajectory", "debugging", "seo_audit", "safety", "evaluation"}
ROLES = {"system", "user", "assistant", "tool"}


def validate(path: Path) -> tuple[int, Counter, Counter]:
    ids: set[str] = set()
    splits: Counter = Counter()
    tasks: Counter = Counter()
    errors: list[str] = []
    rows = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        rows += 1
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc}")
            continue
        required = {"id", "split", "task", "messages", "quality"}
        missing = required - item.keys()
        if missing:
            errors.append(f"line {line_no}: missing {sorted(missing)}")
        if item.get("id") in ids:
            errors.append(f"line {line_no}: duplicate id {item.get('id')}")
        ids.add(item.get("id"))
        if item.get("split") not in ALLOWED_SPLITS:
            errors.append(f"line {line_no}: invalid split")
        if item.get("task") not in ALLOWED_TASKS:
            errors.append(f"line {line_no}: invalid task")
        messages = item.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            errors.append(f"line {line_no}: messages must contain at least system/user/assistant context")
        else:
            for m in messages:
                if not isinstance(m, dict) or m.get("role") not in ROLES or not isinstance(m.get("content"), str) or not m["content"].strip():
                    errors.append(f"line {line_no}: malformed message")
            if not any(m.get("role") == "user" for m in messages):
                errors.append(f"line {line_no}: no user message")
            if not any(m.get("role") == "assistant" for m in messages):
                errors.append(f"line {line_no}: no assistant message")
        quality = item.get("quality")
        if not isinstance(quality, dict) or quality.get("difficulty") not in {"easy", "medium", "hard", "expert"}:
            errors.append(f"line {line_no}: invalid quality.difficulty")
        splits[item.get("split")] += 1
        tasks[item.get("task")] += 1
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} errors across {rows} rows")
        for error in errors[:50]:
            print(error)
        raise SystemExit(1)
    print(f"VALIDATION OK: {rows} rows; {len(ids)} unique IDs")
    print("splits:", dict(splits))
    print("tasks:", dict(tasks))
    return rows, splits, tasks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="data/generated/all.jsonl")
    args = parser.parse_args()
    validate(Path(args.path))


if __name__ == "__main__":
    main()
