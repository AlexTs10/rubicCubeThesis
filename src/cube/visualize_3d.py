"""
3D Visualization for Rubik's Cube using Matplotlib.

This module provides functions to visualize a Rubik's Cube in 3D
with interactive rotation capabilities.

Based on techniques similar to davidwhogg/MagicCube but simplified.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from typing import Optional, Tuple, List
from .rubik_cube import RubikCube, Face


# Color mapping for 3D visualization (RGB values)
COLOR_RGB = {
    0: [1.0, 1.0, 1.0],      # U - White
    1: [1.0, 1.0, 0.0],      # D - Yellow
    2: [0.0, 0.8, 0.0],      # F - Green
    3: [0.0, 0.0, 1.0],      # B - Blue
    4: [1.0, 0.5, 0.0],      # L - Orange
    5: [1.0, 0.0, 0.0],      # R - Red
}


def _create_sticker_polygon(center: np.ndarray, normal: np.ndarray,
                           size: float = 0.9) -> np.ndarray:
    """
    Create a square sticker (facelet) as a 3D polygon.

    Args:
        center: Center position of the sticker [x, y, z]
        normal: Normal vector indicating which face this is on
        size: Size of the sticker (0.9 leaves small gaps)

    Returns:
        Array of 4 corner points defining the square
    """
    # Determine which direction we're facing
    normal = np.array(normal)

    # Create perpendicular vectors for the square
    if abs(normal[2]) < 0.9:  # Not facing up/down
        up = np.array([0, 0, 1])
    else:
        up = np.array([1, 0, 0])

    # Create orthogonal basis
    right = np.cross(normal, up)
    right = right / np.linalg.norm(right)
    up = np.cross(right, normal)
    up = up / np.linalg.norm(up)

    # Create square corners
    d = size / 2
    corners = np.array([
        center + d * (-right - up),
        center + d * (right - up),
        center + d * (right + up),
        center + d * (-right + up)
    ])

    return corners


def _get_face_centers_and_normals(face: Face) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Get the 3D positions and normal vector for all 9 stickers of a face.

    Args:
        face: Face enum

    Returns:
        Tuple of (list of 9 center positions, normal vector)
    """
    centers = []
    offset = 1.5  # Distance from center to face

    if face == Face.U:  # Up (White) - top face
        normal = np.array([0, 0, 1])
        for i in range(3):
            for j in range(3):
                centers.append([j - 1, 1 - i, offset])

    elif face == Face.D:  # Down (Yellow) - bottom face
        normal = np.array([0, 0, -1])
        for i in range(3):
            for j in range(3):
                centers.append([j - 1, 1 - i, -offset])

    elif face == Face.F:  # Front (Green)
        normal = np.array([0, 1, 0])
        for i in range(3):
            for j in range(3):
                centers.append([j - 1, offset, 1 - i])

    elif face == Face.B:  # Back (Blue)
        normal = np.array([0, -1, 0])
        for i in range(3):
            for j in range(3):
                centers.append([j - 1, -offset, 1 - i])

    elif face == Face.L:  # Left (Orange)
        normal = np.array([-1, 0, 0])
        for i in range(3):
            for j in range(3):
                centers.append([-offset, 1 - j, 1 - i])

    elif face == Face.R:  # Right (Red)
        normal = np.array([1, 0, 0])
        for i in range(3):
            for j in range(3):
                centers.append([offset, j - 1, 1 - i])

    return centers, normal


