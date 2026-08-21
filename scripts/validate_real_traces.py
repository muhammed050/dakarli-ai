from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("data/real_traces")
SCHEMA = ROOT / "schema.json"

required = {"trace_id", "source_type", "tool", "request", "steps", "outcome", "verification", "quality"}
allowed_sources = {"verified_connector", "verified_runtime", "verified_browser"}
allowed_kinds = {"plan", "tool_call", "observation", "decision", "correction", "verification"}

schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
assert schema["title"] == "Dakarli Verified Tool Trace"

seen: set[str] = set()
count = 0
for path in sorted(ROOT.rglob("*.json")):
    if path == SCHEMA:
        continue
    row = json.loads(path.read_text(encoding="utf-8"))
    missing = required - row.keys()
    assert not missing, f"{path}: missing {sorted(missing)}"
    assert row["source_type"] in allowed_sources, f"{path}: invalid source_type"
    assert row["trace_id"] not in seen, f"duplicate trace_id: {row['trace_id']}"
    seen.add(row["trace_id"])
    assert row["quality"]["verified"] is True, f"{path}: trace is not verified"
    assert row["quality"]["secrets_removed"] is True, f"{path}: secrets_removed must be true"
    assert row["steps"], f"{path}: empty steps"
    for step in row["steps"]:
        assert step["kind"] in allowed_kinds, f"{path}: invalid step kind"
    kinds = {step["kind"] for step in row["steps"]}
    assert "tool_call" in kinds, f"{path}: no tool_call"
    assert "observation" in kinds or "verification" in kinds, f"{path}: no evidence step"
    count += 1

print(f"Verified real traces OK: {count}")