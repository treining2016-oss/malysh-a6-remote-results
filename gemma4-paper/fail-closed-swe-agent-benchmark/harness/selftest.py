#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BUILDER = HERE / "build_fixtures.py"
EVALUATOR = HERE / "evaluate_candidate.py"

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)

def main():
    with tempfile.TemporaryDirectory(prefix="fail-closed-swe-") as td:
        temp = Path(td)
        source = temp / "source"
        run(["python3", str(BUILDER), "--out", str(source)])

        cases = [("FC008", "GREEN"), ("FC003", "STALE")]
        observed = {}

        for task_id, expected in cases:
            attempt = temp / ("attempt-" + task_id)
            attempt.mkdir()
            shutil.copy2(source / task_id / "task.json", attempt / "task.json")
            run(["git", "clone", "-q", str(source / task_id / "repo"), str(attempt / "repo")])

            receipt = temp / (task_id + ".json")
            run([
                "python3", str(EVALUATOR),
                "--task-dir", str(attempt),
                "--variant", "SELFTEST",
                "--receipt-out", str(receipt),
            ])
            result = json.loads(receipt.read_text())
            observed[task_id] = result["promotion_verdict"]

            if result["promotion_verdict"] != expected:
                raise SystemExit(
                    f"{task_id}: expected {expected}, got {result['promotion_verdict']}"
                )

        print(json.dumps({
            "status": "GREEN",
            "expected": dict(cases),
            "observed": observed,
        }, sort_keys=True))

if __name__ == "__main__":
    main()
