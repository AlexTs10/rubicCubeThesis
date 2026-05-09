"""
Educational Mode Page

Learn about how each algorithm works with explanations and examples.
"""

import streamlit as st
import sys
from pathlib import Path

# Page config
st.set_page_config(page_title="Educational Mode", page_icon="📚", layout="wide")

# Title
st.title("📚 Educational Mode")
st.markdown("Learn how each algorithm solves the Rubik's Cube")

# Algorithm selection tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Overview",
    "🔵 Thistlethwaite",
    "🟢 Kociemba",
    "🟣 Korf IDA*"
])

with tab1:
    st.header("Rubik's Cube Solving Algorithms")

    st.markdown("""
    This project implements and compares three seminal algorithms for solving the Rubik's Cube,
    representing different approaches to the problem from computer science and AI.

    ## 🎯 The Problem

    The Rubik's Cube has **43,252,003,274,489,856,000** possible configurations (43 quintillion!),
    but every scrambled cube can be solved in **20 moves or less** (proven in 2010 - "God's Number").

    ## 🔬 Three Approaches

    Our three algorithms represent different trade-offs between:
    - **Solution quality** (number of moves)
    - **Speed** (computation time)
    - **Memory** (RAM usage)
    - **Optimality guarantees**
    """)

    # Comparison chart
    st.subheader("📊 Quick Comparison")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🔵 Thistlethwaite
        **Year:** 1981
        **Approach:** Group Theory
        **Phases:** 4

        **Strengths:**
        - ⚡ Pure 4-phase solver
        - 💾 Low memory
        - 🎯 100% success on the thesis benchmark corpus

        **Weaknesses:**
        - 📏 Longer solutions than Kociemba or Korf
        - Not optimal

        **Best for:**
        Educational demonstrations, subgroup-based solving
        """)

    with col2:
        st.markdown("""
        ### 🟢 Kociemba
        **Year:** 1992
        **Approach:** Two-Phase IDA*
        **Phases:** 2

        **Strengths:**
        - 🎯 Near-optimal solutions
        - ⚡ Best overall practical trade-off
        - 🏆 100% success on the thesis benchmark corpus

        **Weaknesses:**
        - 💾 More table infrastructure than Thistlethwaite
        - Not guaranteed optimal

        **Best for:**
        Practical solving and mainline comparisons
        """)

    with col3:
        st.markdown("""
        ### 🟣 Korf IDA*
        **Year:** 1997
        **Approach:** Pattern Databases
        **Phases:** 1 (IDA*)

        **Strengths:**
        - ✨ Exact optimality when the external backend finishes
        - 🎯 Shortest solutions among completed runs
        - 🧠 Strong research baseline

        **Weaknesses:**
        - 🐢 Can time out on hard scrambles
        - 💾 Highest memory cost of the three solvers

        **Best for:**
        Optimal search experiments and validation
        """)

    st.markdown("---")

    # Timeline
    st.subheader("📅 Historical Timeline")

    st.markdown("""
    | Year | Event |
    |------|-------|
    | 1974 | Rubik's Cube invented by Ernő Rubik |
    | 1981 | **Thistlethwaite's algorithm** - First efficient solver |
    | 1992 | **Kociemba's algorithm** - Two-phase near-optimal |
    | 1997 | **Korf's IDA*** - Pattern database optimal solver |
    | 2010 | God's Number proven to be 20 |
    | 2026 | This thesis compares all three! 🎓 |
    """)

with tab2:
    st.header("🔵 Thistlethwaite's Algorithm (1981)")

    st.markdown("""
    ## Overview

    Thistlethwaite's algorithm uses **group theory** to solve the cube in **4 phases**,
    progressively restricting the allowed moves to create nested subgroups.

    ## The Four Phases

    Each phase reduces the cube to a smaller subgroup G₀ ⊃ G₁ ⊃ G₂ ⊃ G₃ ⊃ G₄
    """)

    # Phase explanations
    with st.expander("**Phase 1: Orient Edges** (G₀ → G₁)", expanded=True):
        st.markdown("""
        **Goal:** Orient all edges correctly (no "bad edges")

        **Allowed Moves:** All 18 (U, U', U2, D, D', D2, F, F', F2, ...)

        **Reduces to:** <U, D, F2, B2, L, R> (10 moves instead of 18)

        **What happens:**
        - All edge pieces are oriented so they can be solved without F, B, L', or R'
        - This is the largest reduction step
        - Typically takes 7-10 moves

        **Why it works:**
        The subgroup G₁ contains only configurations where edges are correctly oriented
        relative to the F and B faces.
        """)

    with st.expander("**Phase 2: Orient Corners & Position Edges** (G₁ → G₂)"):
        st.markdown("""
        **Goal:** Orient all corners correctly + position middle layer edges

        **Allowed Moves:** <U, D, F2, B2, L, R>

        **Reduces to:** <U, D, F2, B2, L2, R2> (only half-turns on F, B, L, R)

        **What happens:**
        - All corners are now oriented correctly
        - Middle layer edges are in their correct slice
        - Typically takes 10-15 moves

        **Why it works:**
        Quarter turns of F, B, L, R would mess up corner orientation, so we eliminate them.
        """)

    with st.expander("**Phase 3: Position Corners & Middle Edges** (G₂ → G₃)"):
        st.markdown("""
        **Goal:** Get corners and middle edges into correct positions (but possibly swapped)

        **Allowed Moves:** <U, D, F2, B2, L2, R2>

        **Reduces to:** <U2, D2, F2, B2, L2, R2> (all double-turns)

        **What happens:**
        - Corner pieces are in their correct positions
        - Middle layer edges are in their correct positions
        - Everything can now be solved with just double-turns
        - Typically takes 8-12 moves

        **Why it works:**
        The group G₃ has only 96 elements (compared to 43 quintillion!), so it's easy to solve.
        """)

    with st.expander("**Phase 4: Solve** (G₃ → Identity)"):
        st.markdown("""
        **Goal:** Completely solve the cube

        **Allowed Moves:** <U2, D2, F2, B2, L2, R2> (all double-turns)

        **What happens:**
        - Only 96 possible configurations remain
        - Can be solved with a simple lookup table
        - Typically takes 10-15 moves

        **Why it works:**
        G₃ is so small that we can precompute all solutions or use a simple search.
        """)

    st.markdown("---")
    st.subheader("📊 Performance Characteristics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Pros:**
        - ⚡ Fast on the benchmark corpus
        - 💾 Low memory footprint
        - 🎯 Pure solver with 100/100 thesis benchmark success
        - 📚 Elegant mathematical approach
        """)

    with col2:
        st.markdown("""
        **Cons:**
        - 📏 Clearly longer solutions than the other two solvers
        - 🤔 Not human-friendly sequences
        - 🏆 Not used in speedcubing
        """)

