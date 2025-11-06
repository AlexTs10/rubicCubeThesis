"""
Advanced unit tests for RubikCube class.

These tests cover edge cases, specific move combinations,
and cube state properties.
"""

import pytest
import numpy as np
from src.cube.rubik_cube import RubikCube, Face


class TestCubeStateProperties:
    """Test cube state properties and invariants."""

    def test_solved_cube_all_faces_uniform(self):
        """Test that solved cube has uniform colors on each face."""
        cube = RubikCube()

        for face in Face:
            face_state = cube.get_face(face)
            # All stickers on a face should have the same color in solved state
            assert np.all(face_state == face.value)

    def test_total_stickers_unchanged(self):
        """Test that total number of each color is preserved."""
        cube = RubikCube()

        # Count initial colors
        initial_counts = {i: 0 for i in range(6)}
        for i in range(6):
            initial_counts[i] = np.sum(cube.state == i)

        # Scramble
        cube.scramble(moves=50, seed=42)

        # Count after scrambling
        final_counts = {i: 0 for i in range(6)}
        for i in range(6):
            final_counts[i] = np.sum(cube.state == i)

        # Should be the same
        assert initial_counts == final_counts

    def test_cube_has_54_stickers(self):
        """Test that cube always has 54 stickers."""
        cube = RubikCube()
        assert cube.state.size == 54

        cube.scramble(moves=20)
        assert cube.state.size == 54


class TestMoveCommutators:
    """Test move commutators and their properties."""

    def test_commutator_ru(self):
        """Test R U R' U' commutator (sexy move)."""
        cube = RubikCube()

        # Apply sexy move 6 times should return to solved (mostly)
        for _ in range(6):
            cube.apply_move_sequence("R U R' U'")

        assert cube.is_solved()

    def test_non_commuting_moves(self):
        """Test that R U != U R."""
        cube1 = RubikCube()
        cube1.apply_move('R')
        cube1.apply_move('U')

        cube2 = RubikCube()
        cube2.apply_move('U')
        cube2.apply_move('R')

        assert cube1 != cube2

    def test_opposite_faces_commute(self):
        """Test that opposite face moves commute (U D = D U)."""
        cube1 = RubikCube()
        cube1.apply_move('U')
        cube1.apply_move('D')

        cube2 = RubikCube()
        cube2.apply_move('D')
        cube2.apply_move('U')

        assert cube1 == cube2


class TestMoveOrders:
    """Test the order (period) of different moves."""

    def test_quarter_turn_order_4(self):
        """Test that quarter turns have order 4."""
        for move in ['U', 'D', 'F', 'B', 'L', 'R']:
            cube = RubikCube()
            for _ in range(4):
                cube.apply_move(move)
            assert cube.is_solved(), f"Move {move} should have order 4"

    def test_half_turn_order_2(self):
        """Test that half turns have order 2."""
        for move in ['U2', 'D2', 'F2', 'B2', 'L2', 'R2']:
            cube = RubikCube()
            for _ in range(2):
                cube.apply_move(move)
            assert cube.is_solved(), f"Move {move} should have order 2"

    def test_superflip_algorithm(self):
        """Test a known long algorithm."""
        cube = RubikCube()
        # This is not the full superflip, just testing a complex sequence
        sequence = "R L U2 R' L' U R L U2 R' L' U"
        cube.apply_move_sequence(sequence)

        # Apply twice should give identity
        cube.apply_move_sequence(sequence)
        assert cube.is_solved()


class TestSpecificPatterns:
    """Test specific cube patterns and their properties."""

    def test_checkerboard_pattern(self):
        """Test checkerboard pattern generation."""
        cube = RubikCube()
        # Checkerboard pattern
        cube.apply_move_sequence("R2 L2 U2 D2 F2 B2")

        # Should not be solved
        assert not cube.is_solved()

        # Apply again to return to solved
        cube.apply_move_sequence("R2 L2 U2 D2 F2 B2")
        assert cube.is_solved()

    def test_cross_pattern(self):
        """Test cross pattern on top face."""
        cube = RubikCube()
        # Simple cross pattern algorithm
        cube.apply_move_sequence("F U R U' R' F'")

        assert not cube.is_solved()


