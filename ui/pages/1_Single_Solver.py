"""
Single Algorithm Solver Page

Test individual solving algorithms on scrambled cubes.
"""

import streamlit as st
import sys
from pathlib import Path
import time
import psutil
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite import ThistlethwaiteSolver
from src.kociemba.solver import KociembaSolver
from src.kociemba.cubie import from_facelet_cube, to_facelet_cube
from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic

# Import UI components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.visualizer import show_3d_cube, show_2d_cube
from utils.session_state import init_session_state, reset_solve_state

# Page config
st.set_page_config(page_title="Single Solver", page_icon="🎯", layout="wide")

# Initialize session state
init_session_state()

# Title
st.title("🎯 Single Algorithm Solver")
st.markdown("Test individual algorithms on scrambled cubes")

# Sidebar controls
st.sidebar.header("Configuration")

# Algorithm selection
algorithm = st.sidebar.selectbox(
    "Select Algorithm",
    ["Thistlethwaite", "Kociemba", "Korf IDA*"],
    help="Choose which algorithm to use for solving"
)

# Scramble configuration
st.sidebar.subheader("Scramble Settings")

scramble_method = st.sidebar.radio(
    "Scramble Method",
    ["Random", "Custom Sequence", "Seeded Random"]
)

if scramble_method == "Random":
    scramble_depth = st.sidebar.slider(
        "Scramble Depth",
        min_value=5,
        max_value=25,
        value=10,
        help="Number of random moves to scramble"
    )
elif scramble_method == "Custom Sequence":
    custom_moves = st.sidebar.text_input(
        "Enter move sequence",
        placeholder="e.g., R U R' U' F2",
        help="Space-separated moves (U, D, F, B, L, R, with ' for inverse, 2 for double)"
    )
elif scramble_method == "Seeded Random":
    seed = st.sidebar.number_input(
        "Random Seed",
        min_value=0,
        value=42,
        help="Seed for reproducible scrambles"
    )
    scramble_depth = st.sidebar.slider(
        "Scramble Depth",
        min_value=5,
        max_value=25,
        value=10
    )

# Solve button
if st.sidebar.button("🎲 Generate New Scramble", use_container_width=True):
    reset_solve_state()
    st.session_state.cube = RubikCube()

    if scramble_method == "Random":
        st.session_state.cube.scramble(n_moves=scramble_depth)
        st.session_state.scramble_moves = getattr(st.session_state.cube, '_scramble_moves', [])
    elif scramble_method == "Custom Sequence":
        if custom_moves:
            moves = custom_moves.split()
            for move in moves:
                try:
                    st.session_state.cube.apply_move(move)
                except:
                    st.sidebar.error(f"Invalid move: {move}")
            st.session_state.scramble_moves = moves
    elif scramble_method == "Seeded Random":
        import random
        random.seed(seed)
        st.session_state.cube.scramble(n_moves=scramble_depth, seed=seed)
        st.session_state.scramble_moves = getattr(st.session_state.cube, '_scramble_moves', [])

    st.rerun()

# Reset button
if st.sidebar.button("🔄 Reset Cube", use_container_width=True):
    st.session_state.cube = RubikCube()
    reset_solve_state()
    st.session_state.scramble_moves = []
    st.rerun()

st.sidebar.markdown("---")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Current Cube State")
    if st.session_state.cube.is_solved():
        st.success("✅ Cube is solved!")
    else:
        st.info("🎲 Cube is scrambled")

    # Show 3D visualization
    show_3d_cube(st.session_state.cube, title="Current State")

    # Show scramble info
    if st.session_state.scramble_moves:
        with st.expander("📋 Scramble Sequence"):
            st.code(" ".join(st.session_state.scramble_moves))
            st.caption(f"Scramble depth: {len(st.session_state.scramble_moves)} moves")

