"""
Visualization components for the Streamlit UI.

Provides 3D and 2D cube visualization using existing visualization modules.
"""

import matplotlib.pyplot as plt
import streamlit as st
import sys
from pathlib import Path
from io import BytesIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cube.rubik_cube import RubikCube
from src.cube.visualization import display_cube_unfolded
from src.cube.visualize_3d import visualize_cube_3d


def show_3d_cube(cube: RubikCube, title: str = "Cube State", view_angles: tuple = (30, 45)):
    """
    Display a 3D visualization of the cube.

    Args:
        cube: RubikCube to visualize
        title: Title for the visualization
        view_angles: Tuple of (elevation, azimuth) viewing angles
    """
    fig = visualize_cube_3d(cube, view_angles=view_angles)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    st.pyplot(fig)
    plt.close(fig)


def show_2d_cube(cube: RubikCube, colored: bool = True):
    """
    Display a 2D unfolded net of the cube.

    Args:
        cube: RubikCube to visualize
        colored: Whether to use colored terminal output
    """
    display_str = display_cube_unfolded(cube, colored=colored)
    st.text(display_str)


def get_cube_image(cube: RubikCube, view_angles: tuple = (30, 45)) -> BytesIO:
    """
    Generate a cube image as bytes for export.

    Args:
        cube: RubikCube to visualize
        view_angles: Tuple of (elevation, azimuth) viewing angles

    Returns:
        BytesIO object containing the PNG image
    """
    fig = visualize_cube_3d(cube, view_angles=view_angles)

    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def show_side_by_side_cubes(cubes: list, titles: list, view_angles: tuple = (30, 45)):
    """
    Display multiple cubes side by side.

    Args:
        cubes: List of RubikCube objects
        titles: List of titles for each cube
        view_angles: Tuple of (elevation, azimuth) viewing angles
    """
    cols = st.columns(len(cubes))

    for col, cube, title in zip(cols, cubes, titles):
        with col:
            fig = visualize_cube_3d(cube, view_angles=view_angles)
            fig.suptitle(title, fontsize=12, fontweight='bold')
            st.pyplot(fig)
            plt.close(fig)


def create_animation_frames(cube: RubikCube, moves: list) -> list:
    """
    Create animation frames by applying moves sequentially.

    Args:
        cube: Initial RubikCube state
        moves: List of moves to apply

    Returns:
        List of RubikCube states (one per move)
    """
    frames = [cube.copy()]
    current_cube = cube.copy()

    for move in moves:
        current_cube.apply_move(move)
        frames.append(current_cube.copy())

    return frames
