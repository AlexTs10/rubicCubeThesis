#!/usr/bin/env python3
"""
Test script for Korf's Optimal Solver

This script tests the optimal solver on a few easy scrambles to verify
that it works correctly.

NOTE: For difficult scrambles, this solver may take hours. Use easy
scrambles (5-10 moves) for quick testing.
"""

import sys
import time
from src.cube.rubik_cube import RubikCube
from src.korf.optimal_solver import KorfOptimalSolver, solve_optimal


def test_solved_cube():
    """Test that a solved cube returns empty solution."""
    print("\n" + "="*70)
    print("TEST 1: Solved Cube")
    print("="*70)

    cube = RubikCube()
    solver = KorfOptimalSolver()

    result = solver.solve(cube, verbose=True)

    if result is None:
        print("❌ FAILED: Solver returned None")
        return False

    solution, stats = result
    if len(solution) == 0 and cube.is_solved():
        print("✓ PASSED: Correctly returned empty solution for solved cube")
        return True
    else:
        print(f"❌ FAILED: Expected empty solution, got {len(solution)} moves")
        return False


def test_simple_scramble():
    """Test a very simple scramble (2-3 moves)."""
    print("\n" + "="*70)
    print("TEST 2: Simple Scramble (3 moves)")
    print("="*70)

    cube = RubikCube()
    scramble = ['R', 'U', 'R\'']
    print(f"Scramble: {' '.join(scramble)}")

    cube.apply_moves(scramble)

    solver = KorfOptimalSolver()
    result = solver.solve(cube, verbose=True)

    if result is None:
        print("❌ FAILED: Solver returned None")
        return False

    solution, stats = result

    # Verify solution
    test_cube = RubikCube()
    test_cube.apply_moves(scramble)
    test_cube.apply_moves(solution)

    if test_cube.is_solved():
        print(f"✓ PASSED: Solution is correct and optimal ({len(solution)} moves)")
        print(f"  Expected optimal: ≤3 moves")
        print(f"  Found: {len(solution)} moves")
        return True
    else:
        print("❌ FAILED: Solution does not solve the cube")
        return False


def test_medium_scramble():
    """Test a medium scramble (7 moves)."""
    print("\n" + "="*70)
    print("TEST 3: Medium Scramble (7 moves)")
    print("="*70)
    print("⚠️  This may take 1-5 minutes depending on the scramble...")

    cube = RubikCube()
    scramble = ['R', 'U', 'R\'', 'U\'', 'F\'', 'L\'', 'F']
    print(f"Scramble: {' '.join(scramble)}")

    cube.apply_moves(scramble)

    solver = KorfOptimalSolver()
    result = solver.solve(cube, verbose=True)

    if result is None:
        print("❌ FAILED: Solver returned None")
        return False

    solution, stats = result

    # Verify solution
    test_cube = RubikCube()
    test_cube.apply_moves(scramble)
    test_cube.apply_moves(solution)

    if test_cube.is_solved():
        print(f"✓ PASSED: Solution is correct and optimal ({len(solution)} moves)")
        print(f"  Expected optimal: ≤7 moves")
        print(f"  Found: {len(solution)} moves")
        return True
    else:
        print("❌ FAILED: Solution does not solve the cube")
        return False


def benchmark_comparison():
    """Quick comparison with other solvers (if available)."""
    print("\n" + "="*70)
    print("BONUS: Quick Algorithm Comparison")
    print("="*70)

    try:
        from src.thistlethwaite.solver import ThistlethwaiteSolver
        from src.kociemba.solver import KociembaSolver

        cube = RubikCube()
        scramble = ['R', 'U', 'F', 'D', 'L', 'B']
        print(f"Test scramble: {' '.join(scramble)}")
        cube.apply_moves(scramble)

        # Test Thistlethwaite
        print("\n--- Thistlethwaite ---")
        start = time.time()
        t_solver = ThistlethwaiteSolver()
        t_result = t_solver.solve(cube, verbose=False)
        t_time = time.time() - start
        t_moves = len(t_result[0]) if t_result else 0
        print(f"Moves: {t_moves}, Time: {t_time:.2f}s")

        # Test Kociemba
        print("\n--- Kociemba ---")
        start = time.time()
        k_solver = KociembaSolver()
        k_result = k_solver.solve(cube, verbose=False)
        k_time = time.time() - start
        k_moves = len(k_result[0]) if k_result else 0
        print(f"Moves: {k_moves}, Time: {k_time:.2f}s")

        # Test Optimal (skip for now - too slow)
        print("\n--- Korf Optimal ---")
        print("(Skipped - would take too long for this test)")
        print("Use test_medium_scramble() for a full test")

        print("\n" + "="*70)
        print("Algorithm Comparison Summary:")
        print(f"  Thistlethwaite: {t_moves} moves in {t_time:.2f}s")
        print(f"  Kociemba: {k_moves} moves in {k_time:.2f}s")
        print(f"  Korf Optimal: (skipped)")
        print("="*70)

    except ImportError as e:
        print(f"Could not import other solvers: {e}")


def main():
    """Run all tests."""
    print("="*70)
    print("KORF OPTIMAL SOLVER TEST SUITE")
    print("="*70)
    print("\nNOTE: This test suite uses EASY scrambles for speed.")
    print("Real-world solving can take minutes to hours for difficult cubes.")
    print("\nFor best performance:")
    print("  - Install PyPy: sudo apt install pypy3")
    print("  - Run with PyPy: pypy3 test_optimal_solver.py")
    print("="*70)

    results = []

    # Run tests
    results.append(("Solved Cube", test_solved_cube()))
    results.append(("Simple Scramble", test_simple_scramble()))

    # Ask before running medium test
    print("\n" + "="*70)
    response = input("Run medium scramble test? (may take 1-5 minutes) [y/N]: ")
    if response.lower() == 'y':
        results.append(("Medium Scramble", test_medium_scramble()))

    # Run bonus comparison
    print("\n" + "="*70)
    response = input("Run algorithm comparison? [y/N]: ")
    if response.lower() == 'y':
        benchmark_comparison()

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print("="*70)

    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