with tab3:
    st.header("🟢 Kociemba's Algorithm (1992)")

    st.markdown("""
    ## Overview

    Kociemba's algorithm is a **two-phase IDA* search** that finds near-optimal solutions.
    It is the **industry standard** and delivered the best overall practical trade-off
    in the corrected thesis benchmark.

    ## The Two Phases
    """)

    with st.expander("**Phase 1: Reach G₁ Subgroup**", expanded=True):
        st.markdown("""
        **Goal:** Orient all edges and corners, position UD-slice edges

        **Method:** IDA* search with coordinate-based heuristics

        **Coordinates Used:**
        - Edge orientation (2¹² = 4,096 states)
        - Corner orientation (3⁸ = 6,561 states)
        - UD-slice edge positions (C(12,4) = 495 states)

        **Search Space:** ~2 billion states

        **Heuristic:** Pruning tables precomputed from move tables

        **Result:** Cube is in G₁ subgroup (similar to Thistlethwaite's G₁)

        **Typical Length:** 8-12 moves
        """)

    with st.expander("**Phase 2: Solve from G₁**"):
        st.markdown("""
        **Goal:** Solve the cube from G₁ configuration

        **Allowed Moves:** <U, D, F2, B2, L2, R2> (same as Thistlethwaite Phase 2+)

        **Coordinates Used:**
        - Corner permutation (8! = 40,320)
        - UD-edge permutation (8! = 40,320)
        - Middle-edge permutation (4! = 24)

        **Search Space:** ~40 million states

        **Method:** IDA* search with pruning tables

        **Result:** Solved cube

        **Typical Length:** 8-12 moves
        """)

    st.markdown("---")
    st.subheader("🧮 Key Innovation: Coordinate Transformation")

    st.markdown("""
    Instead of storing the full cube state (43 quintillion possibilities), Kociemba uses
    **coordinate systems** that capture only the relevant information for each phase.

    For example, Phase 1 doesn't care about which specific corners are where, only their orientations.

    This reduces the search space from 43 quintillion to ~2 billion (Phase 1) and ~40 million (Phase 2).
    """)

    st.markdown("---")
    st.subheader("📊 Performance Characteristics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Pros:**
        - 🎯 Near-optimal solutions
        - 🚀 Best overall practical trade-off in the thesis benchmark
        - 🏆 Industry standard
        - 💡 Good balance of speed/quality
        """)

    with col2:
        st.markdown("""
        **Cons:**
        - 💾 More table infrastructure than Thistlethwaite
        - 🔧 Complex implementation
        - ❌ Not guaranteed optimal
        """)

with tab4:
    st.header("🟣 Korf's IDA* Algorithm (1997)")

    st.markdown("""
    ## Overview

    Korf's algorithm uses **IDA* search with admissible pattern databases** to find
    **optimal solutions**. In this repository, the publishable benchmark path uses an
    **external optimal backend**, while the lightweight internal composite heuristic is
    retained only for exploratory experiments and is **not** treated as generally admissible.

    ## Pattern Databases

    The key innovation is using **pattern databases** as admissible heuristics.
    """)

    with st.expander("**What are Pattern Databases?**", expanded=True):
        st.markdown("""
        A pattern database is a lookup table that stores the **exact minimum distance**
        from every possible configuration of a subset of pieces to the solved state.

        **Example: Corner Pattern Database**
        - Considers only the 8 corner pieces
        - Ignores all 12 edge pieces
        - Stores minimum moves to solve corners from every configuration
        - Size: 8! × 3⁷ = 88,179,840 entries (~44 MB)

        **Example: Edge Pattern Databases**
        - Multiple databases for different edge subsets
        - Each considers 6 edges, ignores the rest
        - Size: C(12,6) × 6! × 2⁵ = ~42 million entries (~0.6 MB each)

        **Why it works in the exact setting:**
        When the database stores exact distances for a subset of pieces, that lookup is an
        admissible lower bound for the full cube and can support optimal IDA* search.
        """)

    with st.expander("**IDA* Search Algorithm**"):
        st.markdown("""
        **Iterative Deepening A*** is a depth-first search that:

        1. Sets a depth limit (starting at heuristic estimate)
        2. Searches depth-first, pruning when f(n) = g(n) + h(n) exceeds limit
        3. If no solution found, increases limit to next f-value seen
        4. Repeats until solution found

        **Why IDA* instead of A*?**
        - Memory efficient: O(depth) instead of O(branching factor^depth)
        - For Rubik's Cube: ~20 states in memory instead of millions
        - Essential for solving optimally

        **Exact setting:**
        h(n) = max(corner_DB, edge_DB1, edge_DB2, ...)

        This optimality guarantee applies to admissible pattern-database heuristics.
        It does **not** automatically apply to every lightweight heuristic implementation.
        """)

    with st.expander("**Composite Heuristic (Our Implementation)**"):
        st.markdown("""
        This repository also contains a **composite heuristic** for exploratory experiments:

        1. **Corner Pattern Database** (44 MB)
           - All 8 corners
           - Stores exact distance to solve corners

        2. **Edge Pattern Database** (0.6 MB)
           - 6 edges from different slice groups
           - Stores exact distance to solve these edges

        3. **Heuristic Combination:**
           ```python
           h(state) = max(corner_distance, edge_distance)
           ```

        This provides useful guidance while keeping memory moderate, but it is **not**
        the basis for the final optimality claims of the thesis benchmark.

        **Benchmark path used in the thesis:**
        - External exact optimal backend
        - Enforced 120-second timeout
        - Exact on completed runs, but 3/25 requested scramble length 20 benchmark cases timed out
        """)

    st.markdown("---")
    st.subheader("📊 Performance Characteristics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Pros:**
        - ✨ **Optimal solutions when the exact backend finishes**
        - 🎯 Shortest solutions among completed runs
        - 🧠 AI research benchmark
        - 📊 Useful for validating other algorithms
        """)

    with col2:
        st.markdown("""
        **Cons:**
        - 🐢 Variable speed with visible timeout risk on hard requested scramble length 20 cases
        - 💾 Highest memory demand among the three compared solvers
        - 🔬 Overkill for casual solving
        - 💻 Exact backend setup is heavier than the other two algorithms
        """)

