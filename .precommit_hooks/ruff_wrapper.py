#!/usr/bin/env python3
"""Ruff linter runner with logging."""

import sys
from pathlib import Path

# Add parent directory to path to import runner
sys.path.insert(0, str(Path(__file__).parent))
from runner import run_tool

if __name__ == "__main__":
    sys.exit(run_tool("ruff", ["check", "--fix"], sys.argv[1:]))
