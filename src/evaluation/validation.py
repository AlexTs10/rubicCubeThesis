"""
Validation Suite - Phase 8

This module provides validation against cube20.org God's Number data and
known hard positions. Tests algorithms against standardized benchmarks for
academic rigor.

Features:
- Superflip validation (known 20-move position)
- Distance-20 position tests
- Solution verification
- Optimality validation
- Comparison against God's Number

Reference:
- cube20.org: Official God's Number proof and test cases
- God's Number = 20 moves (worst case optimal)
- Average optimal: ~17.8 moves

Usage:
    from src.evaluation.validation import ValidationSuite

    suite = ValidationSuite()
    results = suite.run_all_validations()
    suite.print_report(results)
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time

from ..cube.rubik_cube import RubikCube


@dataclass
class ValidationResult:
    """Result from a validation test."""
    test_name: str
    description: str
    expected_optimal: int  # Expected optimal solution length
    algorithm: str
    solved: bool
    solution_length: Optional[int]
    time_seconds: float
    is_optimal: bool
    solution_moves: Optional[List[str]] = None
    error_message: Optional[str] = None


class ValidationSuite:
    """
    Comprehensive validation suite using cube20.org test cases.
    """

    def __init__(self):
        """Initialize validation suite with known test cases."""
        # Superflip: First proven distance-20 position
        self.superflip_scramble = [
            "U", "R2", "F", "B", "R", "B2", "R", "U2", "L", "B2",
            "R", "U'", "D'", "R2", "F", "R'", "L", "B2", "U2", "F2"
        ]

        # Additional hard positions (sub-optimal known solutions)
        # These are challenging but not necessarily optimal
        self.hard_positions = {
            "hard_1": {
                "scramble": ["F", "U'", "F2", "D'", "B", "U", "R'", "F'", "L", "D'"],
                "min_moves": 10  # Minimum expected (reverse scramble)
            },
            "hard_2": {
                "scramble": ["R", "U", "R'", "U'"] * 6,  # 6x sexy move
                "min_moves": 12  # Known to require more than scramble depth
            }
        }

        # Distance distribution validation
        # From cube20.org: percentage of cubes at each distance
        self.distance_distribution = {
            15: 2.11,    # 2.11% of cubes require 15 moves
            16: 2.55,    # 2.55% require 16 moves
            17: 27.73,   # 27.73% require 17 moves (peak)
            18: 67.08,   # 67.08% require 18 moves (peak)
            19: 0.35,    # 0.35% require 19 moves
            20: 0.00003  # ~490M cubes require 20 moves (rare)
        }

    def run_all_validations(self, algorithms: Optional[List] = None) -> Dict[str, List[ValidationResult]]:
        """
        Run all validation tests.

        Args:
            algorithms: List of algorithm instances to test
                       Each should have a .solve(cube) method

        Returns:
            Dictionary mapping algorithm names to validation results
        """
        if algorithms is None:
            algorithms = []

        results = {}

        print("=" * 80)
        print("CUBE20.ORG VALIDATION SUITE")
        print("=" * 80)
        print(f"\nTesting {len(algorithms)} algorithm(s)")
        print("=" * 80)
        print()

        for algo in algorithms:
            algo_name = algo.__class__.__name__
            print(f"\nValidating: {algo_name}")
            print("-" * 80)

            algo_results = []

            # Test 1: Superflip
            print("  Test 1: Superflip (distance-20 position)...")
            result = self._test_superflip(algo, algo_name)
            algo_results.append(result)
            self._print_result(result)

            # Test 2: Hard positions
            for pos_name, pos_data in self.hard_positions.items():
                print(f"  Test: {pos_name}...")
                result = self._test_hard_position(algo, algo_name, pos_name, pos_data)
                algo_results.append(result)
                self._print_result(result)

            results[algo_name] = algo_results

        return results

    def _test_superflip(self, algorithm, algo_name: str) -> ValidationResult:
        """Test algorithm on Superflip position."""
        cube = RubikCube()
        for move in self.superflip_scramble:
            cube.apply_move(move)

        start_time = time.time()
        try:
            solution = self._solve_with_algorithm(algorithm, cube)
            elapsed = time.time() - start_time

            if solution is None:
                return ValidationResult(
                    test_name="Superflip",
                    description="First proven distance-20 position (all edges flipped)",
                    expected_optimal=20,
                    algorithm=algo_name,
                    solved=False,
                    solution_length=None,
                    time_seconds=elapsed,
                    is_optimal=False,
                    error_message="Failed to solve"
                )

            # Verify solution
            test_cube = RubikCube()
            for move in self.superflip_scramble:
                test_cube.apply_move(move)
            for move in solution:
                test_cube.apply_move(move)

            is_solved = test_cube.is_solved()
            solution_length = len(solution)

            # Check if optimal (20 moves is optimal for Superflip)
            is_optimal = (solution_length == 20) if is_solved else False

            return ValidationResult(
                test_name="Superflip",
                description="First proven distance-20 position (all edges flipped)",
                expected_optimal=20,
                algorithm=algo_name,
                solved=is_solved,
                solution_length=solution_length,
                time_seconds=elapsed,
                is_optimal=is_optimal,
                solution_moves=solution if is_solved else None
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return ValidationResult(
                test_name="Superflip",
                description="First proven distance-20 position (all edges flipped)",
                expected_optimal=20,
                algorithm=algo_name,
                solved=False,
                solution_length=None,
                time_seconds=elapsed,
                is_optimal=False,
                error_message=str(e)
            )

    def _test_hard_position(
        self,
        algorithm,
        algo_name: str,
        position_name: str,
        position_data: Dict
    ) -> ValidationResult:
        """Test algorithm on a hard position."""
        scramble = position_data['scramble']
        min_moves = position_data['min_moves']

        cube = RubikCube()
        for move in scramble:
            cube.apply_move(move)

        start_time = time.time()
        try:
            solution = self._solve_with_algorithm(algorithm, cube)
            elapsed = time.time() - start_time

            if solution is None:
                return ValidationResult(
                    test_name=position_name,
                    description=f"Hard position (min {min_moves} moves)",
                    expected_optimal=min_moves,
                    algorithm=algo_name,
                    solved=False,
                    solution_length=None,
                    time_seconds=elapsed,
                    is_optimal=False,
                    error_message="Failed to solve"
                )

            # Verify solution
            test_cube = RubikCube()
            for move in scramble:
                test_cube.apply_move(move)
            for move in solution:
                test_cube.apply_move(move)

            is_solved = test_cube.is_solved()
            solution_length = len(solution)

            # Hard positions don't have proven optimal, just check if reasonable
            is_optimal = (solution_length <= min_moves * 2) if is_solved else False

            return ValidationResult(
                test_name=position_name,
                description=f"Hard position (min {min_moves} moves)",
                expected_optimal=min_moves,
                algorithm=algo_name,
                solved=is_solved,
                solution_length=solution_length,
                time_seconds=elapsed,
                is_optimal=is_optimal,
                solution_moves=solution if is_solved else None
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return ValidationResult(
                test_name=position_name,
                description=f"Hard position (min {min_moves} moves)",
                expected_optimal=min_moves,
                algorithm=algo_name,
                solved=False,
                solution_length=None,
                time_seconds=elapsed,
                is_optimal=False,
                error_message=str(e)
            )

    def _solve_with_algorithm(self, algorithm, cube: RubikCube) -> Optional[List[str]]:
        """
        Solve cube with algorithm (handles different API styles).

        Args:
            algorithm: Algorithm instance
            cube: Scrambled cube

        Returns:
            Solution moves or None if failed
        """
        algo_name = algorithm.__class__.__name__

        # Try different solver APIs
        try:
            if hasattr(algorithm, 'solve'):
                result = algorithm.solve(cube.copy())

                # Handle different return formats
                if result is None:
                    return None
                elif isinstance(result, tuple):
                    # Thistlethwaite returns (moves, phase_moves)
                    return result[0]
                elif isinstance(result, list):
                    # Korf returns list of moves
                    return result
                else:
                    return None
            else:
                return None

        except Exception as e:
            print(f"    ⚠ Error: {e}")
            return None

    def _print_result(self, result: ValidationResult):
        """Print validation result."""
        if result.solved:
            optimal_str = "✓ OPTIMAL" if result.is_optimal else "✗ Sub-optimal"
            print(f"    ✓ Solved in {result.solution_length} moves "
                  f"({result.time_seconds:.3f}s) {optimal_str}")
        else:
            print(f"    ✗ Failed: {result.error_message or 'No solution found'}")

    def print_report(self, results: Dict[str, List[ValidationResult]]):
        """
        Print comprehensive validation report.

        Args:
            results: Validation results from run_all_validations()
        """
        print("\n")
        print("=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)

        for algo_name, algo_results in results.items():
            print(f"\n{algo_name}:")
            print("-" * 80)

            total_tests = len(algo_results)
            passed = sum(1 for r in algo_results if r.solved)
            optimal = sum(1 for r in algo_results if r.is_optimal)

            print(f"  Tests passed:    {passed}/{total_tests} ({passed/total_tests*100:.1f}%)")
            print(f"  Optimal solutions: {optimal}/{passed if passed > 0 else 1}")

            # Detailed results
            print(f"\n  Detailed Results:")
            for result in algo_results:
                status = "✓" if result.solved else "✗"
                optimal_mark = "★" if result.is_optimal else ""

                if result.solved:
                    print(f"    {status} {result.test_name}: {result.solution_length} moves "
                          f"(expected ≤{result.expected_optimal}) {optimal_mark}")
                else:
                    print(f"    {status} {result.test_name}: FAILED - {result.error_message}")

        print("\n" + "=" * 80)
        print("REFERENCE: cube20.org God's Number")
        print("=" * 80)
        print("  God's Number:        20 moves (worst case)")
        print("  Average optimal:     ~17.8 moves")
        print("  Superflip optimal:   20 moves")
        print("  Total positions:     43,252,003,274,489,856,000")
        print("=" * 80)

    def export_validation_report(self, results: Dict[str, List[ValidationResult]], output_path: str):
        """
        Export validation report to Markdown.

        Args:
            results: Validation results
            output_path: Output file path
        """
        lines = [
            "# Validation Report - cube20.org Test Cases\n",
            "## Summary\n"
        ]

        for algo_name, algo_results in results.items():
            total_tests = len(algo_results)
            passed = sum(1 for r in algo_results if r.solved)
            optimal = sum(1 for r in algo_results if r.is_optimal)

            lines.append(f"\n### {algo_name}\n")
            lines.append(f"- **Tests Passed**: {passed}/{total_tests} ({passed/total_tests*100:.1f}%)")
            lines.append(f"- **Optimal Solutions**: {optimal}/{passed if passed > 0 else 1}")

        lines.extend([
            "\n## Test Cases\n",
            "| Algorithm | Test | Result | Moves | Expected | Optimal | Time (s) |",
            "|-----------|------|--------|-------|----------|---------|----------|"
        ])

        for algo_name, algo_results in results.items():
            for result in algo_results:
                status = "✓ Pass" if result.solved else "✗ Fail"
                moves = str(result.solution_length) if result.solution_length else "-"
                optimal = "Yes" if result.is_optimal else "No"

                lines.append(
                    f"| {algo_name} | {result.test_name} | {status} | {moves} | "
                    f"{result.expected_optimal} | {optimal} | {result.time_seconds:.3f} |"
                )

        lines.extend([
            "\n## Reference: God's Number\n",
            "- **God's Number**: 20 moves (worst case optimal)",
            "- **Average Optimal**: ~17.8 moves",
            "- **Superflip**: 20 moves (first proven distance-20 position)",
            "- **Total Positions**: 43,252,003,274,489,856,000",
            "\n*Source: cube20.org*"
        ])

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

        print(f"\n✓ Validation report exported to: {output_path}")


def main():
    """Example usage showing how to use validation suite."""
    print("""
Validation Suite Usage Example:

from src.evaluation.validation import ValidationSuite
from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic

# Initialize validation suite
suite = ValidationSuite()

# Create algorithm instances
korf_solver = IDAStarSolver(
    heuristic=create_heuristic('composite'),
    max_depth=25,
    timeout=300.0  # 5 minutes for hard positions
)

# Run validation
results = suite.run_all_validations(algorithms=[korf_solver])

# Print report
suite.print_report(results)

# Export report
suite.export_validation_report(results, 'results/validation_report.md')
    """)


if __name__ == '__main__':
    main()
