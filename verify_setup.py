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
import argparse
import importlib
import importlib.metadata
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, Iterable, Tuple


# The full repository suite includes exact-solver validation and can run much
# longer on colder caches or nested subprocess execution than it does in an
# already-warmed interactive shell.
FAST_TEST_TIMEOUT_SECONDS = 120
FULL_TEST_TIMEOUT_SECONDS = 1800
DEMO_TIMEOUT_SECONDS = 60
NOTEBOOK_TIMEOUT_SECONDS = 30
THESIS_ARTIFACT_TIMEOUT_SECONDS = 300
WEBAPP_ARTIFACT_TIMEOUT_SECONDS = 300


GENERATED_CACHE_DIRS = [
    'data',
    'data/kociemba',
    'data/kociemba/move_tables',
    'data/kociemba/pruning_tables',
    'data/move_tables',
    'data/pattern_databases',
    'data/pattern_databases/native_exact',
    'data/pruning_tables',
]

PACKAGE_IMPORTS: Dict[str, str] = {
    "RubikOptimal": "spec:optimal",
    "pillow": "PIL",
    "black": "black",
    "dataclasses-json": "dataclasses_json",
    "imageio": "imageio",
    "ipywidgets": "ipywidgets",
    "jupyter": "jupyter",
    "jupyterlab": "jupyterlab",
    "kociemba": "kociemba",
    "line-profiler": "line_profiler",
    "matplotlib": "matplotlib",
    "memory-profiler": "memory_profiler",
    "mypy": "mypy",
    "numpy": "numpy",
    "pandas": "pandas",
    "plotly": "plotly",
    "psutil": "psutil",
    "pylint": "pylint",
    "pytest": "pytest",
    "pytest-benchmark": "pytest_benchmark",
    "pytest-cov": "pytest_cov",
    "rich": "rich",
    "scipy": "scipy",
    "seaborn": "seaborn",
    "streamlit": "streamlit",
}


def iter_requirements(requirements_path: Path) -> Iterable[Tuple[str, str, str | None]]:
    """Yield package names, import targets, and exact pins from a requirements file."""
    for raw_line in requirements_path.read_text().splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("--", "-r ", "-c ")):
            continue
        line = line.removesuffix("\\").strip()
        package_name = line
        expected_version = None
        if "==" in package_name:
            package_name, expected_version = [part.strip() for part in package_name.split("==", 1)]
            yield package_name, PACKAGE_IMPORTS.get(package_name, package_name.replace("-", "_")), expected_version
            continue
        for separator in ("==", ">=", "<=", "~=", ">", "<"):
            if separator in package_name:
                package_name = package_name.split(separator, 1)[0].strip()
                break
        yield package_name, PACKAGE_IMPORTS.get(package_name, package_name.replace("-", "_")), expected_version


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

    if version.major == 3 and 12 <= version.minor <= 14:
        print_success(f"Python {version_str} is supported (Python 3.12-3.14)")
        return True
    else:
        print_error(f"Python {version_str} is outside the supported range (Python 3.12-3.14)")
        return False


def check_required_packages(requirements_path: Path) -> bool:
    """Check if all required packages are installed."""
    print_section("2. Required Packages Check")

    print(f"Checking packages from: {requirements_path}")
    required_packages = list(iter_requirements(requirements_path))

    all_installed = True

    for package_name, import_name, expected_version in required_packages:
        try:
            version = importlib.metadata.version(package_name)
            if expected_version is not None and version != expected_version:
                print_error(f"{package_name:20s} {version} installed, expected {expected_version}")
                all_installed = False
                continue
            print_success(f"{package_name:20s} {version}")
            continue
        except importlib.metadata.PackageNotFoundError:
            pass

        if import_name.startswith('spec:'):
            package_spec = import_name.split(':', 1)[1]
            installed = importlib.util.find_spec(package_spec) is not None
        else:
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'installed')
                print_success(f"{package_name:20s} {version}")
                continue
            except ImportError:
                installed = False

        if installed:
            print_success(f"{package_name:20s} installed")
        else:
            print_error(f"{package_name:20s} NOT INSTALLED")
            all_installed = False

    if all_installed:
        print(f"\n{Colors.GREEN}All required packages are installed{Colors.RESET}")
    else:
        print(
            f"\n{Colors.RED}Some packages are missing. Run: "
            f"python -m pip install --require-hashes -r {requirements_path.name}{Colors.RESET}"
        )

    return all_installed


