# Pre-commit Hooks

This directory contains cross-platform Python wrappers for various code quality tools used in pre-commit hooks.

## Structure

- `runner.py` - Main runner module with logging functionality
- `*_wrapper.py` - Individual tool wrappers that import and use the runner
- Logs are written to `../.precommit_logs/` directory

## Tools Included

- **black**: Code formatter
- **autoflake**: Removes unused imports and variables
- **isort**: Import sorter
- **ruff**: Fast Python linter
- **mypy**: Type checker
- **pyupgrade**: Syntax modernizer (Python 2 → 3.9+)
- **vulture**: Dead code detector

## Usage

### Manual Testing
```bash
python .precommit_hooks/black_wrapper.py qkit/core/instrument_base.py
python .precommit_hooks/ruff_wrapper.py qkit/analysis/circle_fit/
```

### Pre-commit Integration
The hooks are configured in `.pre-commit-config.yaml` and will run automatically on `git commit`.

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

Run on all files:
```bash
pre-commit run --all-files
```

## Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Logging**: All tool output is logged with timestamps
- **Error handling**: Graceful handling of missing tools and timeout scenarios
- **Tool-specific logic**: Customized success/failure detection per tool

## Log Files

Logs are written to `.precommit_logs/*.log` files:
- Timestamped entries
- Tool output capture
- Success/failure status
- File-by-file processing details

## Requirements

All tools must be available in PATH:
```bash
pip install black autoflake isort ruff mypy pyupgrade vulture
```
