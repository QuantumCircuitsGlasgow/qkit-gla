#!/usr/bin/env python3
"""
Extract dependencies and create pip-installable build system for qkit.

This script will:
1. Scan all Python files for import statements
2. Extract exact versions of installed packages
3. Create modern pyproject.toml for pip installation
4. Generate pinned requirements.txt files
5. Create development and test requirement files
"""

import ast
import os
import pathlib
import re
import subprocess
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple


def find_all_python_files(root_dir: pathlib.Path) -> list[pathlib.Path]:
    """Find all Python files in the project."""
    python_files = []
    for file_path in root_dir.rglob("*.py"):
        # Skip __pycache__ and .git directories
        if "__pycache__" in str(file_path) or ".git" in str(file_path):
            continue
        python_files.append(file_path)
    return python_files


def extract_imports_from_file(file_path: pathlib.Path) -> set[str]:
    """Extract import statements from a Python file using AST."""
    imports = set()
    
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Parse with AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get top-level package name
                        package = alias.name.split('.')[0]
                        imports.add(package)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Get top-level package name
                        package = node.module.split('.')[0]
                        imports.add(package)
        except SyntaxError:
            # Fallback to regex parsing for files with syntax errors
            import_regex = re.compile(r'^(?:from\s+(\S+)\s+)?import\s+([^#\n]+)', re.MULTILINE)
            for match in import_regex.finditer(content):
                module = match.group(1) if match.group(1) else match.group(2)
                if module:
                    # Extract first part of module name
                    package = module.split('.')[0].strip()
                    imports.add(package)
    
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}")
    
    return imports


def get_installed_packages() -> dict[str, str]:
    """Get list of installed packages with versions."""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=freeze"], 
                              capture_output=True, text=True, check=True)
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                packages[name.lower()] = version
        return packages
    except subprocess.CalledProcessError as e:
        print(f"Error getting installed packages: {e}")
        return {}


def map_import_to_package(import_name: str) -> str:
    """Map import names to PyPI package names."""
    # Common mappings from import name to PyPI package name
    import_to_package = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'zmq': 'pyzmq',
        'sklearn': 'scikit-learn',
        'skimage': 'scikit-image',
        'cv': 'opencv-python',
        'Image': 'Pillow',
        'serial': 'pyserial',
        'usb': 'pyusb',
        'visa': 'PyVISA',
        'win32com': 'pywin32',
        'pythoncom': 'pywin32',
        'pywintypes': 'pywin32',
        'PyQt5': 'PyQt5',
        'PyQt6': 'PyQt6',
        'PySide2': 'PySide2',
        'PySide6': 'PySide6',
        'qt': 'PyQt5',
        'zhinst': 'zhinst',
        'uncertainties': 'uncertainties',
        'lmfit': 'lmfit',
        'colorlog': 'colorlog',
        'prettytable': 'prettytable',
        'tabulate': 'tabulate',
        'progressbar': 'progressbar2',
        'tqdm': 'tqdm',
        'requests': 'requests',
        'flask': 'Flask',
        'fastapi': 'fastapi',
        'pandas': 'pandas',
        'seaborn': 'seaborn',
        'plotly': 'plotly',
        'bokeh': 'bokeh',
        'dash': 'dash',
        'ipython': 'ipython',
        'jupyter': 'jupyter',
        'notebook': 'notebook',
        'jupyterlab': 'jupyterlab',
        'ipywidgets': 'ipywidgets'
    }
    
    return import_to_package.get(import_name.lower(), import_name.lower())


def classify_dependencies(all_imports: set[str], installed_packages: dict[str, str]) -> tuple[dict[str, str], set[str], set[str]]:
    """Classify dependencies into core, missing, and stdlib."""
    # Python standard library modules (not exhaustive, but covers common ones)
    stdlib_modules = {
        'os', 'sys', 'time', 'datetime', 'math', 'random', 'json', 'csv', 'xml',
        'urllib', 'http', 'email', 'html', 'collections', 'itertools', 'functools',
        'operator', 'pathlib', 'glob', 'shutil', 'tempfile', 'subprocess', 'threading',
        'multiprocessing', 'queue', 'socket', 'ssl', 'hashlib', 'hmac', 'uuid',
        'pickle', 'copy', 'pprint', 'textwrap', 're', 'string', 'io', 'struct',
        'codecs', 'unicodedata', 'logging', 'warnings', 'traceback', 'inspect',
        'gc', 'weakref', 'types', 'abc', 'contextlib', 'atexit', 'argparse',
        'configparser', 'getpass', 'platform', 'stat', 'filecmp', 'tarfile',
        'zipfile', 'gzip', 'bz2', 'lzma', 'sqlite3', 'dbm', 'decimal', 'fractions',
        'base64', 'binascii', 'quopri', 'uu', 'zlib', 'builtins', 'importlib',
        'pkgutil', 'keyword', 'token', 'tokenize', 'ast', 'symtable', 'py_compile',
        'compileall', 'dis', 'pickletools', '__future__', 'typing', 'unittest',
        'doctest', 'test', 'pdb', 'profile', 'pstats', 'timeit', 'trace',
        'faulthandler', 'tracemalloc'
    }
    
    core_deps = {}
    missing_deps = set()
    stdlib_deps = set()
    
    for import_name in all_imports:
        if import_name in stdlib_modules:
            stdlib_deps.add(import_name)
        else:
            package_name = map_import_to_package(import_name)
            if package_name in installed_packages:
                core_deps[package_name] = installed_packages[package_name]
            else:
                missing_deps.add(import_name)
    
    return core_deps, missing_deps, stdlib_deps