with col2:
    st.subheader("Solve Configuration")

    # Algorithm info
    if algorithm == "Thistlethwaite":
        st.info("""
        **Thistlethwaite's Algorithm (1981)**
        - 4-phase group-theoretic approach
        - Fast: 0.2-0.5 seconds
        - Solution: 30-52 moves
        - Memory: ~2 MB
        """)
        timeout = st.slider("Timeout (seconds)", 5, 60, 30)
    elif algorithm == "Kociemba":
        st.info("""
        **Kociemba's Algorithm (1992)**
        - 2-phase IDA* approach
        - Medium: 1-3 seconds
        - Solution: <19 moves
        - Memory: ~80 MB
        """)
        timeout = st.slider("Timeout (seconds)", 10, 120, 60)
    else:  # Korf IDA*
        st.info("""
        **Korf's IDA* (1997)**
        - Pattern database heuristic search
        - Variable: 1-30+ seconds
        - Solution: ≤20 moves (optimal)
        - Memory: ~45 MB
        """)
        timeout = st.slider("Timeout (seconds)", 30, 300, 120)
        max_depth = st.slider("Max Search Depth", 10, 25, 20)

    # Solve button
    if st.button("🚀 Solve Cube", type="primary", use_container_width=True):
        if st.session_state.cube.is_solved():
            st.warning("Cube is already solved!")
        else:
            with st.spinner(f"Solving with {algorithm}..."):
                process = psutil.Process(os.getpid())
                mem_before = process.memory_info().rss / 1024 / 1024

                start_time = time.time()
                solution = None
                success = False

                try:
                    if algorithm == "Thistlethwaite":
                        solver = ThistlethwaiteSolver(use_pattern_databases=False)
                        solution = solver.solve(st.session_state.cube.copy())
                        success = True

                    elif algorithm == "Kociemba":
                        solver = KociembaSolver()
                        cubie = from_facelet_cube(st.session_state.cube)
                        solution = solver.solve(cubie, timeout=timeout)
                        success = solution is not None

                    else:  # Korf IDA*
                        heuristic = create_heuristic('composite')
                        solver = IDAStarSolver(heuristic=heuristic, max_depth=max_depth, timeout=timeout)
                        result = solver.solve(st.session_state.cube.copy())
                        if result:
                            solution = result['moves']
                            success = True

                except Exception as e:
                    st.error(f"Error during solving: {str(e)}")
                    success = False

                elapsed_time = time.time() - start_time
                mem_after = process.memory_info().rss / 1024 / 1024
                mem_used = mem_after - mem_before

                if success and solution:
                    st.session_state.solution_moves = solution
                    st.session_state.solve_time = elapsed_time
                    st.session_state.algorithm_used = algorithm
                    st.session_state.memory_used = mem_used
                    st.rerun()
                else:
                    st.error(f"Failed to find solution within {timeout} seconds")

# Display solution if available
if st.session_state.solution_moves and st.session_state.algorithm_used:
    st.markdown("---")
    st.subheader("✅ Solution Found!")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Algorithm", st.session_state.algorithm_used)
    col2.metric("Solution Length", f"{len(st.session_state.solution_moves)} moves")
    col3.metric("Time", f"{st.session_state.solve_time:.3f}s")
    col4.metric("Memory", f"{st.session_state.memory_used:.2f} MB")

    # Solution sequence
    with st.expander("📋 Solution Sequence", expanded=True):
        st.code(" ".join(st.session_state.solution_moves))

        # Copy button
        if st.button("📋 Copy to Clipboard"):
            st.code(" ".join(st.session_state.solution_moves))

    # Animation controls
    st.subheader("🎬 Solution Animation")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        move_index = st.slider(
            "Move Progress",
            0,
            len(st.session_state.solution_moves),
            0,
            help="Slide to see the cube state after each move"
        )

    # Show cube state at selected move
    cube_at_move = st.session_state.cube.copy()
    for i in range(move_index):
        if i < len(st.session_state.solution_moves):
            cube_at_move.apply_move(st.session_state.solution_moves[i])

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        show_3d_cube(
            cube_at_move,
            title=f"After {move_index}/{len(st.session_state.solution_moves)} moves"
        )

    if move_index < len(st.session_state.solution_moves):
        st.caption(f"Next move: **{st.session_state.solution_moves[move_index]}**")
    elif move_index == len(st.session_state.solution_moves):
        st.success("✅ Cube solved!")

# Footer
st.markdown("---")
st.caption("Phase 9: Demos & UI | Alex Toska - University of Patras")
