"""
Benchmark Demo

Quick benchmark of all algorithms on multiple scrambles.

Usage:
    python demos/phase9/benchmark_demo.py [--n-scrambles N] [--depth DEPTH]

Example:
    python demos/phase9/benchmark_demo.py --n-scrambles 20 --depth 10
"""

import sys
from pathlib import Path
import argparse
import statistics

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.evaluation.algorithm_comparison import AlgorithmComparison

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_header(console=None):
    """Print application header."""
    if console:
        console.print(Panel.fit(
            "[bold cyan]📊 Algorithm Benchmark Tool[/bold cyan]\n"
            "[yellow]Performance testing for all three algorithms[/yellow]\n"
            "[dim]Phase 9: Demos & UI | Alex Toska[/dim]",
            border_style="cyan"
        ))
    else:
        print("\n" + "=" * 70)
        print("  📊 Algorithm Benchmark Tool")
        print("  Performance testing for all three algorithms")
        print("  Phase 9: Demos & UI | Alex Toska")
        print("=" * 70 + "\n")


def print_summary_statistics(comparison, console=None):
    """Print summary statistics."""
    summaries = comparison.generate_summary()

    if console:
        console.print("\n[bold cyan]📈 Summary Statistics[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="yellow")
        table.add_column("Thistlethwaite", justify="right", style="blue")
        table.add_column("Kociemba", justify="right", style="green")
        table.add_column("Korf IDA*", justify="right", style="magenta")

        # Success rate
        table.add_row(
            "Success Rate",
            f"{summaries['Thistlethwaite'].success_rate * 100:.1f}%",
            f"{summaries['Kociemba'].success_rate * 100:.1f}%",
            f"{summaries['Korf_IDA*'].success_rate * 100:.1f}%"
        )

        # Average moves
        table.add_row(
            "Avg Moves",
            f"{summaries['Thistlethwaite'].avg_solution_length:.1f}",
            f"{summaries['Kociemba'].avg_solution_length:.1f}",
            f"{summaries['Korf_IDA*'].avg_solution_length:.1f}"
        )

        # Move range
        table.add_row(
            "Move Range",
            f"{summaries['Thistlethwaite'].min_solution_length}-{summaries['Thistlethwaite'].max_solution_length}",
            f"{summaries['Kociemba'].min_solution_length}-{summaries['Kociemba'].max_solution_length}",
            f"{summaries['Korf_IDA*'].min_solution_length}-{summaries['Korf_IDA*'].max_solution_length}"
        )

        # Average time
        table.add_row(
            "Avg Time (s)",
            f"{summaries['Thistlethwaite'].avg_time_seconds:.3f}",
            f"{summaries['Kociemba'].avg_time_seconds:.3f}",
            f"{summaries['Korf_IDA*'].avg_time_seconds:.3f}"
        )

        # Time range
        table.add_row(
            "Time Range (s)",
            f"{summaries['Thistlethwaite'].min_time_seconds:.3f}-{summaries['Thistlethwaite'].max_time_seconds:.3f}",
            f"{summaries['Kociemba'].min_time_seconds:.3f}-{summaries['Kociemba'].max_time_seconds:.3f}",
            f"{summaries['Korf_IDA*'].min_time_seconds:.3f}-{summaries['Korf_IDA*'].max_time_seconds:.3f}"
        )

        # Average memory
        table.add_row(
            "Avg Memory (MB)",
            f"{summaries['Thistlethwaite'].avg_memory_mb:.2f}",
            f"{summaries['Kociemba'].avg_memory_mb:.2f}",
            f"{summaries['Korf_IDA*'].avg_memory_mb:.2f}"
        )

        console.print(table)

    else:
        print("\n📈 Summary Statistics\n")
        print("=" * 90)
        print(f"{'Metric':<20} {'Thistlethwaite':<20} {'Kociemba':<20} {'Korf IDA*':<20}")
        print("=" * 90)

        print(f"{'Success Rate':<20} "
              f"{summaries['Thistlethwaite'].success_rate * 100:<20.1f}% "
              f"{summaries['Kociemba'].success_rate * 100:<20.1f}% "
              f"{summaries['Korf_IDA*'].success_rate * 100:<20.1f}%")

        print(f"{'Avg Moves':<20} "
              f"{summaries['Thistlethwaite'].avg_solution_length:<20.1f} "
              f"{summaries['Kociemba'].avg_solution_length:<20.1f} "
              f"{summaries['Korf_IDA*'].avg_solution_length:<20.1f}")

        print(f"{'Avg Time (s)':<20} "
              f"{summaries['Thistlethwaite'].avg_time_seconds:<20.3f} "
              f"{summaries['Kociemba'].avg_time_seconds:<20.3f} "
              f"{summaries['Korf_IDA*'].avg_time_seconds:<20.3f}")

        print(f"{'Avg Memory (MB)':<20} "
              f"{summaries['Thistlethwaite'].avg_memory_mb:<20.2f} "
              f"{summaries['Kociemba'].avg_memory_mb:<20.2f} "
              f"{summaries['Korf_IDA*'].avg_memory_mb:<20.2f}")

        print("=" * 90 + "\n")


def print_winners(comparison, console=None):
    """Print winner analysis."""
    summaries = comparison.generate_summary()

    if console:
        console.print("\n[bold cyan]🏆 Overall Winners[/bold cyan]\n")

        # Fewest moves
        moves_data = [
            ("Thistlethwaite", summaries['Thistlethwaite'].avg_solution_length),
            ("Kociemba", summaries['Kociemba'].avg_solution_length),
            ("Korf IDA*", summaries['Korf_IDA*'].avg_solution_length)
        ]
        winner = min(moves_data, key=lambda x: x[1])
        console.print(f"[green]Fewest Moves:[/green] {winner[0]} ({winner[1]:.1f} avg)")

        # Fastest
        time_data = [
            ("Thistlethwaite", summaries['Thistlethwaite'].avg_time_seconds),
            ("Kociemba", summaries['Kociemba'].avg_time_seconds),
            ("Korf IDA*", summaries['Korf_IDA*'].avg_time_seconds)
        ]
        winner = min(time_data, key=lambda x: x[1])
        console.print(f"[green]Fastest:[/green] {winner[0]} ({winner[1]:.3f}s avg)")

        # Least memory
        mem_data = [
            ("Thistlethwaite", summaries['Thistlethwaite'].avg_memory_mb),
            ("Kociemba", summaries['Kociemba'].avg_memory_mb),
            ("Korf IDA*", summaries['Korf_IDA*'].avg_memory_mb)
        ]
        winner = min(mem_data, key=lambda x: x[1])
        console.print(f"[green]Least Memory:[/green] {winner[0]} ({winner[1]:.2f} MB avg)")

    else:
        print("\n🏆 Overall Winners\n")

        # Fewest moves
        moves_data = [
            ("Thistlethwaite", summaries['Thistlethwaite'].avg_solution_length),
            ("Kociemba", summaries['Kociemba'].avg_solution_length),
            ("Korf IDA*", summaries['Korf_IDA*'].avg_solution_length)
        ]
        winner = min(moves_data, key=lambda x: x[1])
        print(f"Fewest Moves: {winner[0]} ({winner[1]:.1f} avg)")

        # Fastest
        time_data = [
            ("Thistlethwaite", summaries['Thistlethwaite'].avg_time_seconds),
            ("Kociemba", summaries['Kociemba'].avg_time_seconds),
            ("Korf IDA*", summaries['Korf_IDA*'].avg_time_seconds)
        ]
        winner = min(time_data, key=lambda x: x[1])
        print(f"Fastest: {winner[0]} ({winner[1]:.3f}s avg)")

        # Least memory
        mem_data = [
            ("Thistlethwaite", summaries['Thistlethwaite'].avg_memory_mb),
            ("Kociemba", summaries['Kociemba'].avg_memory_mb),
            ("Korf IDA*", summaries['Korf_IDA*'].avg_memory_mb)
        ]
        winner = min(mem_data, key=lambda x: x[1])
        print(f"Least Memory: {winner[0]} ({winner[1]:.2f} MB avg)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Benchmark Rubik's Cube solving algorithms")
    parser.add_argument('--n-scrambles', type=int, default=10,
                       help='Number of scrambles to test (default: 10)')
    parser.add_argument('--depth', type=int, default=10,
                       help='Scramble depth (default: 10)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--export', type=str,
                       help='Export results to file (JSON or Markdown)')

    args = parser.parse_args()

    console = Console() if RICH_AVAILABLE else None

    # Print header
    print_header(console)

    # Display configuration
    if console:
        console.print(f"[cyan]Configuration:[/cyan]")
        console.print(f"  Number of Scrambles: {args.n_scrambles}")
        console.print(f"  Scramble Depth: {args.depth}")
        console.print(f"  Random Seed: {args.seed}\n")
    else:
        print(f"Configuration:")
        print(f"  Number of Scrambles: {args.n_scrambles}")
        print(f"  Scramble Depth: {args.depth}")
        print(f"  Random Seed: {args.seed}\n")

    # Initialize comparison framework
    if console:
        with console.status("[cyan]Initializing solvers...[/cyan]"):
            comparison = AlgorithmComparison(
                thistlethwaite_timeout=30.0,
                kociemba_timeout=60.0,
                korf_timeout=120.0,
                korf_max_depth=20
            )
        console.print("[green]✓ Solvers initialized[/green]\n")
    else:
        print("Initializing solvers...")
        comparison = AlgorithmComparison(
            thistlethwaite_timeout=30.0,
            kociemba_timeout=60.0,
            korf_timeout=120.0,
            korf_max_depth=20
        )
        print("✓ Solvers initialized\n")

    # Run benchmark
    if console:
        console.print(f"[bold cyan]Running benchmark on {args.n_scrambles} scrambles...[/bold cyan]\n")
    else:
        print(f"Running benchmark on {args.n_scrambles} scrambles...\n")

    results = comparison.run_batch_test(
        n_scrambles=args.n_scrambles,
        scramble_depth=args.depth,
        seed=args.seed
    )

    # Print results
    print_summary_statistics(comparison, console)
    print_winners(comparison, console)

    # Export if requested
    if args.export:
        if args.export.endswith('.json'):
            comparison.export_results(args.export)
            if console:
                console.print(f"\n[green]✓ Results exported to {args.export}[/green]")
            else:
                print(f"\n✓ Results exported to {args.export}")
        elif args.export.endswith('.md'):
            comparison.export_summary_table(args.export, format='markdown')
            if console:
                console.print(f"\n[green]✓ Summary exported to {args.export}[/green]")
            else:
                print(f"\n✓ Summary exported to {args.export}")
        else:
            if console:
                console.print(f"\n[yellow]⚠ Unknown export format. Use .json or .md[/yellow]")
            else:
                print(f"\n⚠ Unknown export format. Use .json or .md")

    if console:
        console.print("\n[cyan]Benchmark complete![/cyan]")
    else:
        print("\nBenchmark complete!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
