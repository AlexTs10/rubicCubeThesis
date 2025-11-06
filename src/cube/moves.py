"""
Move utilities for Rubik's Cube.

This module provides utilities for working with move sequences,
including parsing, formatting, and optimizing move sequences.
"""

from typing import List, Tuple


# All basic moves in Singmaster notation
BASIC_MOVES = ['U', 'D', 'F', 'B', 'L', 'R']
ALL_MOVES = ['U', 'U\'', 'U2', 'D', 'D\'', 'D2',
             'F', 'F\'', 'F2', 'B', 'B\'', 'B2',
             'L', 'L\'', 'L2', 'R', 'R\'', 'R2']


def inverse_move(move: str) -> str:
    """
    Get the inverse of a move.

    Args:
        move: Move string like 'U', 'R\'', 'F2'

    Returns:
        Inverse move string

    Examples:
        >>> inverse_move('U')
        "U'"
        >>> inverse_move("R'")
        'R'
        >>> inverse_move('F2')
        'F2'
    """
    if len(move) == 1:
        return move + "'"
    elif move.endswith("'"):
        return move[0]
    elif move.endswith('2'):
        return move  # Double moves are self-inverse
    else:
        raise ValueError(f"Invalid move: {move}")


def inverse_sequence(moves: List[str]) -> List[str]:
    """
    Get the inverse of a move sequence.

    Args:
        moves: List of moves

    Returns:
        Inverse sequence (reversed with each move inverted)

    Example:
        >>> inverse_sequence(['R', 'U', 'R\''])
        ['R', "U'", "R'"]
    """
    return [inverse_move(move) for move in reversed(moves)]


def parse_move_sequence(sequence: str) -> List[str]:
    """
    Parse a space-separated move sequence string.

    Args:
        sequence: String like "R U R' U'"

    Returns:
        List of individual moves

    Example:
        >>> parse_move_sequence("R U R' U'")
        ['R', 'U', "R'", "U'"]
    """
    return [move.strip() for move in sequence.split() if move.strip()]


def format_move_sequence(moves: List[str]) -> str:
    """
    Format a list of moves as a space-separated string.

    Args:
        moves: List of move strings

    Returns:
        Space-separated string

    Example:
        >>> format_move_sequence(['R', 'U', "R'"])
        "R U R'"
    """
    return ' '.join(moves)


def simplify_moves(moves: List[str]) -> List[str]:
    """
    Simplify a move sequence by combining consecutive moves on the same face.

    Args:
        moves: List of moves

    Returns:
        Simplified move sequence

    Example:
        >>> simplify_moves(['R', 'R', 'R'])
        ["R'"]
        >>> simplify_moves(['U', 'U2'])
        ["U'"]
    """
    if not moves:
        return []

    # Convert moves to (face, count) representation
    def move_to_count(move: str) -> Tuple[str, int]:
        """Convert move to (face, rotation_count) where count is 1, 2, or 3."""
        face = move[0]
        if len(move) == 1:
            return (face, 1)
        elif move.endswith("'"):
            return (face, 3)  # Prime = 3 clockwise
        elif move.endswith('2'):
            return (face, 2)
        else:
            raise ValueError(f"Invalid move: {move}")

    def count_to_move(face: str, count: int) -> str:
        """Convert (face, count) to move string."""
        count = count % 4  # Normalize to 0-3
        if count == 0:
            return None
        elif count == 1:
            return face
        elif count == 2:
            return face + '2'
        elif count == 3:
            return face + "'"

    simplified = []
    current_face = None
    current_count = 0

    for move in moves:
        face, count = move_to_count(move)

        if face == current_face:
            current_count += count
        else:
            # Save previous move if exists
            if current_face is not None:
                move_str = count_to_move(current_face, current_count)
                if move_str is not None:
                    simplified.append(move_str)

            # Start new face
            current_face = face
            current_count = count

    # Don't forget the last move
    if current_face is not None:
        move_str = count_to_move(current_face, current_count)
        if move_str is not None:
            simplified.append(move_str)

    return simplified


def count_moves(moves: List[str]) -> int:
    """
    Count the number of moves in a sequence.

    This is simply the length of the list, but provided for clarity
    and potential future extensions (e.g., metric variations).

    Args:
        moves: List of moves

    Returns:
        Number of moves
    """
    return len(moves)


def are_opposite_faces(face1: str, face2: str) -> bool:
    """
    Check if two faces are opposite to each other.

    Args:
        face1: First face letter ('U', 'D', 'F', 'B', 'L', 'R')
        face2: Second face letter

    Returns:
        True if faces are opposite

    Opposite pairs:
        U-D, F-B, L-R
    """
    opposite_pairs = [('U', 'D'), ('D', 'U'),
                     ('F', 'B'), ('B', 'F'),
                     ('L', 'R'), ('R', 'L')]
    return (face1, face2) in opposite_pairs
