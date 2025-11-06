"""
Rubik's Cube module.

This module provides the core Rubik's Cube representation, moves, and visualization.
"""

from .rubik_cube import RubikCube, Face, Color, FACE_COLORS
from .moves import (
    BASIC_MOVES, ALL_MOVES,
    inverse_move, inverse_sequence,
    parse_move_sequence, format_move_sequence,
    simplify_moves, count_moves, are_opposite_faces
)
from .visualize_2d import visualize_2d, visualize_2d_with_moves, save_visualization
from .visualize_3d import visualize_3d, visualize_3d_interactive, visualize_3d_sequence, save_3d_visualization

__all__ = [
    # Core classes
    'RubikCube', 'Face', 'Color', 'FACE_COLORS',
    # Move utilities
    'BASIC_MOVES', 'ALL_MOVES',
    'inverse_move', 'inverse_sequence',
    'parse_move_sequence', 'format_move_sequence',
    'simplify_moves', 'count_moves', 'are_opposite_faces',
    # 2D visualization
    'visualize_2d', 'visualize_2d_with_moves', 'save_visualization',
    # 3D visualization
    'visualize_3d', 'visualize_3d_interactive', 'visualize_3d_sequence', 'save_3d_visualization',
]
