"""
Algorithm Comparison Page

Side-by-side comparison of all three algorithms.
Inspired by rubiks-cube-cracker's F1/F2 comparison feature.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cube.rubik_cube import RubikCube
from src.evaluation.algorithm_comparison import AlgorithmComparison
from src.korf.optimal_solver import OPTIMAL_AVAILABLE

# Import UI components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.visualizer import show_3d_cube, show_side_by_side_cubes
from utils.session_state import init_session_state


def _backend_label(algo_result) -> str:
    """Human-readable backend label for tables and captions."""
    labels = {
        "thistlethwaite_native": "native pure solver",
        "kociemba_internal": "internal two-phase solver",
        "kociemba_native": "native two-phase solver",
        "optimal_external": "external optimal backend",
        "heuristic_ida_star": "internal heuristic IDA*",
    }
    return labels.get(algo_result.backend or "", algo_result.backend or "n/a")


def _optimality_label(algo_result) -> str:
    """Human-readable optimality label."""
    if algo_result.optimal_guaranteed is True:
        return "Exact when solved"
    if algo_result.optimal_guaranteed is False:
        return "Not guaranteed"
    return "Unknown"


def _format_memory_mb(value) -> str:
    """Format optional memory deltas for Streamlit tables."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


# Page config
st.set_page_config(page_title="Algorithm Comparison", page_icon="⚖️", layout="wide")

# Initialize session state
init_session_state()

# Title
st.title("⚖️ Algorithm Comparison Mode")
st.markdown("Compare all three algorithms side-by-side on identical scrambles")

# Info box
st.info("""
💡 This mode runs the repository's current benchmark paths on the same scramble:
pure Thistlethwaite, Kociemba, and the configured Korf backend.
""")

# Sidebar controls
st.sidebar.header("Comparison Configuration")

# Scramble settings
scramble_depth = st.sidebar.slider(
    "Scramble Depth",
    min_value=5,
    max_value=20,
    value=10,
    help="Number of random moves (deeper = harder)"
)

seed = st.sidebar.number_input(
    "Random Seed",
    min_value=0,
    value=42,
    help="For reproducible results"
)
scramble_policy = st.sidebar.selectbox(
    "Scramble Policy",
    options=[
        "Benchmark-style: no consecutive same-face moves",
        "Legacy demo: redundant moves allowed",
    ],
    help="Benchmark-style mode matches the current generator; legacy mode preserves older demo behavior.",
)

# Timeout settings
st.sidebar.subheader("Timeout Settings")
thistle_timeout = st.sidebar.slider("Thistlethwaite (s)", 5, 60, 30)
kociemba_timeout = st.sidebar.slider("Kociemba (s)", 10, 120, 60)
korf_timeout = st.sidebar.slider("Korf Exact / IDA* (s)", 30, 300, 120)
korf_max_depth = 20
if OPTIMAL_AVAILABLE:
    st.sidebar.slider(
        "Korf Max Depth (fallback only)",
        10,
        25,
        korf_max_depth,
        disabled=True,
        help="Only used when the internal heuristic Korf fallback is active.",
    )
    st.sidebar.caption("External exact backend detected. Timeout is active; max depth is ignored in this configuration.")
else:
    korf_max_depth = st.sidebar.slider("Korf Max Depth", 10, 25, 20)

# Comparison button
if st.sidebar.button("🚀 Run Comparison", type="primary", use_container_width=True):
    st.session_state.comparison_running = True

# Reset button
if st.sidebar.button("🔄 Reset", use_container_width=True):
    st.session_state.comparison_results = None
    st.session_state.comparison_running = False
    st.rerun()

# Run comparison
if 'comparison_running' in st.session_state and st.session_state.comparison_running:
    st.markdown("---")
    st.subheader("🔬 Running Comparison Test")

    # Create scramble
    cube = RubikCube()
    cube.scramble(
        moves=scramble_depth,
        seed=seed,
        allow_redundant=scramble_policy.startswith("Legacy"),
    )
    scramble_moves = getattr(cube, '_scramble_moves', [])

    # Show scrambled cube
    with st.expander("📋 Scramble Sequence", expanded=False):
        st.code(" ".join(scramble_moves))

    # Initialize comparison framework
    with st.spinner("Initializing solvers..."):
        comparison = AlgorithmComparison(
            thistlethwaite_timeout=thistle_timeout,
            kociemba_timeout=kociemba_timeout,
            korf_timeout=korf_timeout,
            korf_max_depth=korf_max_depth
        )

    # Progress indicators
    progress_text = st.empty()
    progress_bar = st.progress(0)

    # Run each algorithm
    progress_text.text("Testing Thistlethwaite...")
    progress_bar.progress(0)

    result = comparison.compare_on_scramble(cube, scramble_id=0)

    progress_text.text("Comparison complete!")
    progress_bar.progress(100)

    # Store results
    st.session_state.comparison_results = result
    st.session_state.comparison_running = False
    st.rerun()

