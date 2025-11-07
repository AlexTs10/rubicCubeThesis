"""
Unified Algorithm Comparison Framework - Phase 8

This module provides a comprehensive framework for comparing all three
implemented Rubik's Cube solving algorithms:
- Thistlethwaite (1981): 4-phase group-theoretic approach
- Kociemba (1992): 2-phase near-optimal solver
- Korf (1997): IDA* with pattern databases (optimal)

The framework runs identical scrambles through all algorithms and collects
standardized metrics for statistical analysis and thesis presentation.

Key Features:
- Standardized test methodology
- Comprehensive metric collection
- Statistical analysis
- Export to JSON/CSV/LaTeX
- Progress tracking for large test runs

References:
- cube20.org: God's Number validation data
- The-Semicolons/AnalysisofRubiksCubeSolvingAlgorithm: Comparison methodology
"""

import time
import psutil
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import json
from datetime import datetime

from ..cube.rubik_cube import RubikCube
from ..thistlethwaite import ThistlethwaiteSolver
from ..kociemba.solver import KociembaSolver
from ..kociemba.cubie import CubieCube, from_facelet_cube, to_facelet_cube
from ..korf.a_star import IDAStarSolver
from ..korf.composite_heuristic import create_heuristic


@dataclass
class AlgorithmResult:
    """Results from a single algorithm on a single scramble."""
    algorithm: str
    scramble_depth: int
    solved: bool
    solution_length: Optional[int]
    time_seconds: float
    memory_mb: float
    nodes_explored: Optional[int] = None
    reason_failed: Optional[str] = None
    solution_moves: Optional[List[str]] = None


@dataclass
class ComparisonResult:
    """Complete comparison results for all algorithms on one scramble."""
    scramble_id: int
    scramble_depth: int
    scramble_moves: List[str]
    timestamp: str
    thistlethwaite: AlgorithmResult
    kociemba: AlgorithmResult
    korf: AlgorithmResult


@dataclass
class ComparisonSummary:
    """Summary statistics for an algorithm across multiple scrambles."""
    algorithm: str
    total_tests: int
    successful_solves: int
    success_rate: float

    # Solution quality
    avg_solution_length: float
    min_solution_length: int
    max_solution_length: int
    std_solution_length: float

    # Performance
    avg_time_seconds: float
    min_time_seconds: float
    max_time_seconds: float

    # Memory
    avg_memory_mb: float
    max_memory_mb: float

    # Additional metrics
    total_nodes_explored: Optional[int] = None
    avg_nodes_explored: Optional[float] = None


