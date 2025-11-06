"""
Unit tests for RubikCube class.
"""

import pytest
import numpy as np
from src.cube.rubik_cube import RubikCube, Face
from src.cube.moves import inverse_sequence


class TestRubikCubeBasics:
    """Test basic cube functionality."""

    def test_cube_initialization(self):
        """Test that a new cube is in solved state."""
        cube = RubikCube()
        assert cube.is_solved()

    def test_cube_copy(self):
        """Test cube copying."""
        cube1 = RubikCube()
        cube1.scramble(moves=5, seed=42)

        cube2 = cube1.copy()
        assert cube1 == cube2
        assert cube1 is not cube2
        assert not np.shares_memory(cube1.state, cube2.state)

    def test_cube_equality(self):
        """Test cube equality."""
        cube1 = RubikCube()
        cube2 = RubikCube()
        assert cube1 == cube2

        cube1.apply_move('R')
        assert cube1 != cube2

    def test_solved_state(self):
        """Test solved state detection."""
        cube = RubikCube()
        assert cube.is_solved()

        cube.apply_move('R')
        assert not cube.is_solved()

        cube.apply_move('R\'')
        assert cube.is_solved()


class TestBasicMoves:
    """Test basic cube moves."""

    def test_move_and_inverse(self):
        """Test that a move and its inverse return to solved state."""
        moves = ['U', 'D', 'F', 'B', 'L', 'R']

        for move in moves:
            cube = RubikCube()
            cube.apply_move(move)
            assert not cube.is_solved()

            cube.apply_move(move + "'")
            assert cube.is_solved(), f"Move {move} and {move}' should return to solved"

    def test_double_moves(self):
        """Test double moves."""
        cube = RubikCube()
        original = cube.copy()

        cube.apply_move('R2')
        assert not cube.is_solved()

        cube.apply_move('R2')
        assert cube == original

    def test_four_moves_return_to_start(self):
        """Test that four identical moves return to start."""
        for move in ['U', 'D', 'F', 'B', 'L', 'R']:
            cube = RubikCube()
            original = cube.copy()

            for _ in range(4):
                cube.apply_move(move)

            assert cube == original, f"Four {move} moves should return to original"


class TestMoveSequences:
    """Test move sequences."""

    def test_apply_moves_list(self):
        """Test applying a list of moves."""
        cube = RubikCube()
        moves = ['R', 'U', 'R\'', 'U\'']
        cube.apply_moves(moves)
        assert not cube.is_solved()

    def test_apply_move_sequence_string(self):
        """Test applying a space-separated move sequence."""
        cube = RubikCube()
        cube.apply_move_sequence("R U R' U'")
        assert not cube.is_solved()

    def test_inverse_sequence(self):
        """Test that a sequence and its inverse cancel out."""
        cube = RubikCube()
        sequence = ['R', 'U', 'R\'', 'U\'']

        cube.apply_moves(sequence)
        assert not cube.is_solved()

        # Apply inverse sequence using the utility function
        inv = inverse_sequence(sequence)
        cube.apply_moves(inv)
        assert cube.is_solved()


class TestScrambling:
    """Test scrambling functionality."""

    def test_scramble(self):
        """Test basic scrambling."""
        cube = RubikCube()
        moves = cube.scramble(moves=20, seed=42)

        assert len(moves) == 20
        # After 20 random moves, cube is very likely not solved
        # (though technically possible with specific moves)

    def test_scramble_reproducibility(self):
        """Test that scrambling with same seed gives same result."""
        cube1 = RubikCube()
        moves1 = cube1.scramble(moves=10, seed=123)

        cube2 = RubikCube()
        moves2 = cube2.scramble(moves=10, seed=123)

        assert moves1 == moves2
        assert cube1 == cube2


class TestMoveValidation:
    """Test move validation and error handling."""

    def test_invalid_move(self):
        """Test that invalid moves raise errors."""
        cube = RubikCube()

        with pytest.raises(ValueError):
            cube.apply_move('X')  # Invalid face

        with pytest.raises(ValueError):
            cube.apply_move('R3')  # Invalid modifier

    def test_empty_move(self):
        """Test that empty move does nothing."""
        cube = RubikCube()
        original = cube.copy()
        cube.apply_move('')
        assert cube == original


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
