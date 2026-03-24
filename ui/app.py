"""
Rubik's Cube Solver - Interactive Web UI

Main Streamlit application for demonstrating and comparing three solving algorithms:
- Thistlethwaite's Algorithm (pure 4-phase solver, longer solutions)
- Kociemba's Algorithm (best overall practical compromise)
- Korf's IDA* (exact when solved, timeout-sensitive on hard cases)

Author: Alex Toska, University of Patras
Phase: 9 (Demos & UI Visualization)
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cube.rubik_cube import RubikCube

# Page configuration
st.set_page_config(
    page_title="Rubik's Cube Solver",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeeba;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application page."""

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎲 Rubik's Cube Solver - Interactive Demo</h1>
        <p>Alex Toska - University of Patras</p>
        <p>Comparing Three Classic Solving Algorithms</p>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message
    st.markdown("""
    ## Welcome to the Interactive Rubik's Cube Solver!

    This application demonstrates three different algorithms for solving the Rubik's Cube:

    ### 📊 Available Features

    Use the sidebar to navigate between different pages:

    1. **🎯 Single Solver** - Test individual algorithms
    2. **⚖️ Algorithm Comparison** - Compare all three algorithms side-by-side
    3. **📚 Educational Mode** - Learn how each algorithm works

    ### 🔍 Algorithm Overview

    | Algorithm | Speed Profile | Solution Length | Optimality | Memory |
    |-----------|---------------|-----------------|------------|--------|
    | **Thistlethwaite** | ⚡ Fast, predictable | Longer than the others | Not optimal | 💾 Low |
    | **Kociemba** | 🚀 Best practical trade-off | Near-optimal | Not guaranteed | 💾 Moderate |
    | **Korf IDA*** | 🐢 Variable, timeout-sensitive | Shortest when solved | Exact when solved | 💾 Highest |

    ### 🎮 Getting Started

    Choose a page from the sidebar to begin exploring!
    """)

    # Quick stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Fastest</h3>
            <p><strong>Thistlethwaite</strong></p>
            <p>Best for quick demos</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Most Efficient</h3>
            <p><strong>Kociemba</strong></p>
            <p>Best moves/time balance</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>✨ Most Optimal</h3>
            <p><strong>Korf IDA*</strong></p>
            <p>Exact on completed runs</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    ### 📖 About This Project

    This is part of a thesis project on Rubik's Cube solving algorithms at the University of Patras.
    The project implements and compares three seminal algorithms from computer science and
    artificial intelligence.

    **Phase 9: Demos & UI Visualization**
    Creating interactive demonstrations and educational materials to showcase the algorithms.
    """)

    # Technical info in expander
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        **Implementation Details:**
        - Language: Python 3.8+
        - UI Framework: Streamlit
        - Visualization: matplotlib (3D), seaborn (charts)
        - Testing Framework: Comprehensive Phase 8 evaluation

        **Algorithms:**
        1. **Thistlethwaite (1981)**: pure 4-phase group-theoretic approach
        2. **Kociemba (1992)**: 2-phase IDA* with the best overall practical benchmark profile
        3. **Korf (1997)**: external exact backend for benchmark runs, with exploratory heuristic code kept separately

        **References:**
        - Corrected thesis benchmark results
        - Integration with existing visualization modules
        - Standardized metric collection framework
        """)

if __name__ == "__main__":
    main()
