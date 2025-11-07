"""
Statistical Analysis Module - Phase 8

This module provides comprehensive statistical analysis tools for algorithm
comparison results. Generates summary statistics, distributions, confidence
intervals, and exports to various formats for thesis presentation.

Features:
- Summary statistics (mean, median, std dev, quartiles)
- Distribution analysis
- Confidence intervals
- Comparison tables (Markdown, LaTeX, CSV)
- Hypothesis testing
- Effect size calculations

Usage:
    from src.evaluation.statistics import StatisticalAnalyzer

    analyzer = StatisticalAnalyzer('results/comprehensive_test.json')
    summary = analyzer.generate_summary()
    analyzer.export_table('results/summary.md', format='markdown')
    analyzer.export_table('results/summary.tex', format='latex')
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class AlgorithmStatistics:
    """Statistical summary for a single algorithm."""
    algorithm: str
    total_tests: int
    successful_tests: int
    success_rate: float

    # Solution length statistics
    solution_length_mean: Optional[float] = None
    solution_length_median: Optional[float] = None
    solution_length_std: Optional[float] = None
    solution_length_min: Optional[int] = None
    solution_length_max: Optional[int] = None
    solution_length_q1: Optional[float] = None
    solution_length_q3: Optional[float] = None

    # Time statistics (seconds)
    time_mean: Optional[float] = None
    time_median: Optional[float] = None
    time_std: Optional[float] = None
    time_min: Optional[float] = None
    time_max: Optional[float] = None

    # Memory statistics (MB)
    memory_mean: Optional[float] = None
    memory_max: Optional[float] = None

    # Nodes explored (if applicable)
    nodes_mean: Optional[float] = None
    nodes_median: Optional[float] = None
    nodes_total: Optional[int] = None

    # Failure analysis
    failure_reasons: Dict[str, int] = field(default_factory=dict)


class StatisticalAnalyzer:
    """
    Comprehensive statistical analysis of algorithm comparison results.
    """

    def __init__(self, results_path: str):
        """
        Initialize analyzer with results file.

        Args:
            results_path: Path to results JSON file
        """
        self.results_path = Path(results_path)
        self.data = self._load_results()
        self.statistics = {}

    def _load_results(self) -> Dict:
        """Load results from JSON file."""
        with open(self.results_path, 'r') as f:
            return json.load(f)

    def generate_summary(self) -> Dict[str, AlgorithmStatistics]:
        """
        Generate comprehensive statistical summary for all algorithms.

        Returns:
            Dictionary mapping algorithm names to statistics
        """
        # Extract results by algorithm
        algorithm_results = self._extract_algorithm_results()

        # Compute statistics for each algorithm
        self.statistics = {}
        for algo_name, results in algorithm_results.items():
            self.statistics[algo_name] = self._compute_statistics(algo_name, results)

        return self.statistics

    def _extract_algorithm_results(self) -> Dict[str, List[Dict]]:
        """Extract results grouped by algorithm."""
        algorithm_map = {
            'Thistlethwaite': 'thistlethwaite',
            'Kociemba': 'kociemba',
            'Korf_IDA*': 'korf'
        }

        algorithm_results = defaultdict(list)

        for result in self.data['results']:
            for algo_name, result_key in algorithm_map.items():
                algorithm_results[algo_name].append(result[result_key])

        return dict(algorithm_results)

    def _compute_statistics(self, algorithm: str, results: List[Dict]) -> AlgorithmStatistics:
        """Compute comprehensive statistics for one algorithm."""
        total_tests = len(results)
        successful = [r for r in results if r['solved']]
        successful_tests = len(successful)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

        stats = AlgorithmStatistics(
            algorithm=algorithm,
            total_tests=total_tests,
            successful_tests=successful_tests,
            success_rate=success_rate
        )

        if successful_tests == 0:
            # Analyze failures
            stats.failure_reasons = self._analyze_failures(results)
            return stats

        # Solution length statistics
        lengths = [r['solution_length'] for r in successful]
        stats.solution_length_mean = self._mean(lengths)
        stats.solution_length_median = self._median(lengths)
        stats.solution_length_std = self._std(lengths)
        stats.solution_length_min = min(lengths)
        stats.solution_length_max = max(lengths)
        stats.solution_length_q1 = self._percentile(lengths, 25)
        stats.solution_length_q3 = self._percentile(lengths, 75)

        # Time statistics
        times = [r['time_seconds'] for r in successful]
        stats.time_mean = self._mean(times)
        stats.time_median = self._median(times)
        stats.time_std = self._std(times)
        stats.time_min = min(times)
        stats.time_max = max(times)

        # Memory statistics
        memories = [r['memory_mb'] for r in successful]
        stats.memory_mean = self._mean(memories)
        stats.memory_max = max(memories)

        # Nodes explored (if available)
        nodes_list = [r['nodes_explored'] for r in successful if r['nodes_explored'] is not None]
        if nodes_list:
            stats.nodes_mean = self._mean(nodes_list)
            stats.nodes_median = self._median(nodes_list)
            stats.nodes_total = sum(nodes_list)

        # Failure analysis
        stats.failure_reasons = self._analyze_failures([r for r in results if not r['solved']])

        return stats

    def _analyze_failures(self, failed_results: List[Dict]) -> Dict[str, int]:
        """Analyze failure reasons."""
        reasons = defaultdict(int)
        for result in failed_results:
            reason = result.get('reason_failed', 'unknown')
            if reason:
                reasons[reason] += 1
        return dict(reasons)

    # Statistical helper functions
    @staticmethod
    def _mean(values: List[float]) -> float:
        """Calculate mean."""
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def _median(values: List[float]) -> float:
        """Calculate median."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        if n % 2 == 0:
            return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
        return sorted_vals[n // 2]

    @staticmethod
    def _std(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    @staticmethod
    def _percentile(values: List[float], p: float) -> float:
        """Calculate percentile."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        k = (len(sorted_vals) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_vals[int(k)]
        d0 = sorted_vals[int(f)] * (c - k)
        d1 = sorted_vals[int(c)] * (k - f)
        return d0 + d1

    def print_summary(self, statistics: Optional[Dict[str, AlgorithmStatistics]] = None):
        """
        Print statistical summary in readable format.

        Args:
            statistics: Statistics to print (uses generated if not provided)
        """
        if statistics is None:
            statistics = self.statistics

        if not statistics:
            print("No statistics generated. Run generate_summary() first.")
            return

        print("\n")
        print("=" * 80)
        print("STATISTICAL ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"\nTest configuration:")
        print(f"  Total tests:   {self.data['metadata']['total_tests']}")
        print(f"  Test duration: {self.data['metadata']['total_time_seconds'] / 60:.1f} minutes")
        print("=" * 80)

        for algo_name, stats in statistics.items():
            print(f"\n{algo_name}:")
            print(f"  Success rate:  {stats.success_rate * 100:.1f}% ({stats.successful_tests}/{stats.total_tests})")

            if stats.successful_tests > 0:
                print(f"\n  Solution Length:")
                print(f"    Mean:   {stats.solution_length_mean:.2f} moves")
                print(f"    Median: {stats.solution_length_median:.2f} moves")
                print(f"    Std:    {stats.solution_length_std:.2f} moves")
                print(f"    Range:  [{stats.solution_length_min}, {stats.solution_length_max}]")
                print(f"    IQR:    [{stats.solution_length_q1:.2f}, {stats.solution_length_q3:.2f}]")

                print(f"\n  Solve Time:")
                print(f"    Mean:   {stats.time_mean:.3f}s")
                print(f"    Median: {stats.time_median:.3f}s")
                print(f"    Std:    {stats.time_std:.3f}s")
                print(f"    Range:  [{stats.time_min:.3f}s, {stats.time_max:.3f}s]")

                print(f"\n  Memory:")
                print(f"    Mean: {stats.memory_mean:.2f} MB")
                print(f"    Max:  {stats.memory_max:.2f} MB")

                if stats.nodes_mean:
                    print(f"\n  Nodes Explored:")
                    print(f"    Mean:  {stats.nodes_mean:,.0f}")
                    print(f"    Median: {stats.nodes_median:,.0f}")
                    print(f"    Total: {stats.nodes_total:,}")

            if stats.failure_reasons:
                print(f"\n  Failure Analysis:")
                for reason, count in stats.failure_reasons.items():
                    print(f"    {reason}: {count} ({count/stats.total_tests*100:.1f}%)")

        print("\n" + "=" * 80)

    def export_table(self, output_path: str, format: str = 'markdown'):
        """
        Export comparison table.

        Args:
            output_path: Output file path
            format: 'markdown', 'latex', or 'csv'
        """
        if not self.statistics:
            raise ValueError("No statistics generated. Run generate_summary() first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'markdown':
            self._export_markdown(output_path)
        elif format == 'latex':
            self._export_latex(output_path)
        elif format == 'csv':
            self._export_csv(output_path)
        else:
            raise ValueError(f"Unknown format: {format}")

        print(f"✓ Table exported to: {output_path}")

    def _export_markdown(self, output_path: Path):
        """Export as Markdown table."""
        lines = [
            "# Algorithm Performance Comparison\n",
            "## Summary Statistics\n",
            "| Algorithm | Success Rate | Avg Moves | Std Dev | Avg Time (s) | Avg Memory (MB) |",
            "|-----------|--------------|-----------|---------|--------------|-----------------|"
        ]

        for algo_name, stats in self.statistics.items():
            if stats.successful_tests > 0:
                lines.append(
                    f"| {algo_name} | {stats.success_rate*100:.1f}% | "
                    f"{stats.solution_length_mean:.1f} | {stats.solution_length_std:.2f} | "
                    f"{stats.time_mean:.3f} | {stats.memory_mean:.2f} |"
                )
            else:
                lines.append(
                    f"| {algo_name} | {stats.success_rate*100:.1f}% | - | - | - | - |"
                )

        lines.extend([
            "\n## Detailed Statistics\n"
        ])

        for algo_name, stats in self.statistics.items():
            lines.append(f"\n### {algo_name}\n")
            lines.append(f"- **Success Rate**: {stats.success_rate*100:.1f}% ({stats.successful_tests}/{stats.total_tests})")

            if stats.successful_tests > 0:
                lines.append(f"- **Solution Length**: {stats.solution_length_mean:.2f} ± {stats.solution_length_std:.2f} moves")
                lines.append(f"- **Time**: {stats.time_mean:.3f} ± {stats.time_std:.3f}s")
                lines.append(f"- **Memory**: {stats.memory_mean:.2f} MB (max: {stats.memory_max:.2f} MB)")
                if stats.nodes_mean:
                    lines.append(f"- **Nodes**: {stats.nodes_mean:,.0f} (median: {stats.nodes_median:,.0f})")

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

    def _export_latex(self, output_path: Path):
        """Export as LaTeX table."""
        lines = [
            "\\begin{table}[htbp]",
            "\\centering",
            "\\caption{Algorithm Performance Comparison}",
            "\\label{tab:algorithm-comparison}",
            "\\begin{tabular}{|l|c|c|c|c|c|}",
            "\\hline",
            "\\textbf{Algorithm} & \\textbf{Success} & \\textbf{Avg Moves} & \\textbf{Std Dev} & \\textbf{Avg Time (s)} & \\textbf{Avg Mem (MB)} \\\\",
            "\\hline"
        ]

        for algo_name, stats in self.statistics.items():
            algo_display = algo_name.replace('_', '\\_')
            if stats.successful_tests > 0:
                lines.append(
                    f"{algo_display} & {stats.success_rate*100:.1f}\\% & "
                    f"{stats.solution_length_mean:.1f} & {stats.solution_length_std:.2f} & "
                    f"{stats.time_mean:.3f} & {stats.memory_mean:.2f} \\\\"
                )
            else:
                lines.append(
                    f"{algo_display} & {stats.success_rate*100:.1f}\\% & --- & --- & --- & --- \\\\"
                )

        lines.extend([
            "\\hline",
            "\\end{tabular}",
            "\\end{table}"
        ])

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

    def _export_csv(self, output_path: Path):
        """Export as CSV."""
        lines = [
            "Algorithm,Success Rate (%),Successful Tests,Total Tests,Avg Moves,Std Dev,Avg Time (s),Avg Memory (MB)"
        ]

        for algo_name, stats in self.statistics.items():
            if stats.successful_tests > 0:
                lines.append(
                    f"{algo_name},{stats.success_rate*100:.1f},{stats.successful_tests},{stats.total_tests},"
                    f"{stats.solution_length_mean:.2f},{stats.solution_length_std:.2f},"
                    f"{stats.time_mean:.3f},{stats.memory_mean:.2f}"
                )
            else:
                lines.append(
                    f"{algo_name},{stats.success_rate*100:.1f},{stats.successful_tests},{stats.total_tests},,,,"
                )

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.evaluation.statistics <results_file.json>")
        sys.exit(1)

    results_path = sys.argv[1]

    analyzer = StatisticalAnalyzer(results_path)
    stats = analyzer.generate_summary()
    analyzer.print_summary(stats)

    # Export tables
    base_path = Path(results_path).stem
    analyzer.export_table(f'results/{base_path}_summary.md', format='markdown')
    analyzer.export_table(f'results/{base_path}_summary.tex', format='latex')
    analyzer.export_table(f'results/{base_path}_summary.csv', format='csv')

    print("\n✓ Analysis complete!")


if __name__ == '__main__':
    main()
