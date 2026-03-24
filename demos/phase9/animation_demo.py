"""
Animation Demo

Play back solution sequences move-by-move with adjustable speed.

Usage:
    python demos/phase9/animation_demo.py [--algorithm ALGO] [--depth DEPTH] [--speed SPEED]

Example:
    python demos/phase9/animation_demo.py --algorithm kociemba --depth 10 --speed 0.5
"""

import sys
import os
from pathlib import Path
import argparse
import time


def _configure_local_cache() -> None:
    """Point matplotlib/fontconfig at a writable cache under /tmp."""
    cache_root = Path("/tmp/rubicCubeThesis_phase9_cache")
    mpl_cache = cache_root / "matplotlib"
    xdg_cache = cache_root / "xdg"
    mpl_cache.mkdir(parents=True, exist_ok=True)
    xdg_cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_cache))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_cache))


_configure_local_cache()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cube.rubik_cube import RubikCube
from src.cube.visualization import display_cube_unfolded
from src.thistlethwaite import ThistlethwaiteSolver
from src.kociemba.solver import KociembaSolver
from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic
from src.korf.optimal_solver import KorfOptimalSolver, OPTIMAL_AVAILABLE

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.progress import Progress, BarColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def solve_thistlethwaite(cube: RubikCube):
    """Solve with pure Thistlethwaite and normalize the return value."""
    solver = ThistlethwaiteSolver(
        use_pattern_databases=True,
        enable_kociemba_fallback=False,
    )
    result = solver.solve(cube.copy(), max_time=30, verbose=False)
    if not result:
        return None

    solution, _phase_moves, _used_fallback = result
    return solution


def solve_kociemba(cube: RubikCube):
    """Solve with Kociemba and normalize the return value."""
    solver = KociembaSolver()
    result = solver.solve(cube.copy(), timeout=60)
    if not result:
        return None

    solution, _phase1_moves, _phase2_moves = result
    return solution


def solve_korf(cube: RubikCube):
    """Solve with the preferred Korf backend and normalize the return value."""
    if OPTIMAL_AVAILABLE:
        solver = KorfOptimalSolver()
        result = solver.solve(cube.copy(), verbose=False, timeout=120)
        if not result:
            return None
        solution, _stats = result
        return solution

    heuristic = create_heuristic('composite', use_pattern_db=True)
    solver = IDAStarSolver(heuristic=heuristic, max_depth=20, timeout=120)
    return solver.solve(cube.copy())


