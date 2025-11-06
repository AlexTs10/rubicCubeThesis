"""
Basic usage demonstration of the Rubik's Cube implementation.

This script shows how to:
1. Create and manipulate a cube
2. Apply moves and sequences
3. Scramble and check state
"""

import sys
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cube.rubik_cube import RubikCube
from src.cube.moves import (format_move_sequence, inverse_sequence,
                            simplify_moves, parse_move_sequence)


def main():
    """Run basic usage demonstrations."""

    print("=" * 60)
    print("Rubik's Cube Implementation - Basic Usage Demo")
    print("=" * 60)
    print()

    # 1. Create a solved cube
    print("1. Creating a solved cube:")
    cube = RubikCube()
    print(f"   Is solved? {cube.is_solved()}")
    print()

    # 2. Apply a single move
    print("2. Applying move 'R' (Right face clockwise):")
    cube.apply_move('R')
    print(f"   Is solved? {cube.is_solved()}")
    print()

    # 3. Undo the move
    print("3. Applying inverse move 'R\\'' (Right face counter-clockwise):")
    cube.apply_move("R'")
    print(f"   Is solved? {cube.is_solved()}")
    print()

    # 4. Apply a sequence
    print("4. Applying sequence 'R U R\\' U\\'' (Sexy Move):")
    cube = RubikCube()
    sequence = "R U R' U'"
    cube.apply_move_sequence(sequence)
    print(f"   Applied: {sequence}")
    print(f"   Is solved? {cube.is_solved()}")
    print()

    # 5. Scramble
    print("5. Scrambling cube with 20 random moves:")
    cube = RubikCube()
    scramble = cube.scramble(moves=20, seed=42)
    print(f"   Scramble: {format_move_sequence(scramble)}")
    print(f"   Is solved? {cube.is_solved()}")
    print()

    # 6. Move utilities
    print("6. Move utilities demonstration:")
    moves = parse_move_sequence("R U R' U'")
    print(f"   Original: {format_move_sequence(moves)}")

    inverse = inverse_sequence(moves)
    print(f"   Inverse:  {format_move_sequence(inverse)}")

    to_simplify = ['R', 'R', 'R']
    simplified = simplify_moves(to_simplify)
    print(f"   Simplify ['R', 'R', 'R'] -> {simplified}")
    print()

    # 7. Verify inverse works
    print("7. Verifying sequence + inverse = solved:")
    cube = RubikCube()
    test_sequence = parse_move_sequence("R U R' U' F' U' F U")
    cube.apply_moves(test_sequence)
    print(f"   After sequence: solved = {cube.is_solved()}")

    inverse = inverse_sequence(test_sequence)
    cube.apply_moves(inverse)
    print(f"   After inverse: solved = {cube.is_solved()}")
    print()

    # 8. Display cube state
    print("8. Cube state visualization:")
    cube = RubikCube()
    cube.apply_move_sequence("R U")
    print(cube)

    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
