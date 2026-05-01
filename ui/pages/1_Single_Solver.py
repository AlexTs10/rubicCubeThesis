"""
Single Algorithm Solver Page

Test individual solving algorithms on scrambled cubes.
"""

import json
import streamlit as st
import streamlit.components.v1 as components
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
from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic
from src.korf.optimal_solver import KorfOptimalSolver, OPTIMAL_AVAILABLE

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


def _solve_thistlethwaite(cube: RubikCube, timeout: float):
    """Return a flat solution list from the pure Thistlethwaite solver."""
    solver = ThistlethwaiteSolver(
        use_pattern_databases=True,
        enable_kociemba_fallback=False,
    )
    result = solver.solve(cube, max_time=timeout, verbose=False)
    if not result:
        return None

    all_moves, _phase_moves, _used_fallback = result
    return all_moves


def _solve_kociemba(cube: RubikCube, timeout: float):
    """Return a flat solution list from the Kociemba solver."""
    solver = KociembaSolver()
    result = solver.solve(cube, timeout=timeout)
    if not result:
        return None

    solution, _phase1_moves, _phase2_moves = result
    return solution


def _solve_korf(cube: RubikCube, max_depth: int, timeout: float):
    """Return a flat solution list from the preferred Korf backend."""
    if OPTIMAL_AVAILABLE:
        solver = KorfOptimalSolver()
        result = solver.solve(cube, verbose=False, timeout=timeout)
        if not result:
            return None
        solution, _stats = result
        return solution

    heuristic = create_heuristic('composite', use_pattern_db=True)
    solver = IDAStarSolver(heuristic=heuristic, max_depth=max_depth, timeout=timeout)
    return solver.solve(cube)

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
    st.session_state.scramble_moves = []
    if scramble_method == "Random":
        st.session_state.scramble_moves = st.session_state.cube.scramble(moves=scramble_depth)
    elif scramble_method == "Custom Sequence":
        if custom_moves:
            moves = custom_moves.split()
            applied_moves = []
            for move in moves:
                try:
                    st.session_state.cube.apply_move(move)
                    applied_moves.append(move)
                except:
                    st.sidebar.error(f"Invalid move: {move}")
            st.session_state.scramble_moves = applied_moves
    elif scramble_method == "Seeded Random":
        st.session_state.scramble_moves = st.session_state.cube.scramble(moves=scramble_depth, seed=seed)

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
        - Pure 4-phase group-theoretic solver
        - 100% success on the thesis benchmark corpus
        - Typically longer solutions than Kociemba or Korf
        - No fallback in this page
        """)
        timeout = st.slider("Timeout (seconds)", 5, 60, 30)
    elif algorithm == "Kociemba":
        st.info("""
        **Kociemba's Algorithm (1992)**
        - 2-phase IDA* approach
        - 100% success on the thesis benchmark corpus
        - Near-optimal solutions
        - Strong default trade-off between quality and cost
        """)
        timeout = st.slider("Timeout (seconds)", 10, 120, 60)
    else:  # Korf IDA*
        if OPTIMAL_AVAILABLE:
            st.info("""
            **Korf's IDA* (1997)**
            - External exact backend is active on this page
            - Very fast on many shallow/mid-depth benchmark cases, but not a predictable default
            - Can still time out on hard depth-20 cases
            - Highest memory cost of the three solvers
            """)
            timeout = st.slider("Timeout (seconds)", 30, 300, 120)
            max_depth = 20
            st.caption("Max search depth is inactive while the external exact backend is available; timeout is the active control.")
        else:
            st.info("""
            **Korf's IDA* (1997)**
            - Internal heuristic IDA* fallback is active on this page
            - Useful for exploratory experiments, but not the canonical exact benchmark path
            - Can time out on harder scrambles and is not treated as generally admissible
            - Highest memory cost of the three solvers
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
                        result = _solve_thistlethwaite(st.session_state.cube.copy(), timeout=timeout)
                        if result:
                            solution = result
                            success = True
                        else:
                            success = False

                    elif algorithm == "Kociemba":
                        result = _solve_kociemba(st.session_state.cube.copy(), timeout=timeout)
                        if result:
                            solution = result
                            success = True
                        else:
                            success = False

                    else:  # Korf IDA*
                        result = _solve_korf(st.session_state.cube.copy(), max_depth=max_depth, timeout=timeout)
                        if result:
                            solution = result
                            success = True

                except Exception as e:
                    st.error(f"Error during solving: {str(e)}")
                    success = False

                elapsed_time = time.time() - start_time
                mem_after = process.memory_info().rss / 1024 / 1024
                mem_used = max(mem_after - mem_before, 0.0)

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

        solution_text = " ".join(st.session_state.solution_moves)
        components.html(
            f"""
            <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.5rem;">
              <button id="copy-solution-btn" style="
                background:#0f766e;
                color:white;
                border:none;
                border-radius:0.5rem;
                padding:0.5rem 0.9rem;
                cursor:pointer;
                font:inherit;
              ">Copy to Clipboard</button>
              <span id="copy-solution-status" style="font-size:0.9rem; color:#475569;"></span>
            </div>
            <script>
              const button = document.getElementById('copy-solution-btn');
              const status = document.getElementById('copy-solution-status');
              const solutionText = {json.dumps(solution_text)};
              button.addEventListener('click', async () => {{
                try {{
                  await navigator.clipboard.writeText(solutionText);
                  status.textContent = 'Copied';
                }} catch (error) {{
                  status.textContent = 'Copy failed';
                }}
              }});
            </script>
            """,
            height=72,
        )

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
