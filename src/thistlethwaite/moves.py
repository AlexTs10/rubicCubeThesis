"""
Move Definitions for Thistlethwaite Algorithm

Defines the allowed move sets for each phase of the algorithm.
Each phase restricts the move set to maintain the invariants of the previous phase.
"""

from typing import List

# Phase 0 (G0 → G1): Edge Orientation
# Goal: Orient all edges correctly
# Allowed moves: All 18 moves
PHASE_0_MOVES: List[str] = [
    'U', 'U\'', 'U2',
    'D', 'D\'', 'D2',
    'F', 'F\'', 'F2',
    'B', 'B\'', 'B2',
    'L', 'L\'', 'L2',
    'R', 'R\'', 'R2'
]

# Phase 1 (G1 → G2): Corner Orientation + E-slice Edges
# Goal: Orient all corners + place E-slice edges in E-slice
# Allowed moves: Remove F, F', B, B' (keep F2, B2)
# Reasoning: F and B quarter-turns change corner orientation
PHASE_1_MOVES: List[str] = [
    'U', 'U\'', 'U2',
    'D', 'D\'', 'D2',
    'F2',  # Only F2, no F or F'
    'B2',  # Only B2, no B or B'
    'L', 'L\'', 'L2',
    'R', 'R\'', 'R2'
]

# Phase 2 (G2 → G3): Tetrad Positioning + Edge Slicing
# Goal: Place corners in tetrads, edges in slices, fix parity
# Allowed moves: Remove L, L', R, R' (keep L2, R2)
# Reasoning: L and R quarter-turns move edges between slices
PHASE_2_MOVES: List[str] = [
    'U', 'U\'', 'U2',
    'D', 'D\'', 'D2',
    'F2',
    'B2',
    'L2',  # Only L2, no L or L'
    'R2',  # Only R2, no R or R'
]

# Phase 3 (G3 → G4): Final Solve
# Goal: Solve the entire cube
# Allowed moves: Only double moves (180° turns)
# Reasoning: These moves preserve all previous phase invariants
PHASE_3_MOVES: List[str] = [
    'U2',
    'D2',
    'F2',
    'B2',
    'L2',
    'R2'
]

# All phase moves in a list for easy access
ALL_PHASE_MOVES = [
    PHASE_0_MOVES,
    PHASE_1_MOVES,
    PHASE_2_MOVES,
    PHASE_3_MOVES
]


def get_phase_moves(phase: int) -> List[str]:
    """
    Get the allowed moves for a specific phase.

    Args:
        phase: Phase number (0-3)

    Returns:
        List of allowed move strings

    Raises:
        ValueError: If phase is not in range [0, 3]
    """
    if phase < 0 or phase >= len(ALL_PHASE_MOVES):
        raise ValueError(f"Phase must be 0-3, got {phase}")
    return ALL_PHASE_MOVES[phase]


def is_move_allowed(move: str, phase: int) -> bool:
    """
    Check if a move is allowed in a given phase.

    Args:
        move: Move string (e.g., 'U', 'R2', 'F\'')
        phase: Phase number (0-3)

    Returns:
        True if move is allowed in this phase
    """
    return move in get_phase_moves(phase)


# Move transition effects on coordinates
# These would be pre-computed and stored in transition tables

def affects_edge_orientation(move: str) -> bool:
    """
    Check if a move affects edge orientation.

    Only F, F', B, B', L, L', R, R' affect edge orientation.
    U, U', U2, D, D', D2 and all double moves preserve orientation.

    Args:
        move: Move string

    Returns:
        True if move affects edge orientation
    """
    base = move[0]
    modifier = move[1:] if len(move) > 1 else ''

    # F, B quarter turns affect orientation
    if base in ['F', 'B']:
        return modifier != '2'

    # L, R quarter turns affect orientation
    if base in ['L', 'R']:
        return modifier != '2'

    return False


def affects_corner_orientation(move: str) -> bool:
    """
    Check if a move affects corner orientation.

    Only F, F', B, B' affect corner orientation.

    Args:
        move: Move string

    Returns:
        True if move affects corner orientation
    """
    base = move[0]
    modifier = move[1:] if len(move) > 1 else ''

    # Only F, B quarter turns affect corner orientation
    return base in ['F', 'B'] and modifier != '2'


def affects_edge_slicing(move: str) -> bool:
    """
    Check if a move affects edge slicing (moves edges between slices).

    Only L, L', R, R' move edges between slices.

    Args:
        move: Move string

    Returns:
        True if move affects edge slicing
    """
    base = move[0]
    modifier = move[1:] if len(move) > 1 else ''

    # Only L, R quarter turns affect slicing
    return base in ['L', 'R'] and modifier != '2'


def affects_permutation_parity(move: str) -> bool:
    """
    Check if a move affects permutation parity.

    Only quarter turns (not double moves) affect parity.

    Args:
        move: Move string

    Returns:
        True if move affects parity
    """
    modifier = move[1:] if len(move) > 1 else ''
    return modifier != '2'  # Quarter turns affect parity


# Phase goal checking functions

def is_in_g1(edge_orientation_coord: int) -> bool:
    """Check if cube is in group G1 (all edges oriented)."""
    return edge_orientation_coord == 0


def is_in_g2(corner_orientation_coord: int, e_slice_coord: int) -> bool:
    """Check if cube is in group G2 (corners oriented, E-edges in E-slice)."""
    # Corner orientation must be 0, E-slice edges must be in E-slice
    # E-slice coord = 0 means all E-edges are in positions 8-11
    return corner_orientation_coord == 0 and e_slice_coord == 0


def is_in_g3(corner_tetrad_coord: int, edge_slice_coord: int) -> bool:
    """Check if cube is in group G3 (corners in tetrads, edges in slices)."""
    # This is simplified - full check requires verifying tetrad and slice invariants
    return corner_tetrad_coord == 0 and edge_slice_coord == 0


def is_solved(corner_perm_coord: int, edge_perm_coord: int) -> bool:
    """Check if cube is fully solved (G4)."""
    return corner_perm_coord == 0 and edge_perm_coord == 0