# Display results
if st.session_state.comparison_results:
    result = st.session_state.comparison_results

    st.markdown("---")
    st.subheader("📊 Comparison Results")

    # Side-by-side metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔵 Thistlethwaite")
        r = result.thistlethwaite
        st.caption("Pure 4-phase solver with pattern databases; no fallback.")
        if r.solved:
            st.success("✅ Solved")
            st.metric("Moves", r.solution_length)
            st.metric("Time", f"{r.time_seconds:.3f}s")
            st.metric("Memory", f"{_format_memory_mb(r.memory_mb)} MB" if r.memory_mb is not None else "N/A")
            if r.nodes_explored:
                st.metric("Nodes", f"{r.nodes_explored:,}")
        else:
            st.error("❌ Failed")
            st.caption(r.reason_failed or "Timeout")

    with col2:
        st.markdown("### 🟢 Kociemba")
        r = result.kociemba
        st.caption("Best overall practical compromise in the thesis benchmark.")
        if r.solved:
            st.success("✅ Solved")
            st.metric("Moves", r.solution_length)
            st.metric("Time", f"{r.time_seconds:.3f}s")
            st.metric("Memory", f"{_format_memory_mb(r.memory_mb)} MB" if r.memory_mb is not None else "N/A")
            if r.nodes_explored:
                st.metric("Nodes", f"{r.nodes_explored:,}")
        else:
            st.error("❌ Failed")
            st.caption(r.reason_failed or "Timeout")

    with col3:
        st.markdown("### 🟣 Korf")
        r = result.korf
        st.caption(
            "External optimal backend when available; fast on many shallow/mid-depth solved cases, "
            "but hard requested scramble length 20 scrambles can still time out."
        )
        if r.solved:
            st.success("✅ Solved")
            st.metric("Moves", r.solution_length)
            st.metric("Time", f"{r.time_seconds:.3f}s")
            st.metric("Memory", f"{_format_memory_mb(r.memory_mb)} MB" if r.memory_mb is not None else "N/A")
            if r.nodes_explored:
                st.metric("Nodes", f"{r.nodes_explored:,}")
            st.caption(f"Backend: {_backend_label(r)} | {_optimality_label(r)}")
        else:
            st.error("❌ Failed")
            st.caption(
                f"{r.reason_failed or 'Timeout'} | "
                f"Backend: {_backend_label(r)} | {_optimality_label(r)}"
            )

    # Comparison table
    st.markdown("---")
    st.subheader("📋 Detailed Comparison Table")

    data = []
    for name, algo_result in [
        ("Thistlethwaite", result.thistlethwaite),
        ("Kociemba", result.kociemba),
        ("Korf", result.korf)
    ]:
        if algo_result.solved:
            data.append({
                "Algorithm": name,
                "Solved": "✅",
                "Moves": algo_result.solution_length,
                "Time (s)": f"{algo_result.time_seconds:.3f}",
                "Memory (MB)": _format_memory_mb(algo_result.memory_mb),
                "Nodes": algo_result.nodes_explored or "N/A",
                "Backend": _backend_label(algo_result),
                "Optimality": _optimality_label(algo_result),
            })
        else:
            data.append({
                "Algorithm": name,
                "Solved": "❌",
                "Moves": "-",
                "Time (s)": f"{algo_result.time_seconds:.3f}",
                "Memory (MB)": _format_memory_mb(algo_result.memory_mb),
                "Nodes": "-",
                "Backend": _backend_label(algo_result),
                "Optimality": _optimality_label(algo_result),
            })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Winner analysis
    st.markdown("---")
    st.subheader("🏆 Winner Analysis")

    col1, col2, col3 = st.columns(3)

    # Find winners
    solved_results = [
        ("Thistlethwaite", result.thistlethwaite),
        ("Kociemba", result.kociemba),
        ("Korf", result.korf)
    ]
    solved_results = [(name, r) for name, r in solved_results if r.solved]

    if solved_results:
        # Fewest moves
        with col1:
            winner = min(solved_results, key=lambda x: x[1].solution_length)
            st.success(f"**Fewest Moves**\n\n{winner[0]}\n\n{winner[1].solution_length} moves")

        # Fastest time
        with col2:
            winner = min(solved_results, key=lambda x: x[1].time_seconds)
            st.success(f"**Fastest**\n\n{winner[0]}\n\n{winner[1].time_seconds:.3f}s")

        # Least memory
        with col3:
            memory_results = [item for item in solved_results if item[1].memory_mb is not None]
            if memory_results:
                winner = min(memory_results, key=lambda x: x[1].memory_mb)
                st.success(f"**Least Memory**\n\n{winner[0]}\n\n{winner[1].memory_mb:.2f} MB")
            else:
                st.info("**Least Memory**\n\nN/A")

    # Solution sequences
    st.markdown("---")
    st.subheader("📝 Solution Sequences")

    for name, algo_result in [
        ("Thistlethwaite", result.thistlethwaite),
        ("Kociemba", result.kociemba),
        ("Korf", result.korf)
    ]:
        if algo_result.solved and algo_result.solution_moves:
            with st.expander(f"{name} Solution ({algo_result.solution_length} moves)"):
                st.code(" ".join(algo_result.solution_moves))

    # Export results
    st.markdown("---")
    st.subheader("💾 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        # Export as JSON
        import json
        from datetime import datetime

        export_data = {
            "timestamp": datetime.now().isoformat(),
            "scramble_depth": result.scramble_depth,
            "scramble_moves": result.scramble_moves,
            "results": {
                "thistlethwaite": {
                    "solved": result.thistlethwaite.solved,
                    "moves": result.thistlethwaite.solution_length,
                    "time": result.thistlethwaite.time_seconds,
                    "memory": result.thistlethwaite.memory_mb,
                    "backend": result.thistlethwaite.backend,
                    "optimal_guaranteed": result.thistlethwaite.optimal_guaranteed,
                },
                "kociemba": {
                    "solved": result.kociemba.solved,
                    "moves": result.kociemba.solution_length,
                    "time": result.kociemba.time_seconds,
                    "memory": result.kociemba.memory_mb,
                    "backend": result.kociemba.backend,
                    "optimal_guaranteed": result.kociemba.optimal_guaranteed,
                },
                "korf": {
                    "solved": result.korf.solved,
                    "moves": result.korf.solution_length,
                    "time": result.korf.time_seconds,
                    "memory": result.korf.memory_mb,
                    "backend": result.korf.backend,
                    "optimal_guaranteed": result.korf.optimal_guaranteed,
                    "nodes_explored": result.korf.nodes_explored,
                    "reason_failed": result.korf.reason_failed,
                }
            }
        }

        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name="comparison_results.json",
            mime="application/json"
        )

    with col2:
        # Export as CSV
        st.download_button(
            label="📥 Download CSV",
            data=df.to_csv(index=False),
            file_name="comparison_results.csv",
            mime="text/csv"
        )