def visualize_3d(cube: RubikCube, title: str = "Rubik's Cube - 3D View",
                figsize: Tuple[int, int] = (10, 10),
                elev: float = 20, azim: float = -60,
                show: bool = True) -> plt.Figure:
    """
    Create a 3D visualization of the Rubik's Cube.

    Args:
        cube: RubikCube instance to visualize
        title: Title for the plot
        figsize: Figure size
        elev: Elevation angle for viewing
        azim: Azimuth angle for viewing
        show: Whether to display the figure immediately

    Returns:
        Matplotlib figure object
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')

    # Draw each face
    for face in Face:
        face_state = cube.get_face(face)
        centers, normal = _get_face_centers_and_normals(face)

        # Draw each sticker on the face
        for i, (center, color_idx) in enumerate(zip(centers, face_state)):
            color = COLOR_RGB[color_idx]

            # Create sticker polygon
            corners = _create_sticker_polygon(np.array(center), normal, size=0.9)

            # Create polygon collection
            poly = Poly3DCollection([corners], alpha=1.0, linewidths=1.5,
                                   edgecolors='black')
            poly.set_facecolor(color)
            ax.add_collection3d(poly)

    # Set viewing parameters
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.view_init(elev=elev, azim=azim)

    # Set title
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Add status text
    status = "SOLVED" if cube.is_solved() else "SCRAMBLED"
    color = "green" if cube.is_solved() else "red"
    fig.text(0.5, 0.02, f"Status: {status}",
            ha='center', fontsize=12, color=color, fontweight='bold')

    # Make background white
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    if show:
        plt.show()

    return fig


def visualize_3d_interactive(cube: RubikCube, title: str = "Rubik's Cube - Interactive 3D") -> None:
    """
    Create an interactive 3D visualization that can be rotated with mouse.

    Args:
        cube: RubikCube instance to visualize
        title: Title for the plot
    """
    fig = visualize_3d(cube, title=title, show=False)

    # Add instructions
    fig.text(0.5, 0.95, "Click and drag to rotate the cube",
            ha='center', fontsize=10, style='italic')

    plt.show()


def visualize_3d_sequence(cube: RubikCube, moves: List[str],
                         figsize: Tuple[int, int] = (15, 10),
                         elev: float = 20, azim: float = -60) -> None:
    """
    Visualize a sequence of moves in 3D.

    Args:
        cube: Initial cube state
        moves: List of moves to apply
        figsize: Figure size
        elev: Elevation angle
        azim: Azimuth angle
    """
    n_states = min(len(moves) + 1, 8)  # Limit to 8 views
    cols = min(4, n_states)
    rows = (n_states + cols - 1) // cols

    fig = plt.figure(figsize=figsize)

    current_cube = cube.copy()

    # Initial state
    ax = fig.add_subplot(rows, cols, 1, projection='3d')
    _draw_cube_on_axis(ax, current_cube, "Initial", elev, azim)

    # Apply moves
    for i, move in enumerate(moves[:7]):  # Max 7 moves (8 states total)
        current_cube.apply_move(move)
        ax = fig.add_subplot(rows, cols, i + 2, projection='3d')
        _draw_cube_on_axis(ax, current_cube, f"After: {move}", elev, azim)

    plt.tight_layout()
    plt.show()


def _draw_cube_on_axis(ax: Axes3D, cube: RubikCube, title: str,
                      elev: float = 20, azim: float = -60) -> None:
    """
    Helper function to draw a cube on a specific axis.

    Args:
        ax: 3D axis to draw on
        cube: RubikCube to draw
        title: Title for this subplot
        elev: Elevation angle
        azim: Azimuth angle
    """
    # Draw each face
    for face in Face:
        face_state = cube.get_face(face)
        centers, normal = _get_face_centers_and_normals(face)

        # Draw each sticker
        for center, color_idx in zip(centers, face_state):
            color = COLOR_RGB[color_idx]
            corners = _create_sticker_polygon(np.array(center), normal, size=0.9)

            poly = Poly3DCollection([corners], alpha=1.0, linewidths=1,
                                   edgecolors='black')
            poly.set_facecolor(color)
            ax.add_collection3d(poly)

    # Set parameters
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10, fontweight='bold')

    # Make background white
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False


def save_3d_visualization(cube: RubikCube, filename: str,
                         title: str = "Rubik's Cube - 3D View",
                         elev: float = 20, azim: float = -60,
                         dpi: int = 150) -> None:
    """
    Save 3D cube visualization to a file.

    Args:
        cube: RubikCube instance to visualize
        filename: Output filename
        title: Title for the plot
        elev: Elevation angle
        azim: Azimuth angle
        dpi: DPI for output
    """
    fig = visualize_3d(cube, title=title, elev=elev, azim=azim, show=False)
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f"3D visualization saved to {filename}")