class TestCopyAndEquality:
    """Test copy and equality operations."""

    def test_deep_copy_modification(self):
        """Test that modifying copy doesn't affect original."""
        original = RubikCube()
        original.scramble(moves=5, seed=42)

        copy = original.copy()
        copy.apply_move('R')

        assert original != copy

    def test_equality_reflexive(self):
        """Test that a cube equals itself."""
        cube = RubikCube()
        assert cube == cube

    def test_equality_symmetric(self):
        """Test that equality is symmetric."""
        cube1 = RubikCube()
        cube2 = RubikCube()

        assert cube1 == cube2
        assert cube2 == cube1

    def test_equality_transitive(self):
        """Test that equality is transitive."""
        cube1 = RubikCube()
        cube2 = RubikCube()
        cube3 = RubikCube()

        assert cube1 == cube2
        assert cube2 == cube3
        assert cube1 == cube3

    def test_hash_consistency(self):
        """Test that equal cubes have equal hashes."""
        cube1 = RubikCube()
        cube2 = RubikCube()

        assert hash(cube1) == hash(cube2)

    def test_hash_after_same_scramble(self):
        """Test hash after same scramble sequence."""
        cube1 = RubikCube()
        cube1.scramble(moves=10, seed=42)

        cube2 = RubikCube()
        cube2.scramble(moves=10, seed=42)

        assert hash(cube1) == hash(cube2)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_apply_no_move(self):
        """Test applying empty move."""
        cube = RubikCube()
        original = cube.copy()

        cube.apply_move('')
        assert cube == original

    def test_apply_empty_sequence(self):
        """Test applying empty move sequence."""
        cube = RubikCube()
        original = cube.copy()

        cube.apply_moves([])
        assert cube == original

        cube.apply_move_sequence("")
        assert cube == original

    def test_scramble_zero_moves(self):
        """Test scrambling with zero moves."""
        cube = RubikCube()
        moves = cube.scramble(moves=0)

        assert len(moves) == 0
        assert cube.is_solved()

    def test_large_scramble(self):
        """Test large scramble doesn't break anything."""
        cube = RubikCube()
        moves = cube.scramble(moves=1000, seed=42)

        assert len(moves) == 1000
        # Cube should still be valid (correct number of each color)
        for i in range(6):
            assert np.sum(cube.state == i) == 9


class TestMoveConsistency:
    """Test consistency of move implementations."""

    def test_move_using_different_methods(self):
        """Test that different ways of applying moves give same result."""
        # Method 1: Using move function
        cube1 = RubikCube()
        cube1.move_R()

        # Method 2: Using apply_move
        cube2 = RubikCube()
        cube2.apply_move('R')

        # Method 3: Using apply_moves
        cube3 = RubikCube()
        cube3.apply_moves(['R'])

        # Method 4: Using apply_move_sequence
        cube4 = RubikCube()
        cube4.apply_move_sequence('R')

        assert cube1 == cube2 == cube3 == cube4

    def test_prime_is_three_quarters(self):
        """Test that R' equals R R R."""
        cube1 = RubikCube()
        cube1.apply_move("R'")

        cube2 = RubikCube()
        cube2.apply_move('R')
        cube2.apply_move('R')
        cube2.apply_move('R')

        assert cube1 == cube2

    def test_double_is_two_quarters(self):
        """Test that R2 equals R R."""
        cube1 = RubikCube()
        cube1.apply_move('R2')

        cube2 = RubikCube()
        cube2.apply_move('R')
        cube2.apply_move('R')

        assert cube1 == cube2


class TestStringRepresentation:
    """Test string representation of cube."""

    def test_str_contains_faces(self):
        """Test that string representation contains all faces."""
        cube = RubikCube()
        cube_str = str(cube)

        for face in ['U', 'D', 'F', 'B', 'L', 'R']:
            assert face in cube_str

    def test_str_shows_solved_status(self):
        """Test that string shows solved status."""
        cube = RubikCube()
        assert "Solved: True" in str(cube)

        cube.apply_move('R')
        assert "Solved: False" in str(cube)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
