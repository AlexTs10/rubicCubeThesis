"""
Thistlethwaite Algorithm Demo

Demonstrates the use of Thistlethwaite's algorithm to solve Rubik's Cube.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite import ThistlethwaiteSolver


def demo_simple_solve():
    """Demonstrate solving a simple scramble."""
    print("="*70)
    print("THISTLETHWAITE ALGORITHM DEMO")
    print("="*70)

    # Create and scramble a cube
    print("\n1. Creating and scrambling cube...")
    cube = RubikCube()
    scramble = cube.scramble(moves=15, seed=42)

    print(f"   Scramble ({len(scramble)} moves): {' '.join(scramble)}")
    print(f"   Cube is solved: {cube.is_solved()}")

    # Solve with Thistlethwaite
    print("\n2. Solving with Thistlethwaite's Algorithm...")
    solver = ThistlethwaiteSolver(use_pattern_databases=False)

    result = solver.solve(cube, verbose=True)

    if result is None:
        print("\n❌ Failed to find solution!")
        return

    all_moves, phase_moves = result

    # Show results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    print(f"\nTotal solution length: {len(all_moves)} moves")
    print(f"Solution: {' '.join(all_moves)}")

    print("\n Phase breakdown:")
    for i, moves in enumerate(phase_moves):
        print(f"   Phase {i}: {len(moves):2d} moves - {' '.join(moves) if moves else '(none)'}")

    # Verify solution
    print("\n3. Verifying solution...")
    test_cube = RubikCube()
    test_cube.apply_moves(scramble)
    print(f"   Before solution: is_solved = {test_cube.is_solved()}")

    test_cube.apply_moves(all_moves)
    print(f"   After solution:  is_solved = {test_cube.is_solved()}")

    if test_cube.is_solved():
        print("\n✅ Solution verified successfully!")
    else:
        print("\n❌ Solution verification failed!")


def demo_multiple_scrambles():
    """Demonstrate solving multiple scrambles."""
    print("\n" + "="*70)
    print("SOLVING MULTIPLE SCRAMBLES")
    print("="*70)

    solver = ThistlethwaiteSolver(use_pattern_databases=False)

    results = []

    for i in range(5):
        print(f"\n--- Scramble {i+1} ---")
        cube = RubikCube()
        scramble = cube.scramble(moves=10, seed=i)

        print(f"Scramble: {' '.join(scramble)}")

        result = solver.solve(cube, verbose=False)

        if result is not None:
            all_moves, phase_moves = result

            # Verify
            test_cube = RubikCube()
            test_cube.apply_moves(scramble)
            test_cube.apply_moves(all_moves)

            success = test_cube.is_solved()

            results.append({
                'scramble_length': len(scramble),
                'solution_length': len(all_moves),
                'phase_lengths': [len(p) for p in phase_moves],
                'success': success
            })

            status = "✅" if success else "❌"
            print(f"Solution: {len(all_moves)} moves {status}")
        else:
            print("❌ No solution found")
            results.append(None)

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    successful = [r for r in results if r is not None and r['success']]
    print(f"\nSuccessful solves: {len(successful)} / {len(results)}")

    if successful:
        avg_length = sum(r['solution_length'] for r in successful) / len(successful)
        min_length = min(r['solution_length'] for r in successful)
        max_length = max(r['solution_length'] for r in successful)

        print(f"Average solution length: {avg_length:.1f} moves")
        print(f"Min solution length: {min_length} moves")
        print(f"Max solution length: {max_length} moves")

        # Phase statistics
        print("\nAverage moves per phase:")
        for phase in range(4):
            avg_phase = sum(r['phase_lengths'][phase] for r in successful) / len(successful)
            print(f"  Phase {phase}: {avg_phase:.1f} moves")


def demo_with_visualization():
    """Demonstrate solving with 2D visualization."""
    print("\n" + "="*70)
    print("SOLVING WITH VISUALIZATION")
    print("="*70)

    try:
        from src.cube.visualize_2d import visualize_cube
    except ImportError:
        print("Visualization not available")
        return

    # Create and scramble
    cube = RubikCube()
    print("\nInitial state (solved):")
    visualize_cube(cube)

    scramble = cube.scramble(moves=10, seed=99)
    print(f"\nAfter scramble ({' '.join(scramble)}):")
    visualize_cube(cube)

    # Solve
    solver = ThistlethwaiteSolver(use_pattern_databases=False)
    result = solver.solve(cube, verbose=False)

    if result is not None:
        all_moves, _ = result
        print(f"\nSolution: {' '.join(all_moves)}")
        print(f"Length: {len(all_moves)} moves")

        # Apply solution
        cube.apply_moves(all_moves)
        print("\nAfter applying solution:")
        visualize_cube(cube)


def main():
    """Run all demos."""
    # Demo 1: Simple solve with detailed output
    demo_simple_solve()

    # Demo 2: Multiple scrambles
    demo_multiple_scrambles()

    # Demo 3: With visualization (if available)
    try:
        demo_with_visualization()
    except Exception as e:
        print(f"\nVisualization demo skipped: {e}")

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
