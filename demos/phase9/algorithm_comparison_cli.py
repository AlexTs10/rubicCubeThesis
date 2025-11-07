"""
Algorithm Comparison CLI Tool

Run all three algorithms on the same scramble and display results side-by-side.

Usage:
    python demos/phase9/algorithm_comparison_cli.py [--depth DEPTH] [--seed SEED]

Example:
    python demos/phase9/algorithm_comparison_cli.py --depth 10 --seed 42
"""

import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cube.rubik_cube import RubikCube
from src.evaluation.algorithm_comparison import AlgorithmComparison

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_header(console=None):
    """Print application header."""
    if console:
        console.print(Panel.fit(
            "[bold cyan]⚖️  Algorithm Comparison Tool[/bold cyan]\n"
            "[yellow]Compare Thistlethwaite vs Kociemba vs Korf IDA*[/yellow]\n"
            "[dim]Phase 9: Demos & UI | Alex Toska[/dim]",
            border_style="cyan"
        ))
    else:
        print("\n" + "=" * 70)
        print("  ⚖️  Algorithm Comparison Tool")
        print("  Compare Thistlethwaite vs Kociemba vs Korf IDA*")
        print("  Phase 9: Demos & UI | Alex Toska")
        print("=" * 70 + "\n")


def print_comparison_table(result, console=None):
    """Print comparison results in a formatted table."""
    if console:
        # Rich table
        table = Table(title="Algorithm Comparison Results", show_header=True, header_style="bold cyan")

        table.add_column("Algorithm", style="yellow", width=15)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Moves", justify="right", width=8)
        table.add_column("Time (s)", justify="right", width=10)
        table.add_column("Memory (MB)", justify="right", width=12)
        table.add_column("Nodes", justify="right", width=12)

        # Add rows
        algorithms = [
            ("Thistlethwaite", result.thistlethwaite, "blue"),
            ("Kociemba", result.kociemba, "green"),
            ("Korf IDA*", result.korf, "magenta")
        ]

        for name, r, color in algorithms:
            if r.solved:
                table.add_row(
                    f"[{color}]{name}[/{color}]",
                    "[green]✓[/green]",
                    str(r.solution_length),
                    f"{r.time_seconds:.3f}",
                    f"{r.memory_mb:.2f}",
                    str(r.nodes_explored) if r.nodes_explored else "N/A"
                )
            else:
                table.add_row(
                    f"[{color}]{name}[/{color}]",
                    "[red]✗[/red]",
                    "-",
                    f"{r.time_seconds:.3f}",
                    f"{r.memory_mb:.2f}",
                    "-"
                )

        console.print("\n")
        console.print(table)

    else:
        # Plain text table
        print("\n" + "=" * 90)
        print(f"{'Algorithm':<20} {'Status':<10} {'Moves':<10} {'Time (s)':<12} {'Memory (MB)':<15} {'Nodes':<12}")
        print("=" * 90)

        algorithms = [
            ("Thistlethwaite", result.thistlethwaite),
            ("Kociemba", result.kociemba),
            ("Korf IDA*", result.korf)
        ]

        for name, r in algorithms:
            if r.solved:
                print(f"{name:<20} {'✓':<10} {r.solution_length:<10} {r.time_seconds:<12.3f} "
                      f"{r.memory_mb:<15.2f} {r.nodes_explored if r.nodes_explored else 'N/A':<12}")
            else:
                print(f"{name:<20} {'✗':<10} {'-':<10} {r.time_seconds:<12.3f} "
                      f"{r.memory_mb:<15.2f} {'-':<12}")

        print("=" * 90 + "\n")