def create_pyproject_toml(core_deps: dict[str, str], project_info: dict[str, str]) -> str:
    """Create a modern pyproject.toml file."""
    
    # Format dependencies for pyproject.toml
    formatted_deps = []
    for package, version in sorted(core_deps.items()):
        formatted_deps.append(f'    "{package}>={version}"')
    
    deps_str = ',\n'.join(formatted_deps)
    
    # Development dependencies
    dev_deps = [
        '    "pytest>=7.0.0"',
        '    "pytest-cov>=4.0.0"',
        '    "black>=23.0.0"',
        '    "isort>=5.0.0"',
        '    "ruff>=0.1.0"',
        '    "mypy>=1.0.0"',
        '    "autoflake>=2.0.0"',
        '    "pyupgrade>=3.0.0"',
        '    "vulture>=2.0.0"',
        '    "pre-commit>=3.0.0"',
        '    "pip-tools>=7.0.0"'
    ]
    
    dev_deps_str = ',\n'.join(dev_deps)
    
    pyproject_content = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_info['name']}"
version = "{project_info['version']}"
description = "{project_info['description']}"
readme = "README.md"
license = {{file = "LICENSE"}}
authors = [
    {{name = "{project_info['author']}", email = "{project_info['author_email']}"}}
]
maintainers = [
    {{name = "{project_info['maintainer']}", email = "{project_info['maintainer_email']}"}}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Software Development :: Libraries :: Python Modules"
]
keywords = ["physics", "quantum", "measurement", "superconducting", "resonator"]
requires-python = ">=3.9"
dependencies = [
{deps_str}
]

[project.optional-dependencies]
dev = [
{dev_deps_str}
]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.0.0"
]
docs = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.18.0"
]
all = [
    "qkit[dev,test,docs]"
]

[project.urls]
Homepage = "{project_info['homepage']}"
Documentation = "{project_info['documentation']}"
Repository = "{project_info['repository']}"
Issues = "{project_info['issues']}"

[project.scripts]
qkit = "qkit.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["qkit*"]
exclude = ["tests*", "docs*", "*.tests*", "*.tests"]

[tool.setuptools.package-data]
qkit = ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"]

