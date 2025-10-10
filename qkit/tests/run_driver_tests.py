#!/usr/bin/env python3
"""
Test runner for qkit driver tests.

This script provides an easy way to run driver tests with various options.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_driver_tests(test_name=None, verbose=False, coverage=False, markers=None):
    """Run driver tests with specified options."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    if test_name:
        if test_name in ['dummy', 'dummyvna']:
            cmd.append("qkit/tests/drivers/test_dummy_vna.py")
        elif test_name in ['keysight', 'p50xxa']:
            cmd.append("qkit/tests/drivers/test_keysight_vna_p50xxa.py")
        else:
            cmd.append(f"qkit/tests/drivers/test_{test_name}.py")
    else:
        cmd.append("qkit/tests/drivers/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=qkit.drivers",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Add markers
    if markers:
        if isinstance(markers, str):
            markers = [markers]
        for marker in markers:
            cmd.extend(["-m", marker])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--strict-markers"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Run qkit driver tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run all driver tests
  %(prog)s --test dummy            # Run only DummyVNA tests
  %(prog)s --test keysight         # Run only Keysight VNA tests
  %(prog)s --verbose               # Run with verbose output
  %(prog)s --coverage              # Run with coverage report
  %(prog)s --markers unit          # Run only unit tests
  %(prog)s --markers "not slow"    # Run all except slow tests
        """
    )
    
    parser.add_argument(
        "--test", "-t",
        help="Specific test to run (dummy, keysight, or test file name)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true", 
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--markers", "-m",
        nargs="*",
        help="Pytest markers to filter tests (e.g., unit, integration, slow)"
    )
    
    parser.add_argument(
        "--list-tests", "-l",
        action="store_true",
        help="List available tests without running them"
    )
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("Available driver tests:")
        test_dir = Path("qkit/tests/drivers")
        if test_dir.exists():
            for test_file in test_dir.glob("test_*.py"):
                print(f"  {test_file.stem}")
        else:
            print("  No test directory found")
        return 0
    
    return run_driver_tests(
        test_name=args.test,
        verbose=args.verbose,
        coverage=args.coverage,
        markers=args.markers
    )


if __name__ == "__main__":
    sys.exit(main())
