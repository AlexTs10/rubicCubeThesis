"""
2D Visualization for Rubik's Cube using Matplotlib.

This module provides functions to visualize a Rubik's Cube as a 2D net
(unfolded cube layout) using matplotlib.

The layout follows the standard cross pattern:
       U
     L F R B
       D
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Optional, Tuple
from .rubik_cube import RubikCube, Face, FACE_COLORS


# Color mapping for visualization
COLOR_MAP = {
    0: '#FFFFFF',  # U - White
    1: '#FFFF00',  # D - Yellow
    2: '#00FF00',  # F - Green
    3: '#0000FF',  # B - Blue
    4: '#FF8000',  # L - Orange
    5: '#FF0000',  # R - Red
}


def draw_face(ax: plt.Axes, face_state: np.ndarray, x_offset: float,
              y_offset: float, size: float = 1.0) -> None:
    """
    Draw a single face of the cube as a 3x3 grid.

    Args:
        ax: Matplotlib axes to draw on
        face_state: 9-element array representing the face
        x_offset: X position offset
        y_offset: Y position offset
        size: Size of each facelet (default 1.0)
    """
    for i in range(3):
        for j in range(3):
            idx = i * 3 + j
            color_idx = face_state[idx]
            color = COLOR_MAP[color_idx]

            # Draw facelet rectangle
            rect = patches.Rectangle(
                (x_offset + j * size, y_offset + (2 - i) * size),
                size, size,
                linewidth=2,
                edgecolor='black',
                facecolor=color
            )
            ax.add_patch(rect)


def visualize_2d(cube: RubikCube, title: str = "Rubik's Cube",
                 figsize: Tuple[int, int] = (12, 9),
                 show: bool = True) -> plt.Figure:
    """
    Visualize a Rubik's Cube as a 2D net.

    The layout is:
           U
         L F R B
           D

    Args:
        cube: RubikCube instance to visualize
        title: Title for the plot
        figsize: Figure size (width, height)
        show: Whether to display the figure immediately

    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect('equal')
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis('off')

    # Set title
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    # Size of each facelet
    size = 1.0

    # Draw faces in cross pattern
    # U face at top center
    draw_face(ax, cube.get_face(Face.U), 3, 6, size)

    # Middle row: L F R B
    draw_face(ax, cube.get_face(Face.L), 0, 3, size)
    draw_face(ax, cube.get_face(Face.F), 3, 3, size)
    draw_face(ax, cube.get_face(Face.R), 6, 3, size)
    draw_face(ax, cube.get_face(Face.B), 9, 3, size)

    # D face at bottom center
    draw_face(ax, cube.get_face(Face.D), 3, 0, size)

    # Add face labels
    label_props = dict(fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(4.5, 8.7, 'U', **label_props)
    ax.text(1.5, 5.7, 'L', **label_props)
    ax.text(4.5, 5.7, 'F', **label_props)
    ax.text(7.5, 5.7, 'R', **label_props)
    ax.text(10.5, 5.7, 'B', **label_props)
    ax.text(4.5, -0.3, 'D', **label_props)

    # Add solved status indicator
    status_text = "SOLVED" if cube.is_solved() else "SCRAMBLED"
    status_color = "green" if cube.is_solved() else "red"
    ax.text(6, -1, f"Status: {status_text}",
            fontsize=12, ha='left', color=status_color, fontweight='bold')

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def visualize_2d_with_moves(cube: RubikCube, moves: list,
                           figsize: Tuple[int, int] = (15, 10)) -> None:
    """
    Visualize a cube and show the effect of a sequence of moves.

    Args:
        cube: Initial RubikCube state
        moves: List of moves to apply and visualize
        figsize: Figure size
    """
    # Calculate number of subplots needed
    n_states = len(moves) + 1
    cols = min(4, n_states)
    rows = (n_states + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(figsize[0], figsize[1] * rows / 2))
    if n_states == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    # Initial state
    current_cube = cube.copy()
    ax = axes[0]
    ax.set_aspect('equal')
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis('off')
    ax.set_title("Initial State", fontsize=12, fontweight='bold')

    # Draw initial state
    size = 0.8
    draw_face(ax, current_cube.get_face(Face.U), 3, 6, size)
    draw_face(ax, current_cube.get_face(Face.L), 0, 3, size)
    draw_face(ax, current_cube.get_face(Face.F), 3, 3, size)
    draw_face(ax, current_cube.get_face(Face.R), 6, 3, size)
    draw_face(ax, current_cube.get_face(Face.B), 9, 3, size)
    draw_face(ax, current_cube.get_face(Face.D), 3, 0, size)

    # Apply moves one by one
    for i, move in enumerate(moves):
        current_cube.apply_move(move)
        ax = axes[i + 1]
        ax.set_aspect('equal')
        ax.set_xlim(-0.5, 12.5)
        ax.set_ylim(-0.5, 9.5)
        ax.axis('off')
        ax.set_title(f"After: {move}", fontsize=12, fontweight='bold')

        # Draw current state
        draw_face(ax, current_cube.get_face(Face.U), 3, 6, size)
        draw_face(ax, current_cube.get_face(Face.L), 0, 3, size)
        draw_face(ax, current_cube.get_face(Face.F), 3, 3, size)
        draw_face(ax, current_cube.get_face(Face.R), 6, 3, size)
        draw_face(ax, current_cube.get_face(Face.B), 9, 3, size)
        draw_face(ax, current_cube.get_face(Face.D), 3, 0, size)

    # Hide unused subplots
    for i in range(n_states, len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    plt.show()


def save_visualization(cube: RubikCube, filename: str,
                       title: str = "Rubik's Cube",
                       figsize: Tuple[int, int] = (12, 9),
                       dpi: int = 150) -> None:
    """
    Save cube visualization to a file.

    Args:
        cube: RubikCube instance to visualize
        filename: Output filename (e.g., 'cube.png')
        title: Title for the plot
        figsize: Figure size
        dpi: DPI for the output image
    """
    fig = visualize_2d(cube, title=title, figsize=figsize, show=False)
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f"Visualization saved to {filename}")