# Help section
with st.expander("❓ Help & Tips"):
    st.markdown("""
    ### How to Use

    1. **Configure scramble**: Set scramble depth (5-20 moves recommended)
    2. **Set timeouts**: Adjust based on your patience level
       - Thistlethwaite: Pure 4-phase solver; usually fast, but solutions are long
       - Kociemba: Best overall practical compromise in the thesis benchmark
       - Korf: Exact on solved cases with the external backend, but requested scramble length 20 cases can still time out
    3. **Run comparison**: Click "Run Comparison" and wait
    4. **Analyze results**: Compare metrics and solution quality

    ### Understanding the Metrics

    - **Moves**: Number of moves in the solution (lower is better)
    - **Time**: How long the algorithm took to find the solution
    - **Memory**: RAM used during solving
    - **Nodes**: Search tree nodes explored (if applicable)

    ### Tips

    - Start with shallow scrambles (7-10 moves) to get quick results
    - Use the same seed to reproduce exact comparisons
    - Thistlethwaite on this page is pure and does not fall back to Kociemba
    - The Korf max-depth control matters only when the comparison falls back to the internal heuristic IDA* path
    - In the thesis benchmark, Korf timed out on 3 of 25 requested scramble length 20 scrambles with a 120s limit
    - If Korf fails here, check the backend column in the results table before drawing conclusions
    """)

# Footer
st.markdown("---")
st.caption("Phase 9: Demos & UI | Alex Toska - University of Patras")
