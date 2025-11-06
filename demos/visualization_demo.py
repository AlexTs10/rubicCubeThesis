"""
Visualization Demo for Rubik's Cube.

This script demonstrates both 2D and 3D visualization capabilities.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cube import (
    RubikCube,
    visualize_2d, visualize_2d_with_moves,
    visualize_3d, visualize_3d_interactive, visualize_3d_sequence
)


def demo_2d_basic():
    """Demonstrate basic 2D visualization."""
    print("=" * 60)
    print("Demo 1: Basic 2D Visualization")
    print("=" * 60)

    # Solved cube
    cube = RubikCube()
    print("\n1. Visualizing a solved cube in 2D...")
    visualize_2d(cube, title="Solved Rubik's Cube")

    # Scrambled cube
    print("\n2. Visualizing a scrambled cube in 2D...")
    cube.scramble(moves=15, seed=42)
    visualize_2d(cube, title="Scrambled Rubik's Cube")


def demo_2d_with_moves():
    """Demonstrate 2D visualization with move sequences."""
    print("\n" + "=" * 60)
    print("Demo 2: 2D Visualization with Move Sequence")
    print("=" * 60)

    cube = RubikCube()
    moves = ['R', 'U', 'R\'', 'U\'']  # Sexy move

    print(f"\nVisualizing the 'Sexy Move': {' '.join(moves)}")
    visualize_2d_with_moves(cube, moves)


def demo_3d_basic():
    """Demonstrate basic 3D visualization."""
    print("\n" + "=" * 60)
    print("Demo 3: Basic 3D Visualization")
    print("=" * 60)

    # Solved cube
    cube = RubikCube()
    print("\n1. Visualizing a solved cube in 3D...")
    visualize_3d(cube, title="Solved Rubik's Cube - 3D View")

    # Scrambled cube
    print("\n2. Visualizing a scrambled cube in 3D...")
    cube.scramble(moves=20, seed=123)
    visualize_3d(cube, title="Scrambled Rubik's Cube - 3D View")


def demo_3d_interactive():
    """Demonstrate interactive 3D visualization."""
    print("\n" + "=" * 60)
    print("Demo 4: Interactive 3D Visualization")
    print("=" * 60)

    cube = RubikCube()
    cube.apply_move_sequence("R U R' U' F' U' F U")

    print("\nShowing interactive 3D view...")
    print("TIP: Click and drag to rotate the cube!")
    visualize_3d_interactive(cube)


def demo_3d_sequence():
    """Demonstrate 3D visualization of move sequence."""
    print("\n" + "=" * 60)
    print("Demo 5: 3D Visualization of Move Sequence")
    print("=" * 60)

    cube = RubikCube()
    moves = ['R', 'U', 'R\'', 'U\'', 'R\'', 'F', 'R', 'F\'']

    print(f"\nVisualizing algorithm: {' '.join(moves)}")
    visualize_3d_sequence(cube, moves)


def demo_different_angles():
    """Demonstrate 3D visualization from different angles."""
    print("\n" + "=" * 60)
    print("Demo 6: 3D Views from Different Angles")
    print("=" * 60)

    cube = RubikCube()
    cube.apply_move_sequence("R U R' U'")

    print("\nShowing cube from different viewing angles...")

    # Different viewing angles
    angles = [
        (20, -60, "Default View"),
        (0, 0, "Front View"),
        (0, 90, "Side View"),
        (90, 0, "Top View"),
        (30, -135, "Corner View")
    ]

    for elev, azim, name in angles:
        print(f"  - {name}")
        visualize_3d(cube, title=f"Rubik's Cube - {name}",
                    elev=elev, azim=azim)


def demo_algorithms():
    """Demonstrate visualization of common algorithms."""
    print("\n" + "=" * 60)
    print("Demo 7: Common Rubik's Cube Algorithms")
    print("=" * 60)

    algorithms = {
        "Sexy Move": "R U R' U'",
        "T-Perm": "R U R' U' R' F R2 U' R' U' R U R' F'",
        "Sledgehammer": "R' F R F'",
        "Sune": "R U R' U R U2 R'",
    }

    for name, algorithm in algorithms.items():
        print(f"\n{name}: {algorithm}")
        cube = RubikCube()
        print("  Showing 2D visualization...")
        visualize_2d_with_moves(cube, algorithm.split())


def demo_all():
    """Run all demos."""
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  Rubik's Cube Visualization Demo Suite".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)

    demos = [
        ("1", "Basic 2D Visualization", demo_2d_basic),
        ("2", "2D with Move Sequence", demo_2d_with_moves),
        ("3", "Basic 3D Visualization", demo_3d_basic),
        ("4", "Interactive 3D", demo_3d_interactive),
        ("5", "3D Move Sequence", demo_3d_sequence),
        ("6", "Different Viewing Angles", demo_different_angles),
        ("7", "Common Algorithms", demo_algorithms),
    ]

    print("\nAvailable Demos:")
    for num, name, _ in demos:
        print(f"  {num}. {name}")
    print("  0. Run all demos")

    try:
        choice = input("\nSelect demo (0-7): ").strip()

        if choice == "0":
            for _, _, demo_func in demos:
                demo_func()
        elif choice in [d[0] for d in demos]:
            demo = next(d for d in demos if d[0] == choice)
            demo[2]()
        else:
            print("Invalid choice!")
            return

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        return

    print("\n" + "=" * 60)
    print("Demo completed! Thank you for viewing.")
    print("=" * 60)


if __name__ == '__main__':
    demo_all()
