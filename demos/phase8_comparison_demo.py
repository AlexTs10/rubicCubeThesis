"""
Phase 8: Comprehensive Algorithm Comparison Demo

This demo showcases the unified algorithm comparison framework that tests
all three implemented algorithms (Thistlethwaite, Kociemba, Korf) on identical
scrambles and collects standardized metrics.

Usage:
    python demos/phase8_comparison_demo.py

This will:
1. Initialize all three solvers
2. Run a quick 10-scramble comparison test
3. Display summary statistics
4. Export results to JSON and Markdown
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.algorithm_comparison import AlgorithmComparison


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Run Phase 8 comparison demo."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Phase 8: Comprehensive Algorithm Comparison".center(68) + "║")
    print("║" + "  Testing Thistlethwaite vs Kociemba vs Korf".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Initialize comparison framework
    print_header("STEP 1: Initialize Comparison Framework")

    comparison = AlgorithmComparison(
        thistlethwaite_timeout=30.0,
        kociemba_timeout=60.0,
        korf_timeout=120.0,
        korf_max_depth=20
    )

    # Run quick test
    print_header("STEP 2: Run Comparison Test")
    print("Testing all algorithms on 10 identical scrambles...")
    print("Scramble depth: 7 moves")
    print("Random seed: 42 (for reproducibility)")
    print()

    results = comparison.run_batch_test(
        n_scrambles=10,
        scramble_depth=7,
        seed=42
    )

    # Generate and print summary
    print_header("STEP 3: Statistical Summary")

    summaries = comparison.generate_summary()
    comparison.print_summary(summaries)

    # Print detailed comparison
    print_header("STEP 4: Algorithm Comparison Analysis")

    thistle_summary = summaries['Thistlethwaite']
    kociemba_summary = summaries['Kociemba']
    korf_summary = summaries['Korf_IDA*']

    print("\nSolution Quality (Average Moves):")
    print(f"  1. {'Korf_IDA*' if korf_summary.avg_solution_length <= kociemba_summary.avg_solution_length else 'Kociemba'}: "
          f"{min(korf_summary.avg_solution_length, kociemba_summary.avg_solution_length):.1f} moves (optimal/near-optimal)")
    print(f"  2. {'Kociemba' if korf_summary.avg_solution_length <= kociemba_summary.avg_solution_length else 'Korf_IDA*'}: "
          f"{max(korf_summary.avg_solution_length, kociemba_summary.avg_solution_length):.1f} moves")
    print(f"  3. Thistlethwaite: {thistle_summary.avg_solution_length:.1f} moves (sub-optimal)")

    print("\nSpeed (Average Time):")
    times = [
        ('Thistlethwaite', thistle_summary.avg_time_seconds),
        ('Kociemba', kociemba_summary.avg_time_seconds),
        ('Korf_IDA*', korf_summary.avg_time_seconds)
    ]
    times.sort(key=lambda x: x[1])

    for i, (name, time_val) in enumerate(times, 1):
        print(f"  {i}. {name}: {time_val:.3f}s")

    print("\nMemory Usage (Average):")
    memories = [
        ('Thistlethwaite', thistle_summary.avg_memory_mb),
        ('Kociemba', kociemba_summary.avg_memory_mb),
        ('Korf_IDA*', korf_summary.avg_memory_mb)
    ]
    memories.sort(key=lambda x: x[1])

    for i, (name, mem_val) in enumerate(memories, 1):
        print(f"  {i}. {name}: {mem_val:.2f} MB")

    print("\nSuccess Rates:")
    for name, summary in summaries.items():
        print(f"  {name}: {summary.success_rate * 100:.1f}% ({summary.successful_solves}/{summary.total_tests})")

    # Export results
    print_header("STEP 5: Export Results")

    comparison.export_results('results/phase8_quick_test.json')
    comparison.export_summary_table('results/phase8_summary.md', format='markdown')
    comparison.export_summary_table('results/phase8_summary.tex', format='latex')

    print("\nResults exported:")
    print("  ✓ JSON data:      results/phase8_quick_test.json")
    print("  ✓ Markdown table: results/phase8_summary.md")
    print("  ✓ LaTeX table:    results/phase8_summary.tex")

    # Final summary
    print_header("Summary")

    print("\nPhase 8 Comparison Framework - Key Features:")
    print("  ✓ Unified testing of all 3 algorithms")
    print("  ✓ Identical scrambles for fair comparison")
    print("  ✓ Comprehensive metrics (moves, time, memory, nodes)")
    print("  ✓ Statistical analysis (mean, std dev, min/max)")
    print("  ✓ Export to JSON, Markdown, and LaTeX")
    print("  ✓ Progress tracking for large test runs")

    print("\nNext Steps:")
    print("  1. Run full 1000-scramble test suite")
    print("  2. Test various scramble depths (5, 10, 15, 20)")
    print("  3. Generate visualizations (charts, graphs)")
    print("  4. Validate against cube20.org test cases")
    print("  5. Compile results for thesis")

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
