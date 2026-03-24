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


def _missing_optional_dependency(feature_name: str, error: ModuleNotFoundError):
    """Return a callable that raises a clear optional-dependency error."""
    def _raiser(*args, **kwargs):
        raise ModuleNotFoundError(
            f"{feature_name} requires optional dependency {error.name!r}."
        ) from error

    return _raiser


try:
    from .visualize_2d import visualize_2d, visualize_2d_with_moves, save_visualization
except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional matplotlib
    visualize_2d = _missing_optional_dependency("2D visualization", exc)
    visualize_2d_with_moves = _missing_optional_dependency("2D visualization", exc)
    save_visualization = _missing_optional_dependency("2D visualization", exc)

try:
    from .visualize_3d import visualize_3d, visualize_3d_interactive, visualize_3d_sequence, save_3d_visualization
except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional matplotlib
    visualize_3d = _missing_optional_dependency("3D visualization", exc)
    visualize_3d_interactive = _missing_optional_dependency("3D visualization", exc)
    visualize_3d_sequence = _missing_optional_dependency("3D visualization", exc)
    save_3d_visualization = _missing_optional_dependency("3D visualization", exc)

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
