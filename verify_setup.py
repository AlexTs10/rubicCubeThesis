#!/usr/bin/env python3
"""
Setup Verification Script for Rubik's Cube Thesis Project

This script verifies that the development environment is correctly set up:
1. Python version
2. Required packages
3. Project structure
4. Core modules functionality
5. Tests can run
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.RESET} {message}")


def check_python_version() -> bool:
    """Check if Python version is adequate."""
    print_section("1. Python Version Check")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print(f"Current Python version: {version_str}")

    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} is supported (>= 3.8 required)")
        return True
    else:
        print_error(f"Python {version_str} is too old (>= 3.8 required)")
        return False


def check_required_packages() -> bool:
    """Check if all required packages are installed."""
    print_section("2. Required Packages Check")

    required_packages = [
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('pytest', 'pytest'),
        ('matplotlib', 'matplotlib'),
        ('pandas', 'pandas'),
    ]

    all_installed = True

    for package_name, import_name in required_packages:
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'unknown')
            print_success(f"{package_name:20s} {version}")
        except ImportError:
            print_error(f"{package_name:20s} NOT INSTALLED")
            all_installed = False

    if all_installed:
        print(f"\n{Colors.GREEN}All required packages are installed{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}Some packages are missing. Run: pip install -r requirements.txt{Colors.RESET}")

    return all_installed


def check_project_structure() -> bool:
    """Check if project structure is correct."""
    print_section("3. Project Structure Check")

    project_root = Path(__file__).parent

    required_dirs = [
        'src',
        'src/cube',
        'src/thistlethwaite',
        'src/kociemba',
        'src/korf',
        'src/utils',
        'src/evaluation',
        'tests',
        'tests/unit',
        'demos',
        'docs',
        'docs/notes',
        'docs/references',
        'data',
        'data/pattern_databases',
        'data/test_cases',
        'results',
    ]

    required_files = [
        'README.md',
        'requirements.txt',
        'src/cube/rubik_cube.py',
        'src/cube/moves.py',
        'src/cube/visualization.py',
        'tests/unit/test_rubik_cube.py',
        'demos/basic_usage.py',
    ]

    all_present = True

    print("Checking directories:")
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"{dir_path:40s}")
        else:
            print_error(f"{dir_path:40s} MISSING")
            all_present = False

    print("\nChecking files:")
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists() and full_path.is_file():
            print_success(f"{file_path:40s}")
        else:
            print_error(f"{file_path:40s} MISSING")
            all_present = False

    return all_present


def check_core_functionality() -> bool:
    """Check if core modules work correctly."""
    print_section("4. Core Functionality Check")

    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        # Test RubikCube import and basic functionality
        print("Testing RubikCube module...")
        from src.cube.rubik_cube import RubikCube, Face

        cube = RubikCube()
        if not cube.is_solved():
            print_error("New cube should be solved")
            return False
        print_success("RubikCube initialization works")

        # Test basic moves
        cube.apply_move('R')
        if cube.is_solved():
            print_error("Cube should not be solved after R move")
            return False
        print_success("Basic moves work")

        cube.apply_move("R'")
        if not cube.is_solved():
            print_error("R R' should return to solved state")
            return False
        print_success("Inverse moves work")

        # Test move sequence
        cube.apply_move_sequence("R U R' U'")
        print_success("Move sequences work")

        # Test scrambling
        cube = RubikCube()
        moves = cube.scramble(moves=10, seed=42)
        if len(moves) != 10:
            print_error(f"Scramble should return 10 moves, got {len(moves)}")
            return False
        print_success("Scrambling works")

        # Test moves module
        print("\nTesting moves module...")
        from src.cube.moves import inverse_move, inverse_sequence, simplify_moves

        if inverse_move('R') != "R'":
            print_error("inverse_move('R') should return R'")
            return False
        print_success("Move utilities work")

        # Test visualization module
        print("\nTesting visualization module...")
        from src.cube.visualization import display_cube_compact, display_cube_state_vector

        cube = RubikCube()
        compact = display_cube_compact(cube)
        if not compact:
            print_error("Visualization should return non-empty string")
            return False
        print_success("Visualization module works")

        print(f"\n{Colors.GREEN}All core functionality tests passed{Colors.RESET}")
        return True

    except Exception as e:
        print_error(f"Error during functionality check: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_tests() -> bool:
    """Check if tests can run."""
    print_section("5. Test Suite Check")

    project_root = Path(__file__).parent
    test_file = project_root / 'tests' / 'unit' / 'test_rubik_cube.py'

    if not test_file.exists():
        print_error("Test file not found")
        return False

    try:
        print("Running test suite...")
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(test_file), '-v', '--tb=short'],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print_success("All tests passed")
            # Show test summary
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'passed' in line.lower() or 'test session starts' in line.lower():
                    print(f"  {line}")
            return True
        else:
            print_error("Some tests failed")
            print("\nTest output:")
            print(result.stdout)
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_error("Tests timed out")
        return False
    except Exception as e:
        print_error(f"Error running tests: {str(e)}")
        return False


def check_demo() -> bool:
    """Check if demo script runs."""
    print_section("6. Demo Script Check")

    project_root = Path(__file__).parent
    demo_file = project_root / 'demos' / 'basic_usage.py'

    if not demo_file.exists():
        print_error("Demo file not found")
        return False

    try:
        print("Running demo script...")
        result = subprocess.run(
            [sys.executable, str(demo_file)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print_success("Demo script runs successfully")
            return True
        else:
            print_error("Demo script failed")
            print("\nDemo output:")
            print(result.stdout)
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_error("Demo script timed out")
        return False
    except Exception as e:
        print_error(f"Error running demo: {str(e)}")
        return False


def check_documentation() -> bool:
    """Check if documentation exists."""
    print_section("7. Documentation Check")

    project_root = Path(__file__).parent

    doc_files = [
        ('README.md', 'Main README'),
        ('docs/notes/01_group_theory_fundamentals.md', 'Group Theory Guide'),
        ('docs/notes/02_singmaster_notation.md', 'Notation Reference'),
    ]

    all_present = True

    for file_path, description in doc_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print_success(f"{description:30s} ({size:,} bytes)")
        else:
            print_warning(f"{description:30s} MISSING")
            all_present = False

    return all_present


def main():
    """Run all verification checks."""
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Rubik's Cube Thesis - Setup Verification{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")

    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("Project Structure", check_project_structure),
        ("Core Functionality", check_core_functionality),
        ("Test Suite", check_tests),
        ("Demo Script", check_demo),
        ("Documentation", check_documentation),
    ]

    results = {}

    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Unexpected error in {name}: {str(e)}")
            results[name] = False

    # Print summary
    print_section("Summary")

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for name, result in results.items():
        if result:
            print_success(f"{name:30s} PASS")
        else:
            print_error(f"{name:30s} FAIL")

    print(f"\n{Colors.BOLD}Overall: {passed}/{total} checks passed{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Setup is complete! Ready to start development.{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed. Please review the output above.{Colors.RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
