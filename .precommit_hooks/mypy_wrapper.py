#!/usr/bin/env python3
"""MyPy type checker runner with logging."""

import sys
from pathlib import Path

# Add parent directory to path to import runner
sys.path.insert(0, str(Path(__file__).parent))
from runner import run_tool

if __name__ == "__main__":
    sys.exit(run_tool("mypy", ["--ignore-missing-imports"], sys.argv[1:]))
