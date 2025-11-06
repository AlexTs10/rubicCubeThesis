"""
Unit tests for move utilities.
"""

import pytest
from src.cube.moves import (
    inverse_move, inverse_sequence,
    parse_move_sequence, format_move_sequence,
    simplify_moves, count_moves, are_opposite_faces
)


class TestInverseMove:
    """Test inverse move functionality."""

    def test_basic_move_inverse(self):
        """Test inverse of basic moves."""
        assert inverse_move('R') == "R'"
        assert inverse_move('U') == "U'"
        assert inverse_move('F') == "F'"
        assert inverse_move('L') == "L'"
        assert inverse_move('B') == "B'"
        assert inverse_move('D') == "D'"

    def test_prime_move_inverse(self):
        """Test inverse of prime moves."""
        assert inverse_move("R'") == 'R'
        assert inverse_move("U'") == 'U'
        assert inverse_move("F'") == 'F'

    def test_double_move_inverse(self):
        """Test that double moves are self-inverse."""
        assert inverse_move('R2') == 'R2'
        assert inverse_move('U2') == 'U2'
        assert inverse_move('F2') == 'F2'

    def test_invalid_move(self):
        """Test invalid moves raise errors."""
        with pytest.raises(ValueError):
            inverse_move('R3')


class TestInverseSequence:
    """Test inverse sequence functionality."""

    def test_simple_sequence(self):
        """Test inverse of simple sequence."""
        moves = ['R', 'U', 'F']
        expected = ["F'", "U'", "R'"]
        assert inverse_sequence(moves) == expected

    def test_sequence_with_primes(self):
        """Test inverse with prime moves."""
        moves = ['R', "U'", 'F2']
        expected = ['F2', 'U', "R'"]
        assert inverse_sequence(moves) == expected

    def test_empty_sequence(self):
        """Test inverse of empty sequence."""
        assert inverse_sequence([]) == []

    def test_single_move(self):
        """Test inverse of single move."""
        assert inverse_sequence(['R']) == ["R'"]


class TestParseAndFormat:
    """Test parsing and formatting move sequences."""

    def test_parse_simple_sequence(self):
        """Test parsing space-separated moves."""
        sequence = "R U R' U'"
        expected = ['R', 'U', "R'", "U'"]
        assert parse_move_sequence(sequence) == expected

    def test_parse_with_double_moves(self):
        """Test parsing with double moves."""
        sequence = "R2 U2 F2"
        expected = ['R2', 'U2', 'F2']
        assert parse_move_sequence(sequence) == expected

    def test_parse_with_extra_spaces(self):
        """Test parsing with extra spaces."""
        sequence = "R  U   R'    U'"
        expected = ['R', 'U', "R'", "U'"]
        assert parse_move_sequence(sequence) == expected

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        assert parse_move_sequence("") == []
        assert parse_move_sequence("   ") == []

    def test_format_sequence(self):
        """Test formatting move list to string."""
        moves = ['R', 'U', "R'", "U'"]
        expected = "R U R' U'"
        assert format_move_sequence(moves) == expected

    def test_format_empty(self):
        """Test formatting empty list."""
        assert format_move_sequence([]) == ""


class TestSimplifyMoves:
    """Test move simplification."""

    def test_simplify_three_same_moves(self):
        """Test that R R R simplifies to R'."""
        moves = ['R', 'R', 'R']
        expected = ["R'"]
        assert simplify_moves(moves) == expected

    def test_simplify_four_same_moves(self):
        """Test that four same moves cancel out."""
        moves = ['R', 'R', 'R', 'R']
        expected = []
        assert simplify_moves(moves) == expected

    def test_simplify_with_double(self):
        """Test simplification with double moves."""
        moves = ['R', 'R2']
        expected = ["R'"]
        assert simplify_moves(moves) == expected

    def test_simplify_with_prime(self):
        """Test simplification with prime moves."""
        moves = ['R', "R'"]
        expected = []
        assert simplify_moves(moves) == expected

    def test_simplify_mixed_faces(self):
        """Test that different faces don't simplify."""
        moves = ['R', 'U', 'R', 'U']
        assert simplify_moves(moves) == moves

    def test_simplify_complex_sequence(self):
        """Test complex simplification."""
        moves = ['R', 'R', 'U', 'U', 'U', 'R']
        expected = ['R2', "U'", 'R']
        assert simplify_moves(moves) == expected

    def test_simplify_empty(self):
        """Test simplifying empty sequence."""
        assert simplify_moves([]) == []


class TestCountMoves:
    """Test move counting."""

    def test_count_simple_sequence(self):
        """Test counting simple sequence."""
        moves = ['R', 'U', "R'", "U'"]
        assert count_moves(moves) == 4

    def test_count_empty(self):
        """Test counting empty sequence."""
        assert count_moves([]) == 0

    def test_count_with_doubles(self):
        """Test counting includes double moves."""
        moves = ['R2', 'U2', 'F2']
        assert count_moves(moves) == 3


class TestOppositeFaces:
    """Test opposite face detection."""

    def test_ud_opposite(self):
        """Test U and D are opposite."""
        assert are_opposite_faces('U', 'D')
        assert are_opposite_faces('D', 'U')

    def test_fb_opposite(self):
        """Test F and B are opposite."""
        assert are_opposite_faces('F', 'B')
        assert are_opposite_faces('B', 'F')

    def test_lr_opposite(self):
        """Test L and R are opposite."""
        assert are_opposite_faces('L', 'R')
        assert are_opposite_faces('R', 'L')

    def test_not_opposite(self):
        """Test adjacent faces are not opposite."""
        assert not are_opposite_faces('U', 'F')
        assert not are_opposite_faces('R', 'F')
        assert not are_opposite_faces('L', 'U')

    def test_same_face_not_opposite(self):
        """Test same face is not opposite to itself."""
        assert not are_opposite_faces('R', 'R')
        assert not are_opposite_faces('U', 'U')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
