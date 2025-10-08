#!/usr/bin/env python3
"""Cross-platform pre-commit hook runner with logging."""

import argparse
import datetime
import os
import pathlib
import shutil
import subprocess
import sys
from typing import List, Optional


def setup_logging(tool_name: str) -> pathlib.Path:
    """Set up logging directory and return log file path."""
    log_dir = pathlib.Path(__file__).parent.parent / ".precommit_logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir / f"{tool_name}.log"


def log_message(log_file: pathlib.Path, message: str) -> None:
    """Write timestamped message to log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def check_tool_available(tool_name: str) -> bool:
    """Check if a tool is available in PATH."""
    return shutil.which(tool_name) is not None


def run_tool(tool_name: str, args: list[str], files: list[str]) -> int:
    """Run a tool on the given files with logging."""
    log_file = setup_logging(tool_name)
    log_message(log_file, f"START {tool_name} runner")
    
    if not check_tool_available(tool_name):
        log_message(log_file, f"ERROR: {tool_name} not found in PATH")
        return 1
    
    if not files:
        log_message(log_file, "No files passed")
        return 0
    
    failed = False
    
    for file_path in files:
        if not os.path.exists(file_path):
            log_message(log_file, f"Skip missing: {file_path}")
            continue
        
        cmd = [tool_name] + args + [file_path]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=100
            )
            
            if result.returncode != 0:
                log_message(log_file, f"ERROR {file_path}")
                log_message(log_file, f"stdout: {result.stdout}")
                log_message(log_file, f"stderr: {result.stderr}")
                failed = True
            else:
                # Check for tool-specific success indicators
                output = result.stdout + result.stderr
                if tool_name == "isort" and ("Fixing" in output or "Reordered" in output or "would reorder" in output.lower()):
                    log_message(log_file, f"IMPORT CHANGES NEEDED: {file_path}")
                    log_message(log_file, f"output: {output}")
                    # For isort --check-only, this indicates changes are needed
                    if "--check-only" in args:
                        failed = True
                elif tool_name == "vulture" and "unused" in output.lower():
                    log_message(log_file, f"UNUSED candidates: {file_path}")
                    log_message(log_file, f"output: {output}")
                    # Vulture finding unused code is informational, not necessarily failure
                    # failed = True  # Uncomment if you want vulture findings to fail the hook
                elif tool_name == "autoflake" and ("import" in output.lower() or "unused" in output.lower()):
                    log_message(log_file, f"CLEANED IMPORTS: {file_path}")
                    log_message(log_file, f"output: {output}")
                elif tool_name == "black" and ("would reformat" in output.lower() or "reformatted" in output.lower()):
                    log_message(log_file, f"FORMATTING CHANGES NEEDED: {file_path}")
                    log_message(log_file, f"output: {output}")
                    if "--check" in args:
                        failed = True
                elif tool_name == "mypy" and ("error:" in output or "Error:" in output):
                    log_message(log_file, f"TYPE ERROR {file_path}")
                    log_message(log_file, f"output: {output}")
                    failed = True
                elif tool_name == "ruff" and ("error" in output.lower() or "warning" in output.lower()):
                    log_message(log_file, f"LINT ISSUES: {file_path}")
                    log_message(log_file, f"output: {output}")
                    # Ruff with --fix will return 0 even if it fixed issues
                elif tool_name == "pyupgrade" and ("upgrading" in output.lower() or "rewriting" in output.lower()):
                    log_message(log_file, f"SYNTAX UPGRADED: {file_path}")
                    log_message(log_file, f"output: {output}")
                else:
                    log_message(log_file, f"OK {file_path}")
                    if output.strip():  # Log any unexpected output
                        log_message(log_file, f"output: {output}")
                    
        except subprocess.TimeoutExpired:
            log_message(log_file, f"TIMEOUT {file_path}")
            failed = True
        except Exception as e:
            log_message(log_file, f"EXCEPTION {file_path}: {e}")
            failed = True
    
    log_message(log_file, f"END (failed={failed})")
    return 1 if failed else 0


def main():
    """Main entry point for tool runners."""
    parser = argparse.ArgumentParser(description="Pre-commit hook runner")
    parser.add_argument("tool", help="Tool name to run")
    parser.add_argument("files", nargs="*", help="Files to process")
    parser.add_argument("--args", help="Additional arguments for the tool", default="")
    
    args = parser.parse_args()
    
    # Parse additional arguments
    tool_args = args.args.split() if args.args else []
      # Tool-specific default arguments
    if args.tool == "black":
        tool_args = tool_args or ["--check", "--diff"]
    elif args.tool == "autoflake":
        tool_args = tool_args or [
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--in-place",
            "--expand-star-imports"
        ]
    elif args.tool == "isort":
        tool_args = tool_args or ["--check-only", "--diff"]
    elif args.tool == "vulture":
        tool_args = tool_args or ["--min-confidence", "80"]
    elif args.tool == "ruff":
        tool_args = tool_args or ["check", "--fix"]
    elif args.tool == "pyupgrade":
        tool_args = tool_args or ["--py39-plus"]
    elif args.tool == "mypy":
        tool_args = tool_args or ["--ignore-missing-imports"]
    
    return run_tool(args.tool, tool_args, args.files)


if __name__ == "__main__":
    sys.exit(main())
