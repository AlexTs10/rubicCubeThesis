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

# Import UI components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.visualizer import show_3d_cube, show_side_by_side_cubes
from utils.session_state import init_session_state

# Page config
st.set_page_config(page_title="Algorithm Comparison", page_icon="⚖️", layout="wide")

# Initialize session state
init_session_state()

# Title
st.title("⚖️ Algorithm Comparison Mode")
st.markdown("Compare all three algorithms side-by-side on identical scrambles")

# Info box
st.info("""
💡 **Inspired by rubiks-cube-cracker**: This mode runs all three algorithms on the same scramble
and displays the results side-by-side for direct comparison.
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

# Timeout settings
st.sidebar.subheader("Timeout Settings")
thistle_timeout = st.sidebar.slider("Thistlethwaite (s)", 5, 60, 30)
kociemba_timeout = st.sidebar.slider("Kociemba (s)", 10, 120, 60)
korf_timeout = st.sidebar.slider("Korf IDA* (s)", 30, 300, 120)
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
    cube.scramble(moves=scramble_depth, seed=seed)
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
        if r.solved:
            st.success("✅ Solved")
            st.metric("Moves", r.solution_length)
            st.metric("Time", f"{r.time_seconds:.3f}s")
            st.metric("Memory", f"{r.memory_mb:.2f} MB")
            if r.nodes_explored:
                st.metric("Nodes", f"{r.nodes_explored:,}")
        else:
            st.error("❌ Failed")
            st.caption(r.reason_failed or "Timeout")

    with col2:
        st.markdown("### 🟢 Kociemba")
        r = result.kociemba
        if r.solved:
            st.success("✅ Solved")
            st.metric("Moves", r.solution_length)
            st.metric("Time", f"{r.time_seconds:.3f}s")
            st.metric("Memory", f"{r.memory_mb:.2f} MB")
            if r.nodes_explored:
                st.metric("Nodes", f"{r.nodes_explored:,}")
        else:
            st.error("❌ Failed")
            st.caption(r.reason_failed or "Timeout")

    with col3:
        st.markdown("### 🟣 Korf IDA*")
        r = result.korf
        if r.solved:
            st.success("✅ Solved")
            st.metric("Moves", r.solution_length)
            st.metric("Time", f"{r.time_seconds:.3f}s")
            st.metric("Memory", f"{r.memory_mb:.2f} MB")
            if r.nodes_explored:
                st.metric("Nodes", f"{r.nodes_explored:,}")
        else:
            st.error("❌ Failed")
            st.caption(r.reason_failed or "Timeout")

    # Comparison table
    st.markdown("---")
    st.subheader("📋 Detailed Comparison Table")

    data = []
    for name, algo_result in [
        ("Thistlethwaite", result.thistlethwaite),
        ("Kociemba", result.kociemba),
        ("Korf IDA*", result.korf)
    ]:
        if algo_result.solved:
            data.append({
                "Algorithm": name,
                "Solved": "✅",
                "Moves": algo_result.solution_length,
                "Time (s)": f"{algo_result.time_seconds:.3f}",
                "Memory (MB)": f"{algo_result.memory_mb:.2f}",
                "Nodes": algo_result.nodes_explored or "N/A"
            })
        else:
            data.append({
                "Algorithm": name,
                "Solved": "❌",
                "Moves": "-",
                "Time (s)": f"{algo_result.time_seconds:.3f}",
                "Memory (MB)": f"{algo_result.memory_mb:.2f}",
                "Nodes": "-"
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
        ("Korf IDA*", result.korf)
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
            winner = min(solved_results, key=lambda x: x[1].memory_mb)
            st.success(f"**Least Memory**\n\n{winner[0]}\n\n{winner[1].memory_mb:.2f} MB")

    # Solution sequences
    st.markdown("---")
    st.subheader("📝 Solution Sequences")

    for name, algo_result in [
        ("Thistlethwaite", result.thistlethwaite),
        ("Kociemba", result.kociemba),
        ("Korf IDA*", result.korf)
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
                    "memory": result.thistlethwaite.memory_mb
                },
                "kociemba": {
                    "solved": result.kociemba.solved,
                    "moves": result.kociemba.solution_length,
                    "time": result.kociemba.time_seconds,
                    "memory": result.kociemba.memory_mb
                },
                "korf": {
                    "solved": result.korf.solved,
                    "moves": result.korf.solution_length,
                    "time": result.korf.time_seconds,
                    "memory": result.korf.memory_mb
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
       - Thistlethwaite: Usually completes in <1s
       - Kociemba: Usually completes in 1-5s
       - Korf: Can take 1-60s depending on scramble
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
    - Korf may time out on scrambles >15 moves with default settings
    - Increase timeouts if you get failures
    """)

# Footer
st.markdown("---")
st.caption("Phase 9: Demos & UI | Alex Toska - University of Patras")
