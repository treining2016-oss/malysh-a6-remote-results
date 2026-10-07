#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

TASKS = {
    "FC001": {
        "class": "single_file_bugfix",
        "stale_injection": False,
        "files": {
            "calc.py": "def add(a,b):\n    return a-b\n",
            "test_calc.py": "import unittest\nfrom calc import add\nclass T(unittest.TestCase):\n    def test_add(self): self.assertEqual(add(2,3),5)\n",
        },
    },
    "FC002": {
        "class": "multi_file_api_consistency",
        "stale_injection": False,
        "files": {
            "api.py": "def normalize(x): return str(x)\n",
            "client.py": "from api import normalize\ndef render(x): return normalize(x).upper()\n",
            "test_api.py": "import unittest\nfrom client import render\nclass T(unittest.TestCase):\n    def test_render(self): self.assertEqual(render(7),'7')\n",
        },
    },
    "FC003": {
        "class": "stale_repository_state",
        "stale_injection": True,
        "files": {
            "core.py": "def flag(): return True\n",
            "test_core.py": "import unittest\nfrom core import flag\nclass T(unittest.TestCase):\n    def test_flag(self): self.assertIs(flag(),True)\n",
        },
    },
    "FC004": {
        "class": "conflicting_writer",
        "stale_injection": True,
        "files": {
            "value.py": "VALUE=1\n",
            "test_value.py": "import unittest, value\nclass T(unittest.TestCase):\n    def test_value(self): self.assertEqual(value.VALUE,1)\n",
        },
    },
    "FC005": {
        "class": "partial_tool_failure",
        "stale_injection": False,
        "files": {
            "store.py": "def save(x):\n    return {'saved':x}\n",
            "test_store.py": "import unittest\nfrom store import save\nclass T(unittest.TestCase):\n    def test_save(self): self.assertEqual(save(3),{'saved':3})\n",
        },
    },
    "FC006": {
        "class": "plausible_patch_verifier_reject",
        "stale_injection": False,
        "files": {
            "auth.py": "def allowed(role): return role=='admin'\n",
            "test_auth.py": "import unittest\nfrom auth import allowed\nclass T(unittest.TestCase):\n    def test_admin(self): self.assertTrue(allowed('admin'))\n    def test_user(self): self.assertFalse(allowed('user'))\n",
        },
    },
    "FC007": {
        "class": "session_rollover",
        "stale_injection": False,
        "files": {
            "steps.py": "DONE=['a','b']\ndef remaining(): return ['c']\n",
            "test_steps.py": "import unittest\nfrom steps import remaining\nclass T(unittest.TestCase):\n    def test_remaining(self): self.assertEqual(remaining(),['c'])\n",
        },
    },
    "FC008": {
        "class": "code_graph_navigation",
        "stale_injection": False,
        "files": {
            "pkg_a.py": "from pkg_b import value\ndef result(): return value()+1\n",
            "pkg_b.py": "def value(): return 4\n",
            "test_graph.py": "import unittest\nfrom pkg_a import result\nclass T(unittest.TestCase):\n    def test_result(self): self.assertEqual(result(),5)\n",
        },
    },
}

def sh(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated_tasks")
    a = ap.parse_args()
    root = Path(a.out).resolve()
    root.mkdir(parents=True, exist_ok=True)

    for task_id, spec in TASKS.items():
        task = root / task_id
        repo = task / "repo"
        if task.exists():
            shutil.rmtree(task)
        repo.mkdir(parents=True)

        for name, body in spec["files"].items():
            (repo / name).write_text(body)

        (task / "task.json").write_text(json.dumps({
            "task_id": task_id,
            "class": spec["class"],
            "stale_injection": spec["stale_injection"],
        }, sort_keys=True, indent=2) + "\n")

        sh(["git", "init", "-q"], repo)
        sh(["git", "add", "."], repo)
        sh([
            "git", "-c", "user.name=benchmark",
            "-c", "user.email=benchmark@example.invalid",
            "commit", "-qm", "benchmark baseline"
        ], repo)

    print(root)

if __name__ == "__main__":
    main()