def animate_solution(cube, solution, speed=1.0, algorithm_name="Algorithm"):
    """
    Animate the solution sequence.

    Args:
        cube: Initial scrambled RubikCube
        solution: List of moves
        speed: Delay between moves in seconds
        algorithm_name: Name of the algorithm used
    """
    console = Console() if RICH_AVAILABLE else None

    if console:
        console.print(Panel.fit(
            f"[bold cyan]🎬 Solution Animation[/bold cyan]\n"
            f"[yellow]Algorithm: {algorithm_name}[/yellow]\n"
            f"[dim]Total moves: {len(solution)} | Speed: {speed}s/move[/dim]",
            border_style="cyan"
        ))
    else:
        print("\n" + "=" * 70)
        print(f"  🎬 Solution Animation")
        print(f"  Algorithm: {algorithm_name}")
        print(f"  Total moves: {len(solution)} | Speed: {speed}s/move")
        print("=" * 70 + "\n")

    # Initial state
    current_cube = cube.copy()

    if console:
        console.print("\n[bold yellow]Initial State (Scrambled)[/bold yellow]\n")
    else:
        print("\nInitial State (Scrambled)\n")

    display_str = display_cube_unfolded(current_cube, colored=not console)
    print(display_str)
    time.sleep(speed * 2)  # Pause to view initial state

    # Animate each move
    for i, move in enumerate(solution, 1):
        clear_screen()

        if console:
            console.print(Panel.fit(
                f"[bold cyan]Move {i}/{len(solution)}: {move}[/bold cyan]\n"
                f"[dim]Algorithm: {algorithm_name}[/dim]",
                border_style="cyan"
            ))
        else:
            print("\n" + "=" * 70)
            print(f"  Move {i}/{len(solution)}: {move}")
            print("=" * 70 + "\n")

        # Apply move
        current_cube.apply_move(move)

        # Display cube
        display_str = display_cube_unfolded(current_cube, colored=not console)
        print(display_str)

        # Progress bar
        if console:
            progress_pct = (i / len(solution)) * 100
            console.print(f"\n[cyan]Progress: {progress_pct:.1f}% complete[/cyan]")

        # Wait before next move
        if i < len(solution):
            time.sleep(speed)

    # Final state
    time.sleep(speed)
    clear_screen()

    if console:
        if current_cube.is_solved():
            console.print(Panel.fit(
                "[bold green]✓✓✓ CUBE SOLVED! ✓✓✓[/bold green]\n"
                f"[yellow]Algorithm: {algorithm_name}[/yellow]\n"
                f"[dim]Solution length: {len(solution)} moves[/dim]",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold red]⚠ Solution incomplete[/bold red]",
                border_style="red"
            ))
    else:
        if current_cube.is_solved():
            print("\n" + "=" * 70)
            print("  ✓✓✓ CUBE SOLVED! ✓✓✓")
            print(f"  Algorithm: {algorithm_name}")
            print(f"  Solution length: {len(solution)} moves")
            print("=" * 70 + "\n")
        else:
            print("\n⚠ Solution incomplete\n")

    display_str = display_cube_unfolded(current_cube, colored=not console)
    print(display_str)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Animate Rubik's Cube solving")
    parser.add_argument('--algorithm', choices=['thistlethwaite', 'kociemba', 'korf'],
                       default='thistlethwaite', help='Algorithm to use (default: thistlethwaite)')
    parser.add_argument('--depth', type=int, default=10, help='Scramble depth (default: 10)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    parser.add_argument('--speed', type=float, default=1.0, help='Speed in seconds per move (default: 1.0)')

    args = parser.parse_args()

    console = Console() if RICH_AVAILABLE else None

    # Print header
    if console:
        console.print(Panel.fit(
            "[bold cyan]🎬 Rubik's Cube Animation Demo[/bold cyan]\n"
            "[yellow]Phase 9: Demos & UI[/yellow]\n"
            "[dim]Alex Toska - University of Patras[/dim]",
            border_style="cyan"
        ))
    else:
        print("\n" + "=" * 70)
        print("  🎬 Rubik's Cube Animation Demo")
        print("  Phase 9: Demos & UI")
        print("  Alex Toska - University of Patras")
        print("=" * 70 + "\n")

    # Create scramble
    if console:
        console.print(f"\n[cyan]Creating scramble (depth {args.depth}, seed {args.seed})...[/cyan]")
    else:
        print(f"\nCreating scramble (depth {args.depth}, seed {args.seed})...")

    cube = RubikCube()
    scramble_moves = cube.scramble(moves=args.depth, seed=args.seed)

    if console:
        console.print(f"[green]✓ Scramble:[/green] {' '.join(scramble_moves)}\n")
    else:
        print(f"✓ Scramble: {' '.join(scramble_moves)}\n")

    # Solve
    if console:
        console.print(f"[cyan]Solving with {args.algorithm}...[/cyan]")
    else:
        print(f"Solving with {args.algorithm}...")

    solution = None
    algorithm_name = args.algorithm.capitalize()
    if args.algorithm == 'thistlethwaite':
        solution = solve_thistlethwaite(cube)
        algorithm_name = "Thistlethwaite"

    elif args.algorithm == 'kociemba':
        solution = solve_kociemba(cube)
        algorithm_name = "Kociemba"

    elif args.algorithm == 'korf':
        solution = solve_korf(cube)
        algorithm_name = (
            "Korf IDA* (optimal backend)"
            if OPTIMAL_AVAILABLE
            else "Korf IDA* (heuristic fallback)"
        )

    if not solution:
        if console:
            console.print("[red]✗ Failed to find solution[/red]")
        else:
            print("✗ Failed to find solution")
        return

    if console:
        console.print(f"[green]✓ Solution found: {len(solution)} moves[/green]")
        console.print(f"[yellow]Starting animation in 3 seconds...[/yellow]\n")
    else:
        print(f"✓ Solution found: {len(solution)} moves")
        print("Starting animation in 3 seconds...\n")

    time.sleep(3)

    # Animate
    animate_solution(cube, solution, speed=args.speed, algorithm_name=algorithm_name)

    if console:
        console.print("\n[cyan]Animation complete![/cyan]")
    else:
        print("\nAnimation complete!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
