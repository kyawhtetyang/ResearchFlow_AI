#!/usr/bin/env python3
"""Restore text snapshot, then refill externalized assets."""
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run(script_name: str) -> int:
    path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(path):
        print(f"❌ Missing {script_name} at {path}")
        return 1
    return subprocess.call([sys.executable, path])


def main() -> int:
    code = run("run.py")
    if code != 0:
        return code
    return run("run_refill.py")


if __name__ == "__main__":
    raise SystemExit(main())
