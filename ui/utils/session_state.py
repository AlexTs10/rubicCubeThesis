"""
Session state management for Streamlit UI.

Manages persistent state across page reloads and interactions.
"""

import streamlit as st
from typing import Optional, List
from src.cube.rubik_cube import RubikCube


def init_session_state():
    """Initialize all session state variables."""

    # Scramble state
    if 'cube' not in st.session_state:
        st.session_state.cube = RubikCube()

    if 'scramble_moves' not in st.session_state:
        st.session_state.scramble_moves = []

    if 'scramble_depth' not in st.session_state:
        st.session_state.scramble_depth = 10

    # Solve state
    if 'solution_moves' not in st.session_state:
        st.session_state.solution_moves = []

    if 'solve_time' not in st.session_state:
        st.session_state.solve_time = 0.0

    if 'algorithm_used' not in st.session_state:
        st.session_state.algorithm_used = None

    # Comparison state
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None

    # Animation state
    if 'animation_index' not in st.session_state:
        st.session_state.animation_index = 0

    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False


def reset_solve_state():
    """Reset solution-related state variables."""
    st.session_state.solution_moves = []
    st.session_state.solve_time = 0.0
    st.session_state.algorithm_used = None
    st.session_state.animation_index = 0
    st.session_state.is_playing = False


def reset_all_state():
    """Reset all state variables to defaults."""
    st.session_state.cube = RubikCube()
    st.session_state.scramble_moves = []
    st.session_state.scramble_depth = 10
    reset_solve_state()
    st.session_state.comparison_results = None


def get_cube() -> RubikCube:
    """Get the current cube state."""
    return st.session_state.cube


def set_cube(cube: RubikCube):
    """Set a new cube state."""
    st.session_state.cube = cube


def get_scramble_moves() -> List[str]:
    """Get the current scramble sequence."""
    return st.session_state.scramble_moves


def set_scramble_moves(moves: List[str]):
    """Set a new scramble sequence."""
    st.session_state.scramble_moves = moves