def print_winners(result, console=None):
    """Print winner analysis."""
    solved_results = []
    if result.thistlethwaite.solved:
        solved_results.append(("Thistlethwaite", result.thistlethwaite))
    if result.kociemba.solved:
        solved_results.append(("Kociemba", result.kociemba))
    if result.korf.solved:
        solved_results.append(("Korf IDA*", result.korf))

    if not solved_results:
        if console:
            console.print("[red]No algorithms succeeded![/red]")
        else:
            print("No algorithms succeeded!")
        return

    if console:
        console.print("\n[bold cyan]🏆 Winner Analysis[/bold cyan]\n")
    else:
        print("\n🏆 Winner Analysis\n")

    # Fewest moves
    winner_moves = min(solved_results, key=lambda x: x[1].solution_length)
    if console:
        console.print(f"[green]Fewest Moves:[/green] {winner_moves[0]} ({winner_moves[1].solution_length} moves)")
    else:
        print(f"Fewest Moves: {winner_moves[0]} ({winner_moves[1].solution_length} moves)")

    # Fastest time
    winner_time = min(solved_results, key=lambda x: x[1].time_seconds)
    if console:
        console.print(f"[green]Fastest:[/green] {winner_time[0]} ({winner_time[1].time_seconds:.3f}s)")
    else:
        print(f"Fastest: {winner_time[0]} ({winner_time[1].time_seconds:.3f}s)")

    # Least memory
    winner_memory = min(solved_results, key=lambda x: x[1].memory_mb)
    if console:
        console.print(f"[green]Least Memory:[/green] {winner_memory[0]} ({winner_memory[1].memory_mb:.2f} MB)")
    else:
        print(f"Least Memory: {winner_memory[0]} ({winner_memory[1].memory_mb:.2f} MB)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Compare Rubik's Cube solving algorithms")
    parser.add_argument('--depth', type=int, default=10, help='Scramble depth (default: 10)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    parser.add_argument('--thistle-timeout', type=float, default=30.0, help='Thistlethwaite timeout (s)')
    parser.add_argument('--kociemba-timeout', type=float, default=60.0, help='Kociemba timeout (s)')
    parser.add_argument('--korf-timeout', type=float, default=120.0, help='Korf timeout (s)')
    parser.add_argument('--korf-max-depth', type=int, default=20, help='Korf max depth')
    parser.add_argument('--export', type=str, help='Export results to file (JSON or Markdown)')

    args = parser.parse_args()

    console = Console() if RICH_AVAILABLE else None

    # Print header
    print_header(console)

    # Display configuration
    if console:
        console.print(f"[cyan]Configuration:[/cyan]")
        console.print(f"  Scramble Depth: {args.depth}")
        console.print(f"  Random Seed: {args.seed}")
        console.print(f"  Timeouts: Thistle={args.thistle_timeout}s, "
                     f"Kociemba={args.kociemba_timeout}s, Korf={args.korf_timeout}s")
        console.print(f"  Korf Max Depth: {args.korf_max_depth}\n")
    else:
        print(f"Configuration:")
        print(f"  Scramble Depth: {args.depth}")
        print(f"  Random Seed: {args.seed}")
        print(f"  Timeouts: Thistle={args.thistle_timeout}s, "
              f"Kociemba={args.kociemba_timeout}s, Korf={args.korf_timeout}s")
        print(f"  Korf Max Depth: {args.korf_max_depth}\n")

    # Create scramble
    if console:
        console.print("[cyan]Creating scramble...[/cyan]")
    else:
        print("Creating scramble...")

    cube = RubikCube()
    cube.scramble(n_moves=args.depth, seed=args.seed)
    scramble_moves = getattr(cube, '_scramble_moves', [])

    if console:
        console.print(f"[green]✓ Scramble created:[/green] {' '.join(scramble_moves)}\n")
    else:
        print(f"✓ Scramble created: {' '.join(scramble_moves)}\n")

    # Initialize comparison framework
    if console:
        with console.status("[cyan]Initializing solvers...[/cyan]"):
            comparison = AlgorithmComparison(
                thistlethwaite_timeout=args.thistle_timeout,
                kociemba_timeout=args.kociemba_timeout,
                korf_timeout=args.korf_timeout,
                korf_max_depth=args.korf_max_depth
            )
        console.print("[green]✓ Solvers initialized[/green]\n")
    else:
        print("Initializing solvers...")
        comparison = AlgorithmComparison(
            thistlethwaite_timeout=args.thistle_timeout,
            kociemba_timeout=args.kociemba_timeout,
            korf_timeout=args.korf_timeout,
            korf_max_depth=args.korf_max_depth
        )
        print("✓ Solvers initialized\n")

    # Run comparison
    if console:
        console.print("[bold cyan]Running comparison...[/bold cyan]\n")
    else:
        print("Running comparison...\n")

    result = comparison.compare_on_scramble(cube, scramble_id=0)

    # Display results
    print_comparison_table(result, console)
    print_winners(result, console)

    # Display solutions
    if console:
        console.print("\n[bold cyan]Solution Sequences:[/bold cyan]\n")
    else:
        print("\nSolution Sequences:\n")

    for name, algo_result in [
        ("Thistlethwaite", result.thistlethwaite),
        ("Kociemba", result.kociemba),
        ("Korf IDA*", result.korf)
    ]:
        if algo_result.solved and algo_result.solution_moves:
            if console:
                console.print(f"[yellow]{name}[/yellow] ({algo_result.solution_length} moves):")
                console.print(f"  {' '.join(algo_result.solution_moves)}\n")
            else:
                print(f"{name} ({algo_result.solution_length} moves):")
                print(f"  {' '.join(algo_result.solution_moves)}\n")

    # Export if requested
    if args.export:
        if args.export.endswith('.json'):
            comparison.export_results(args.export)
            if console:
                console.print(f"[green]✓ Results exported to {args.export}[/green]")
            else:
                print(f"✓ Results exported to {args.export}")
        elif args.export.endswith('.md'):
            comparison.export_summary_table(args.export, format='markdown')
            if console:
                console.print(f"[green]✓ Summary exported to {args.export}[/green]")
            else:
                print(f"✓ Summary exported to {args.export}")
        else:
            if console:
                console.print(f"[yellow]⚠ Unknown export format. Use .json or .md[/yellow]")
            else:
                print(f"⚠ Unknown export format. Use .json or .md")

    if console:
        console.print("\n[cyan]Comparison complete![/cyan]")
    else:
        print("\nComparison complete!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