[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311", "py312"]
include = '\\.pyi?$'
extend-exclude = """
(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
"""

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["qkit"]

[tool.ruff]
line-length = 88
target-version = "py39"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --cov=qkit --cov-report=term-missing"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]

[tool.coverage.run]
source = ["qkit"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/.*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
'''
    
    return pyproject_content


def create_requirements_files(core_deps: dict[str, str]) -> tuple[str, str, str]:
    """Create requirements.txt, requirements-dev.txt, and requirements-test.txt."""
    
    # Core requirements
    requirements_content = "# Core qkit dependencies\n"
    for package, version in sorted(core_deps.items()):
        requirements_content += f"{package}=={version}\n"
    
    # Development requirements
    dev_requirements_content = """# Development dependencies for qkit
-r requirements.txt

# Code formatting and linting
black>=23.0.0
isort>=5.0.0
ruff>=0.1.0
mypy>=1.0.0
autoflake>=2.0.0
pyupgrade>=3.0.0
vulture>=2.0.0

# Pre-commit hooks
pre-commit>=3.0.0

# Build tools
pip-tools>=7.0.0
build>=0.10.0
twine>=4.0.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
myst-parser>=0.18.0
"""
    
    # Test requirements
    test_requirements_content = """# Test dependencies for qkit
-r requirements.txt

# Testing framework
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.0.0
pytest-xdist>=3.0.0
pytest-benchmark>=4.0.0

# Test utilities
factory-boy>=3.2.0
faker>=19.0.0
"""
    
    return requirements_content, dev_requirements_content, test_requirements_content


def main():
    """Main function to extract dependencies and create build system."""
    print("🔍 Extracting dependencies for qkit...")
    
    # Project root
    root_dir = pathlib.Path(__file__).parent
    qkit_dir = root_dir / "qkit"
    
    # Project metadata
    project_info = {
        'name': 'qkit',
        'version': '0.2.0',
        'description': 'A quantum measurement toolkit for superconducting qubits and resonators',
        'author': 'Qkit Team',
        'author_email': 'qkit@example.com',
        'maintainer': 'Qkit Maintainers',
        'maintainer_email': 'qkit-maintainers@example.com',
        'homepage': 'https://github.com/qkitgroup/qkit',
        'documentation': 'https://qkit.readthedocs.io',
        'repository': 'https://github.com/qkitgroup/qkit',
        'issues': 'https://github.com/qkitgroup/qkit/issues'
    }
    
    # Find all Python files
    print("📁 Finding Python files...")
    python_files = find_all_python_files(root_dir)
    print(f"Found {len(python_files)} Python files")
    
    # Extract all imports
    print("📦 Extracting imports...")
    all_imports = set()
    for file_path in python_files:
        file_imports = extract_imports_from_file(file_path)
        all_imports.update(file_imports)
    
    print(f"Found {len(all_imports)} unique imports")
    
    # Get installed packages
    print("🔍 Getting installed package versions...")
    installed_packages = get_installed_packages()
    print(f"Found {len(installed_packages)} installed packages")
    
    # Classify dependencies
    print("📋 Classifying dependencies...")
    core_deps, missing_deps, stdlib_deps = classify_dependencies(all_imports, installed_packages)
    
    print(f"Core dependencies: {len(core_deps)}")
    print(f"Missing dependencies: {len(missing_deps)}")
    print(f"Standard library: {len(stdlib_deps)}")
    
    # Display results
    print("\n🎯 CORE DEPENDENCIES:")
    for package, version in sorted(core_deps.items()):
        print(f"  {package}=={version}")
    
    if missing_deps:
        print("\n⚠️  MISSING DEPENDENCIES:")
        for dep in sorted(missing_deps):
            print(f"  {dep}")
    
    # Create build files
    print("\n📝 Creating build system files...")
    
    # Create pyproject.toml
    pyproject_content = create_pyproject_toml(core_deps, project_info)
    with open(root_dir / "pyproject.toml", "w", encoding="utf-8") as f:
        f.write(pyproject_content)
    print("✅ Created pyproject.toml")
    
    # Create requirements files
    req_content, dev_req_content, test_req_content = create_requirements_files(core_deps)
    
    with open(root_dir / "requirements-pinned.txt", "w", encoding="utf-8") as f:
        f.write(req_content)
    print("✅ Created requirements-pinned.txt")
    
    with open(root_dir / "requirements-dev.txt", "w", encoding="utf-8") as f:
        f.write(dev_req_content)
    print("✅ Created requirements-dev.txt")
    
    with open(root_dir / "requirements-test.txt", "w", encoding="utf-8") as f:
        f.write(test_req_content)
    print("✅ Created requirements-test.txt")
    
    # Create installation instructions
    install_instructions = f"""# Qkit Installation Guide

## Install from PyPI (after publishing)
```bash
pip install qkit
```

## Install from source (development)
```bash
# Clone the repository
git clone https://github.com/qkitgroup/qkit.git
cd qkit

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]

# Or install with all optional dependencies
pip install -e .[all]
```

## Install specific requirement sets
```bash
# Core dependencies only
pip install -r requirements-pinned.txt

# Development dependencies
pip install -r requirements-dev.txt

# Test dependencies
pip install -r requirements-test.txt
```

## Build and publish (for maintainers)
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Pre-commit hooks setup
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Dependencies Summary

### Core Dependencies ({len(core_deps)} packages):
"""
    
    for package, version in sorted(core_deps.items()):
        install_instructions += f"- {package}=={version}\n"
    
    if missing_deps:
        install_instructions += f"\n### Missing Dependencies ({len(missing_deps)} packages):\n"
        for dep in sorted(missing_deps):
            install_instructions += f"- {dep} (needs to be installed manually)\n"
    
    with open(root_dir / "INSTALL.md", "w", encoding="utf-8") as f:
        f.write(install_instructions)
    print("✅ Created INSTALL.md")
    
    print("\n🎉 Build system created successfully!")
    print("\nNext steps:")
    print("1. Review and adjust pyproject.toml metadata")
    print("2. Install missing dependencies if needed")
    print("3. Test installation: pip install -e .")
    print("4. Run tests: pytest")
    print("5. Build package: python -m build")


if __name__ == "__main__":
    main()