class AlgorithmComparison:
    """
    Framework for comparing Thistlethwaite, Kociemba, and Korf algorithms.

    Runs standardized tests across multiple scrambles and collects metrics
    for statistical analysis and thesis presentation.

    Usage:
        comparison = AlgorithmComparison()
        results = comparison.run_batch_test(n_scrambles=100)
        summary = comparison.generate_summary()
        comparison.export_results('results.json')
    """

    def __init__(
        self,
        thistlethwaite_timeout: float = 30.0,
        kociemba_timeout: float = 60.0,
        korf_timeout: float = 120.0,
        korf_max_depth: int = 20
    ):
        """
        Initialize comparison framework.

        Args:
            thistlethwaite_timeout: Max time for Thistlethwaite (seconds)
            kociemba_timeout: Max time for Kociemba (seconds)
            korf_timeout: Max time for Korf IDA* (seconds)
            korf_max_depth: Maximum search depth for Korf
        """
        self.thistlethwaite_timeout = thistlethwaite_timeout
        self.kociemba_timeout = kociemba_timeout
        self.korf_timeout = korf_timeout
        self.korf_max_depth = korf_max_depth

        self.results: List[ComparisonResult] = []
        self.process = psutil.Process(os.getpid())

        # Initialize solvers
        print("Initializing solvers...")
        self.thistlethwaite_solver = ThistlethwaiteSolver(use_pattern_databases=False)
        print("  ✓ Thistlethwaite solver ready")

        self.kociemba_solver = KociembaSolver()
        print("  ✓ Kociemba solver ready")

        # Korf uses composite heuristic
        korf_heuristic = create_heuristic('composite')
        self.korf_solver = IDAStarSolver(
            heuristic=korf_heuristic,
            max_depth=korf_max_depth,
            timeout=korf_timeout
        )
        print("  ✓ Korf IDA* solver ready")
        print()

    def compare_on_scramble(self, cube: RubikCube, scramble_id: int = 0) -> ComparisonResult:
        """
        Run all three algorithms on the same scrambled cube.

        Args:
            cube: Scrambled RubikCube to solve
            scramble_id: Identifier for this scramble

        Returns:
            ComparisonResult with all metrics
        """
        # Get scramble info
        scramble_depth = getattr(cube, '_scramble_depth', 0)
        scramble_moves = getattr(cube, '_scramble_moves', [])

        timestamp = datetime.now().isoformat()

        # Test each algorithm
        print(f"  Testing scramble #{scramble_id} (depth {scramble_depth})...")

        # 1. Thistlethwaite
        print("    - Thistlethwaite: ", end='', flush=True)
        thistle_result = self._test_thistlethwaite(cube.copy(), scramble_depth)
        print("✓" if thistle_result.solved else "✗")

        # 2. Kociemba
        print("    - Kociemba:       ", end='', flush=True)
        kociemba_result = self._test_kociemba(cube.copy(), scramble_depth)
        print("✓" if kociemba_result.solved else "✗")

        # 3. Korf IDA*
        print("    - Korf IDA*:      ", end='', flush=True)
        korf_result = self._test_korf(cube.copy(), scramble_depth)
        print("✓" if korf_result.solved else "✗")

        return ComparisonResult(
            scramble_id=scramble_id,
            scramble_depth=scramble_depth,
            scramble_moves=scramble_moves,
            timestamp=timestamp,
            thistlethwaite=thistle_result,
            kociemba=kociemba_result,
            korf=korf_result
        )

    def _test_thistlethwaite(self, cube: RubikCube, scramble_depth: int) -> AlgorithmResult:
        """Test Thistlethwaite algorithm."""
        mem_before = self.process.memory_info().rss / 1024 / 1024

        start_time = time.time()
        try:
            result = self.thistlethwaite_solver.solve(cube, verbose=False)
            elapsed = time.time() - start_time

            if result is None:
                return AlgorithmResult(
                    algorithm="Thistlethwaite",
                    scramble_depth=scramble_depth,
                    solved=False,
                    solution_length=None,
                    time_seconds=elapsed,
                    memory_mb=0.0,
                    reason_failed="no_solution"
                )

            all_moves, phase_moves = result

            # Verify solution
            test_cube = cube.copy()
            for move in all_moves:
                test_cube.apply_move(move)
            is_solved = test_cube.is_solved()

            mem_after = self.process.memory_info().rss / 1024 / 1024

            return AlgorithmResult(
                algorithm="Thistlethwaite",
                scramble_depth=scramble_depth,
                solved=is_solved,
                solution_length=len(all_moves),
                time_seconds=elapsed,
                memory_mb=mem_after - mem_before,
                solution_moves=all_moves if is_solved else None
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return AlgorithmResult(
                algorithm="Thistlethwaite",
                scramble_depth=scramble_depth,
                solved=False,
                solution_length=None,
                time_seconds=elapsed,
                memory_mb=0.0,
                reason_failed=f"error: {str(e)}"
            )

    def _test_kociemba(self, cube: RubikCube, scramble_depth: int) -> AlgorithmResult:
        """Test Kociemba algorithm."""
        mem_before = self.process.memory_info().rss / 1024 / 1024

        start_time = time.time()
        try:
            # Convert to CubieCube
            cubie = from_facelet_cube(cube)

            # Solve
            solution = self.kociemba_solver.solve(
                cubie,
                max_depth=25,
                timeout=self.kociemba_timeout
            )
            elapsed = time.time() - start_time

            if solution is None:
                return AlgorithmResult(
                    algorithm="Kociemba",
                    scramble_depth=scramble_depth,
                    solved=False,
                    solution_length=None,
                    time_seconds=elapsed,
                    memory_mb=0.0,
                    reason_failed="no_solution"
                )

            # Verify solution
            test_cube = cube.copy()
            for move in solution:
                test_cube.apply_move(move)
            is_solved = test_cube.is_solved()

            mem_after = self.process.memory_info().rss / 1024 / 1024

            return AlgorithmResult(
                algorithm="Kociemba",
                scramble_depth=scramble_depth,
                solved=is_solved,
                solution_length=len(solution),
                time_seconds=elapsed,
                memory_mb=mem_after - mem_before,
                solution_moves=solution if is_solved else None
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return AlgorithmResult(
                algorithm="Kociemba",
                scramble_depth=scramble_depth,
                solved=False,
                solution_length=None,
                time_seconds=elapsed,
                memory_mb=0.0,
                reason_failed=f"error: {str(e)}"
            )

    def _test_korf(self, cube: RubikCube, scramble_depth: int) -> AlgorithmResult:
        """Test Korf IDA* algorithm."""
        mem_before = self.process.memory_info().rss / 1024 / 1024

        start_time = time.time()
        try:
            solution = self.korf_solver.solve(cube)
            elapsed = time.time() - start_time

            stats = self.korf_solver.get_statistics()

            if solution is None:
                reason = "timeout" if elapsed >= self.korf_timeout - 0.1 else "no_solution"
                return AlgorithmResult(
                    algorithm="Korf_IDA*",
                    scramble_depth=scramble_depth,
                    solved=False,
                    solution_length=None,
                    time_seconds=elapsed,
                    memory_mb=0.0,
                    nodes_explored=stats.get('nodes_explored', 0),
                    reason_failed=reason
                )

            # Verify solution
            test_cube = cube.copy()
            for move in solution:
                test_cube.apply_move(move)
            is_solved = test_cube.is_solved()

            mem_after = self.process.memory_info().rss / 1024 / 1024

            return AlgorithmResult(
                algorithm="Korf_IDA*",
                scramble_depth=scramble_depth,
                solved=is_solved,
                solution_length=len(solution),
                time_seconds=elapsed,
                memory_mb=mem_after - mem_before,
                nodes_explored=stats.get('nodes_explored', 0),
                solution_moves=solution if is_solved else None
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return AlgorithmResult(
                algorithm="Korf_IDA*",
                scramble_depth=scramble_depth,
                solved=False,
                solution_length=None,
                time_seconds=elapsed,
                memory_mb=0.0,
                reason_failed=f"error: {str(e)}"
            )

    def run_batch_test(
        self,
        n_scrambles: int = 10,
        scramble_depth: int = 10,
        seed: Optional[int] = None
    ) -> List[ComparisonResult]:
        """
        Run all algorithms on N scrambles.

        Args:
            n_scrambles: Number of scrambles to test
            scramble_depth: Number of moves per scramble
            seed: Random seed for reproducibility

        Returns:
            List of ComparisonResults
        """
        print("=" * 70)
        print(f"BATCH COMPARISON TEST")
        print("=" * 70)
        print(f"Scrambles:       {n_scrambles}")
        print(f"Scramble depth:  {scramble_depth}")
        print(f"Random seed:     {seed}")
        print("=" * 70)
        print()

        for i in range(n_scrambles):
            # Generate scramble
            cube = RubikCube()
            scramble = cube.scramble(moves=scramble_depth, seed=seed + i if seed else None)

            # Store scramble info
            cube._scramble_depth = scramble_depth
            cube._scramble_moves = scramble

            # Run comparison
            result = self.compare_on_scramble(cube, scramble_id=i)
            self.results.append(result)

            print()

        print("=" * 70)
        print(f"Batch test complete: {n_scrambles} scrambles tested")
        print("=" * 70)
        print()

        return self.results

    def generate_summary(self) -> Dict[str, ComparisonSummary]:
        """
        Generate summary statistics from collected results.

        Returns:
            Dictionary mapping algorithm name to summary statistics
        """
        if not self.results:
            print("No results to summarize. Run tests first.")
            return {}

        # Collect results by algorithm
        algo_results = {
            'Thistlethwaite': [],
            'Kociemba': [],
            'Korf_IDA*': []
        }

        for comp_result in self.results:
            algo_results['Thistlethwaite'].append(comp_result.thistlethwaite)
            algo_results['Kociemba'].append(comp_result.kociemba)
            algo_results['Korf_IDA*'].append(comp_result.korf)

        # Compute summaries
        summaries = {}
        for algo_name, results in algo_results.items():
            summaries[algo_name] = self._compute_algorithm_summary(algo_name, results)

        return summaries

    def _compute_algorithm_summary(
        self,
        algorithm: str,
        results: List[AlgorithmResult]
    ) -> ComparisonSummary:
        """Compute summary statistics for one algorithm."""
        total_tests = len(results)
        successful = [r for r in results if r.solved]
        successful_solves = len(successful)

        if successful_solves == 0:
            return ComparisonSummary(
                algorithm=algorithm,
                total_tests=total_tests,
                successful_solves=0,
                success_rate=0.0,
                avg_solution_length=0.0,
                min_solution_length=0,
                max_solution_length=0,
                std_solution_length=0.0,
                avg_time_seconds=0.0,
                min_time_seconds=0.0,
                max_time_seconds=0.0,
                avg_memory_mb=0.0,
                max_memory_mb=0.0
            )

        # Solution lengths
        lengths = [r.solution_length for r in successful]
        avg_length = sum(lengths) / len(lengths)
        std_length = (sum((x - avg_length) ** 2 for x in lengths) / len(lengths)) ** 0.5

        # Times
        times = [r.time_seconds for r in successful]

        # Memory
        memories = [r.memory_mb for r in successful]

        # Nodes (if available)
        nodes_list = [r.nodes_explored for r in successful if r.nodes_explored is not None]
        total_nodes = sum(nodes_list) if nodes_list else None
        avg_nodes = sum(nodes_list) / len(nodes_list) if nodes_list else None

        return ComparisonSummary(
            algorithm=algorithm,
            total_tests=total_tests,
            successful_solves=successful_solves,
            success_rate=successful_solves / total_tests,
            avg_solution_length=avg_length,
            min_solution_length=min(lengths),
            max_solution_length=max(lengths),
            std_solution_length=std_length,
            avg_time_seconds=sum(times) / len(times),
            min_time_seconds=min(times),
            max_time_seconds=max(times),
            avg_memory_mb=sum(memories) / len(memories),
            max_memory_mb=max(memories),
            total_nodes_explored=total_nodes,
            avg_nodes_explored=avg_nodes
        )

    def print_summary(self, summaries: Optional[Dict[str, ComparisonSummary]] = None) -> None:
        """Print summary statistics in readable format."""
        if summaries is None:
            summaries = self.generate_summary()

        print("\n")
        print("=" * 70)
        print("ALGORITHM COMPARISON SUMMARY")
        print("=" * 70)

        for algo_name, summary in summaries.items():
            print(f"\n{algo_name}:")
            print(f"  Success rate:         {summary.success_rate * 100:.1f}% ({summary.successful_solves}/{summary.total_tests})")

            if summary.successful_solves > 0:
                print(f"  Avg solution length:  {summary.avg_solution_length:.1f} moves (min={summary.min_solution_length}, max={summary.max_solution_length})")
                print(f"  Std deviation:        {summary.std_solution_length:.2f} moves")
                print(f"  Avg time:             {summary.avg_time_seconds:.3f}s (min={summary.min_time_seconds:.3f}s, max={summary.max_time_seconds:.3f}s)")
                print(f"  Avg memory:           {summary.avg_memory_mb:.2f} MB (max={summary.max_memory_mb:.2f} MB)")

                if summary.avg_nodes_explored is not None:
                    print(f"  Avg nodes explored:   {summary.avg_nodes_explored:,.0f}")

        print("\n" + "=" * 70)

    def export_results(self, filename: str) -> None:
        """
        Export results to JSON file.

        Args:
            filename: Output filename
        """
        data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_scrambles': len(self.results),
                'thistlethwaite_timeout': self.thistlethwaite_timeout,
                'kociemba_timeout': self.kociemba_timeout,
                'korf_timeout': self.korf_timeout,
                'korf_max_depth': self.korf_max_depth
            },
            'results': [asdict(r) for r in self.results]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Results exported to: {filename}")

    def export_summary_table(self, filename: str, format: str = 'markdown') -> None:
        """
        Export summary table in specified format.

        Args:
            filename: Output filename
            format: 'markdown' or 'latex'
        """
        summaries = self.generate_summary()

        if format == 'markdown':
            self._export_markdown_table(filename, summaries)
        elif format == 'latex':
            self._export_latex_table(filename, summaries)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _export_markdown_table(self, filename: str, summaries: Dict[str, ComparisonSummary]) -> None:
        """Export summary as Markdown table."""
        lines = [
            "# Algorithm Comparison Summary\n",
            "| Algorithm | Success Rate | Avg Moves | Std Dev | Avg Time (s) | Avg Memory (MB) |",
            "|-----------|--------------|-----------|---------|--------------|-----------------|"
        ]

        for algo_name, summary in summaries.items():
            if summary.successful_solves > 0:
                lines.append(
                    f"| {algo_name} | {summary.success_rate*100:.1f}% | "
                    f"{summary.avg_solution_length:.1f} | {summary.std_solution_length:.2f} | "
                    f"{summary.avg_time_seconds:.3f} | {summary.avg_memory_mb:.2f} |"
                )
            else:
                lines.append(f"| {algo_name} | 0.0% | - | - | - | - |")

        with open(filename, 'w') as f:
            f.write('\n'.join(lines))

        print(f"\n✓ Markdown table exported to: {filename}")

    def _export_latex_table(self, filename: str, summaries: Dict[str, ComparisonSummary]) -> None:
        """Export summary as LaTeX table."""
        lines = [
            "\\begin{table}[h]",
            "\\centering",
            "\\begin{tabular}{|l|c|c|c|c|c|}",
            "\\hline",
            "Algorithm & Success Rate & Avg Moves & Std Dev & Avg Time (s) & Avg Memory (MB) \\\\",
            "\\hline"
        ]

        for algo_name, summary in summaries.items():
            if summary.successful_solves > 0:
                lines.append(
                    f"{algo_name.replace('_', ' ')} & {summary.success_rate*100:.1f}\\% & "
                    f"{summary.avg_solution_length:.1f} & {summary.std_solution_length:.2f} & "
                    f"{summary.avg_time_seconds:.3f} & {summary.avg_memory_mb:.2f} \\\\"
                )
            else:
                lines.append(f"{algo_name.replace('_', ' ')} & 0.0\\% & - & - & - & - \\\\")

        lines.extend([
            "\\hline",
            "\\end{tabular}",
            "\\caption{Algorithm Performance Comparison}",
            "\\label{tab:algorithm-comparison}",
            "\\end{table}"
        ])

        with open(filename, 'w') as f:
            f.write('\n'.join(lines))

        print(f"\n✓ LaTeX table exported to: {filename}")


def run_quick_test():
    """Run a quick 10-scramble test for validation."""
    comparison = AlgorithmComparison()

    # Run test
    results = comparison.run_batch_test(
        n_scrambles=10,
        scramble_depth=7,
        seed=42
    )

    # Print summary
    summaries = comparison.generate_summary()
    comparison.print_summary(summaries)

    # Export results
    comparison.export_results('quick_comparison_results.json')
    comparison.export_summary_table('quick_comparison_summary.md', format='markdown')


if __name__ == '__main__':
    run_quick_test()