def check_project_structure(create_cache_dirs: bool = False) -> bool:
    """Check if project structure is correct."""
    print_section("3. Project Structure Check")

    project_root = Path(__file__).parent

    if create_cache_dirs:
        print("Ensuring generated cache directories:")
        for dir_path in GENERATED_CACHE_DIRS:
            full_path = project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print_success(f"{dir_path:40s}")
    else:
        print("Checking generated cache directories without creating them:")
        for dir_path in GENERATED_CACHE_DIRS:
            full_path = project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                print_success(f"{dir_path:40s}")
            else:
                print_warning(f"{dir_path:40s} MISSING (generated; use --create-cache-dirs)")

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
        'papers',
        'thesis',
        'results',
    ]
    optional_dirs = [
        'docs/references',
        'data/test_cases',
        'agent_workflow',
    ]

    required_files = [
        'README.md',
        'requirements.txt',
        'requirements.lock',
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

    if optional_dirs:
        print("\nChecking optional directories:")
        for dir_path in optional_dirs:
            full_path = project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                print_success(f"{dir_path:40s}")
            else:
                print_warning(f"{dir_path:40s} MISSING (optional)")

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


def check_tests(full: bool = False) -> bool:
    """Check if the supported test suite can run."""
    print_section("5. Test Suite Check")

    project_root = Path(__file__).parent
    tests_dir = project_root / 'tests'

    if not tests_dir.exists():
        print_error("Tests directory not found")
        return False

    try:
        if full:
            command = [sys.executable, '-m', 'pytest', 'tests', '-q', '-o', 'addopts=']
            timeout = FULL_TEST_TIMEOUT_SECONDS
            label = "full test suite"
        else:
            command = [
                sys.executable, '-m', 'pytest', 'tests', '-q',
                '-m', 'not slow and not external and not cache_building',
            ]
            timeout = FAST_TEST_TIMEOUT_SECONDS
            label = "fast supported test profile"

        print(f"Running {label}: {' '.join(command)} (timeout: {timeout}s)")
        result = subprocess.run(
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            print_success(f"{label.capitalize()} passed")
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'passed' in line.lower() or 'collected' in line.lower():
                    print(f"  {line}")
            return True
        else:
            print_error("The supported test command failed")
            print("\nTest output:")
            print(result.stdout)
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_error(f"Test profile timed out after {timeout}s")
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
            timeout=DEMO_TIMEOUT_SECONDS
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


def check_notebooks() -> bool:
    """Run the lightweight notebook source smoke check."""
    print_section("8. Notebook Smoke Check")

    project_root = Path(__file__).parent
    command = [sys.executable, "scripts/verify_notebooks.py"]
    try:
        result = subprocess.run(
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=NOTEBOOK_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print_error(f"Notebook smoke check timed out after {NOTEBOOK_TIMEOUT_SECONDS}s")
        return False

    if result.returncode == 0:
        print_success("Notebook smoke check passed")
        print(result.stdout.strip())
        return True

    print_error("Notebook smoke check failed")
    print(result.stdout)
    print(result.stderr)
    return False


def check_thesis_artifact_build() -> bool:
    """Run thesis workflow validation and automatic thesis build."""
    print_section("9. Thesis Artifact Check")

    project_root = Path(__file__).parent
    commands = [
        [sys.executable, 'scripts/thesis_workflow.py', 'validate'],
        [sys.executable, 'scripts/thesis_workflow.py', 'build', '--mode', 'auto'],
    ]

    for command in commands:
        print(f"Running: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=THESIS_ARTIFACT_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            print_error(f"Command timed out after {THESIS_ARTIFACT_TIMEOUT_SECONDS}s: {' '.join(command)}")
            return False

        if result.returncode != 0:
            print_error(f"Command failed: {' '.join(command)}")
            print(result.stdout)
            print(result.stderr)
            return False

    print_success("Thesis validation/build commands passed")
    return True


def check_webapp_artifacts() -> bool:
    """Run preview webapp tests and production build."""
    print_section("10. Webapp Artifact Check")

    project_root = Path(__file__).parent
    webapp_dir = project_root / 'webapp'
    if not webapp_dir.exists():
        print_warning("webapp directory not found; skipping")
        return True
    if not (webapp_dir / 'node_modules').exists():
        print_error("webapp/node_modules is absent. Run `cd webapp && npm ci` before --all-artifacts.")
        return False

    for command in (['npm', 'test'], ['npm', 'run', 'build']):
        print(f"Running: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                cwd=str(webapp_dir),
                capture_output=True,
                text=True,
                timeout=WEBAPP_ARTIFACT_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            print_error(f"Command timed out after {WEBAPP_ARTIFACT_TIMEOUT_SECONDS}s: {' '.join(command)}")
            return False

        if result.returncode != 0:
            print_error(f"Command failed: {' '.join(command)}")
            print(result.stdout)
            print(result.stderr)
            return False

    print_success("Webapp test/build commands passed")
    return True


def main():
    """Run all verification checks."""
    parser = argparse.ArgumentParser(description="Verify the Rubik's Cube thesis checkout.")
    parser.add_argument(
        "--full",
        action="store_true",
        help="run the full pytest suite, including slow/cache-building tests",
    )
    parser.add_argument(
        "--create-cache-dirs",
        action="store_true",
        help="create generated cache directories instead of only checking their presence",
    )
    parser.add_argument(
        "--requirements",
        default="requirements.lock",
        help="requirements file to verify; defaults to the pinned requirements.lock",
    )
    parser.add_argument(
        "--notebooks",
        action="store_true",
        help="also run the lightweight notebook JSON/metadata smoke check",
    )
    parser.add_argument(
        "--all-artifacts",
        action="store_true",
        help="also verify thesis artifact build and preview webapp test/build; requires local TeX/Docker and webapp dependencies",
    )
    args = parser.parse_args()
    project_root = Path(__file__).parent
    requirements_path = Path(args.requirements)
    if not requirements_path.is_absolute():
        requirements_path = project_root / requirements_path

    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Rubik's Cube Thesis - Setup Verification{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.RESET}")

    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", lambda: check_required_packages(requirements_path)),
        ("Project Structure", lambda: check_project_structure(create_cache_dirs=args.create_cache_dirs)),
        ("Core Functionality", check_core_functionality),
        ("Test Suite", lambda: check_tests(full=args.full)),
        ("Demo Script", check_demo),
        ("Documentation", check_documentation),
    ]
    if args.notebooks:
        checks.append(("Notebook Smoke", check_notebooks))
    if args.all_artifacts:
        checks.extend(
            [
                ("Thesis Artifact", check_thesis_artifact_build),
                ("Webapp Artifact", check_webapp_artifacts),
            ]
        )

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
        if args.all_artifacts:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Full repository artifact verification passed.{Colors.RESET}")
        else:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✓ Python-only setup profile passed.{Colors.RESET}\n"
                f"{Colors.YELLOW}{Colors.BOLD}⚠ Thesis PDF and webapp artifact builds were not checked. "
                f"Run --all-artifacts when local TeX/Docker and webapp dependencies are available.{Colors.RESET}"
            )
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed. Please review the output above.{Colors.RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