# Glossary
st.markdown("---")
st.header("📖 Glossary of Terms")

with st.expander("Click to expand glossary"):
    st.markdown("""
    ### Basic Cube Terms

    - **Cubie**: A single physical piece of the cube (corner, edge, or center)
    - **Facelet**: An individual colored sticker on the cube (54 total)
    - **Sticker**: Same as facelet

    ### Notation

    - **Singmaster Notation**: Standard move notation (U, D, F, B, L, R)
      - U = Top face clockwise
      - U' = Top face counter-clockwise
      - U2 = Top face 180°
    - **Face**: One of the six sides (Up, Down, Front, Back, Left, Right)

    ### Algorithm Terms

    - **IDA***: Iterative Deepening A* - depth-first search with heuristic pruning
    - **A***: Best-first search algorithm using f(n) = g(n) + h(n)
    - **Heuristic**: Estimated cost from current state to goal
    - **Admissible**: Heuristic that never overestimates (h(n) ≤ h*(n))
    - **Pruning**: Eliminating branches of search tree that can't improve solution
    - **Pattern Database**: Lookup table of exact distances for piece subsets

    ### Group Theory Terms

    - **Group**: Mathematical structure with a set and operation (cube moves)
    - **Subgroup**: Subset of group closed under the operation
    - **Coset**: Partition of group by subgroup
    - **Group Order**: Number of elements in group
    - **Generator**: Set of moves that can produce all group elements

    ### Performance Metrics

    - **Solution Length**: Number of moves in solution
    - **God's Number**: Proven maximum (20 moves for any scramble)
    - **Time Complexity**: How computation time grows with problem size
    - **Space Complexity**: How memory usage grows with problem size
    - **Node Expansion**: Number of states explored during search
    """)

# References
st.markdown("---")
st.header("📚 References & Further Reading")

with st.expander("Academic Papers"):
    st.markdown("""
    1. **Thistlethwaite, M.** (1981). "52-move algorithm for Rubik's Cube"

    2. **Kociemba, H.** (1992). "Close to God's Algorithm"
       - http://kociemba.org/cube.htm

    3. **Korf, R.** (1997). "Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"
       - Proceedings of AAAI-97

    4. **Rokicki et al.** (2010). "God's Number is 20"
       - http://cube20.org/

    5. **Hart, P., Nilsson, N., and Raphael, B.** (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"
       - Original A* paper
    """)

with st.expander("Online Resources"):
    st.markdown("""
    - **cube20.org**: Proof of God's Number
    - **ruwix.com**: Interactive cube solver and tutorials
    - **speedsolving.com**: Community of speedcubers
    - **GitHub Projects**: V-Wong/CubeSim, davidwhogg/MagicCube, mtking2/PyCube, benbotto/rubiks-cube-cracker
    """)

# Footer
st.markdown("---")
st.caption("Phase 9: Demos & UI | Alex Toska - University of Patras")
