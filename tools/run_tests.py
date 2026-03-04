#!/usr/bin/env python3
"""Run showcase unit tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

subprocess.run(["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], cwd=ROOT, check=True)
print("All tests passed.")
