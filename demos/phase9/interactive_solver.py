"""
Interactive CLI Solver Demo

Provides a menu-driven interface for solving cubes with step-by-step progress.

Usage:
    python demos/phase9/interactive_solver.py

Features:
- Menu-driven interface
- Step-by-step solving with pause
- Colorized output
- Progress visualization
"""

import sys
import os
from pathlib import Path
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
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not found. Install with: pip install rich")
    print("Falling back to basic output.\n")


class InteractiveSolver:
    """Interactive command-line Rubik's Cube solver."""

    def __init__(self):
        """Initialize the interactive solver."""
        self.cube = RubikCube()
        self.solution = None
        self.solve_time = None
        self.algorithm_name = None

        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    def print(self, *args, **kwargs):
        """Print with rich if available, otherwise use regular print."""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def _solve_thistlethwaite(self):
        """Solve with pure Thistlethwaite and normalize the return value."""
        solver = ThistlethwaiteSolver(
            use_pattern_databases=True,
            enable_kociemba_fallback=False,
        )
        result = solver.solve(self.cube.copy(), max_time=30, verbose=False)
        if not result:
            return None

        solution, _phase_moves, _used_fallback = result
        return solution

    def _solve_kociemba(self):
        """Solve with Kociemba and normalize the return value."""
        solver = KociembaSolver()
        result = solver.solve(self.cube.copy(), timeout=60)
        if not result:
            return None

        solution, _phase1_moves, _phase2_moves = result
        return solution

    def _solve_korf(self):
        """Solve with the preferred Korf backend and normalize the return value."""
        if OPTIMAL_AVAILABLE:
            solver = KorfOptimalSolver()
            result = solver.solve(self.cube.copy(), verbose=False, timeout=120)
            if not result:
                return None
            solution, _stats = result
            return solution

        heuristic = create_heuristic('composite', use_pattern_db=True)
        solver = IDAStarSolver(heuristic=heuristic, max_depth=20, timeout=120)
        return solver.solve(self.cube.copy())

    def display_header(self):
        """Display application header."""
        if self.console:
            self.console.print(Panel.fit(
                "[bold cyan]🎲 Interactive Rubik's Cube Solver[/bold cyan]\n"
                "[yellow]Phase 9: Demos & UI[/yellow]\n"
                "[dim]Alex Toska - University of Patras[/dim]",
                border_style="cyan"
            ))
        else:
            print("\n" + "=" * 60)
            print("  Interactive Rubik's Cube Solver")
            print("  Phase 9: Demos & UI")
            print("  Alex Toska - University of Patras")
            print("=" * 60 + "\n")

    def display_cube(self):
        """Display current cube state."""
        self.print("\n[bold]Current Cube State:[/bold]" if self.console else "\nCurrent Cube State:")
        display_str = display_cube_unfolded(self.cube, colored=not self.console)
        print(display_str)

        if self.cube.is_solved():
            self.print("[bold green]✓ Cube is SOLVED![/bold green]" if self.console else "✓ Cube is SOLVED!")
        else:
            self.print("[yellow]○ Cube is scrambled[/yellow]" if self.console else "○ Cube is scrambled")

    def display_menu(self):
        """Display main menu."""
        if self.console:
            table = Table(title="Main Menu", show_header=False, border_style="blue")
            table.add_column("Option", style="cyan")
            table.add_column("Description", style="white")

            table.add_row("1", "Scramble cube (random)")
            table.add_row("2", "Scramble cube (with seed)")
            table.add_row("3", "Apply custom moves")
            table.add_row("4", "Solve with Thistlethwaite")
            table.add_row("5", "Solve with Kociemba")
            table.add_row("6", "Solve with Korf IDA*")
            table.add_row("7", "View solution (step-by-step)")
            table.add_row("8", "Reset cube")
            table.add_row("9", "View cube state")
            table.add_row("0", "Exit")

            self.console.print("\n")
            self.console.print(table)
        else:
            print("\n" + "=" * 60)
            print("Main Menu")
            print("=" * 60)
            print("  1. Scramble cube (random)")
            print("  2. Scramble cube (with seed)")
            print("  3. Apply custom moves")
            print("  4. Solve with Thistlethwaite")
            print("  5. Solve with Kociemba")
            print("  6. Solve with Korf IDA*")
            print("  7. View solution (step-by-step)")
            print("  8. Reset cube")
            print("  9. View cube state")
            print("  0. Exit")
            print("=" * 60)

    def scramble_random(self):
        """Scramble cube with random moves."""
        if RICH_AVAILABLE:
            depth = IntPrompt.ask("Scramble depth (5-25)", default=10)
        else:
            depth = int(input("Scramble depth (5-25) [default: 10]: ") or "10")

        depth = max(5, min(25, depth))

        self.cube = RubikCube()
        scramble_moves = self.cube.scramble(moves=depth)

        self.print(f"\n[green]✓ Scrambled with {depth} random moves[/green]" if self.console
                  else f"\n✓ Scrambled with {depth} random moves")
        self.print(f"[dim]Scramble: {' '.join(scramble_moves)}[/dim]" if self.console
                  else f"Scramble: {' '.join(scramble_moves)}")

        self.solution = None

    def scramble_seeded(self):
        """Scramble cube with seeded random."""
        if RICH_AVAILABLE:
            seed = IntPrompt.ask("Random seed", default=42)
            depth = IntPrompt.ask("Scramble depth (5-25)", default=10)
        else:
            seed = int(input("Random seed [default: 42]: ") or "42")
            depth = int(input("Scramble depth (5-25) [default: 10]: ") or "10")

        depth = max(5, min(25, depth))

        self.cube = RubikCube()
        scramble_moves = self.cube.scramble(moves=depth, seed=seed)

        self.print(f"\n[green]✓ Scrambled with seed {seed}, depth {depth}[/green]" if self.console
                  else f"\n✓ Scrambled with seed {seed}, depth {depth}")
        self.print(f"[dim]Scramble: {' '.join(scramble_moves)}[/dim]" if self.console
                  else f"Scramble: {' '.join(scramble_moves)}")

        self.solution = None

    def apply_custom_moves(self):
        """Apply custom move sequence."""
        if RICH_AVAILABLE:
            moves_str = Prompt.ask("Enter moves (space-separated)")
        else:
            moves_str = input("Enter moves (space-separated): ")

        moves = moves_str.split()

        try:
            for move in moves:
                self.cube.apply_move(move)
            self.print(f"\n[green]✓ Applied {len(moves)} moves[/green]" if self.console
                      else f"\n✓ Applied {len(moves)} moves")
            self.solution = None
        except Exception as e:
            self.print(f"[red]✗ Error: {str(e)}[/red]" if self.console
                      else f"✗ Error: {str(e)}")

    def solve_thistlethwaite(self):
        """Solve using Thistlethwaite algorithm."""
        if self.cube.is_solved():
            self.print("[yellow]Cube is already solved![/yellow]" if self.console
                      else "Cube is already solved!")
            return

        self.print("\n[cyan]Solving with Thistlethwaite...[/cyan]" if self.console
                  else "\nSolving with Thistlethwaite...")

        start_time = time.time()
        result = self._solve_thistlethwaite()
        self.solve_time = time.time() - start_time
        self.algorithm_name = "Thistlethwaite"

        if result:
            self.solution = result
            self.print(f"[green]✓ Solution found![/green]" if self.console
                      else "✓ Solution found!")
            self.print(f"  Moves: {len(self.solution)}")
            self.print(f"  Time: {self.solve_time:.3f}s")
        else:
            self.solution = None
            self.print("[red]✗ No solution found[/red]" if self.console
                      else "✗ No solution found")

    def solve_kociemba(self):
        """Solve using Kociemba algorithm."""
        if self.cube.is_solved():
            self.print("[yellow]Cube is already solved![/yellow]" if self.console
                      else "Cube is already solved!")
            return

        self.print("\n[cyan]Solving with Kociemba...[/cyan]" if self.console
                  else "\nSolving with Kociemba...")

        start_time = time.time()
        self.solution = self._solve_kociemba()
        self.solve_time = time.time() - start_time
        self.algorithm_name = "Kociemba"

        if self.solution:
            self.print(f"[green]✓ Solution found![/green]" if self.console
                      else "✓ Solution found!")
            self.print(f"  Moves: {len(self.solution)}")
            self.print(f"  Time: {self.solve_time:.3f}s")
        else:
            self.print("[red]✗ No solution found (timeout)[/red]" if self.console
                      else "✗ No solution found (timeout)")

    def solve_korf(self):
        """Solve using Korf IDA* algorithm."""
        if self.cube.is_solved():
            self.print("[yellow]Cube is already solved![/yellow]" if self.console
                      else "Cube is already solved!")
            return

        self.print("\n[cyan]Solving with Korf IDA*...[/cyan]" if self.console
                  else "\nSolving with Korf IDA*...")
        self.print("[yellow]Warning: This may take a while![/yellow]" if self.console
                  else "Warning: This may take a while!")

        start_time = time.time()
        result = self._solve_korf()
        self.solve_time = time.time() - start_time
        self.algorithm_name = "Korf IDA*"

        if result:
            self.solution = result
            self.print(f"[green]✓ Solution found![/green]" if self.console
                      else "✓ Solution found!")
            self.print(f"  Moves: {len(self.solution)}")
            self.print(f"  Time: {self.solve_time:.3f}s")
            if OPTIMAL_AVAILABLE:
                self.print("  Backend: external optimal solver")
            else:
                self.print("  Backend: internal heuristic IDA* fallback")
        else:
            self.print("[red]✗ No solution found (timeout or depth limit)[/red]" if self.console
                      else "✗ No solution found (timeout or depth limit)")

    def view_solution_stepwise(self):
        """View solution step by step."""
        if not self.solution:
            self.print("[yellow]No solution available. Solve the cube first![/yellow]" if self.console
                      else "No solution available. Solve the cube first!")
            return

        self.print(f"\n[bold]Solution ({self.algorithm_name}):[/bold]" if self.console
                  else f"\nSolution ({self.algorithm_name}):")
        self.print(f"Total moves: {len(self.solution)}\n")

        test_cube = self.cube.copy()

        for i, move in enumerate(self.solution, 1):
            self.print(f"\n[cyan]Step {i}/{len(self.solution)}: {move}[/cyan]" if self.console
                      else f"\nStep {i}/{len(self.solution)}: {move}")

            test_cube.apply_move(move)
            display_str = display_cube_unfolded(test_cube, colored=not self.console)
            print(display_str)

            if i < len(self.solution):
                if RICH_AVAILABLE:
                    if not Confirm.ask("Continue?", default=True):
                        break
                else:
                    cont = input("Continue? (y/n) [y]: ").lower()
                    if cont == 'n':
                        break

        if test_cube.is_solved():
            self.print("\n[bold green]✓✓✓ Cube SOLVED! ✓✓✓[/bold green]" if self.console
                      else "\n✓✓✓ Cube SOLVED! ✓✓✓")

    def reset_cube(self):
        """Reset cube to solved state."""
        self.cube = RubikCube()
        self.solution = None
        self.solve_time = None
        self.algorithm_name = None
        self.print("[green]✓ Cube reset to solved state[/green]" if self.console
                  else "✓ Cube reset to solved state")

    def run(self):
        """Run the interactive solver."""
        self.display_header()

        while True:
            self.display_menu()

            try:
                if RICH_AVAILABLE:
                    choice = Prompt.ask("\nSelect option", choices=[str(i) for i in range(10)], default="9")
                else:
                    choice = input("\nSelect option (0-9): ")

                if choice == "0":
                    self.print("\n[cyan]Thanks for using the solver! Goodbye![/cyan]" if self.console
                              else "\nThanks for using the solver! Goodbye!")
                    break
                elif choice == "1":
                    self.scramble_random()
                elif choice == "2":
                    self.scramble_seeded()
                elif choice == "3":
                    self.apply_custom_moves()
                elif choice == "4":
                    self.solve_thistlethwaite()
                elif choice == "5":
                    self.solve_kociemba()
                elif choice == "6":
                    self.solve_korf()
                elif choice == "7":
                    self.view_solution_stepwise()
                elif choice == "8":
                    self.reset_cube()
                elif choice == "9":
                    self.display_cube()
                else:
                    self.print("[red]Invalid option![/red]" if self.console
                              else "Invalid option!")

            except KeyboardInterrupt:
                self.print("\n\n[cyan]Interrupted by user. Goodbye![/cyan]" if self.console
                          else "\n\nInterrupted by user. Goodbye!")
                break
            except Exception as e:
                self.print(f"[red]Error: {str(e)}[/red]" if self.console
                          else f"Error: {str(e)}")


def main():
    """Main entry point."""
    solver = InteractiveSolver()
    solver.run()


if __name__ == '__main__':
    main()
