# 📋 COMPLETE PHASE-BY-PHASE RESOURCE GUIDE

## 🔴 **PHASE 1: FOUNDATION & SETUP** (Weeks 1-2)

### Tasks
- Set up development environment
- Study group theory basics
- Understand cube representation
- Learn Singmaster notation

### **📚 Resources to Study:**

**Group Theory Fundamentals:**
- 📄 **MIT SP.268 Course Notes**: https://web.mit.edu/sp.268/www/rubik.pdf
  - Read: Sections on permutation groups, Cayley graphs, subgroups (pages 1-15)
- 📄 **Harvard Notes**: http://people.math.harvard.edu/~jjchen/docs/Group%20Theory%20and%20the%20Rubik's%20Cube.pdf
  - Focus on: Bounds for solving, parity constraints
- 📄 **UC Berkeley Handout**: http://math.berkeley.edu/~hutching/rubik.pdf
  - Read: How to construct macros using commutators

**Notation & Basics:**
- 🌐 **Singmaster Notation Guide**: https://ruwix.com/the-rubiks-cube/notation/
  - Master all basic moves: F, B, L, R, U, D and modifiers (', 2)
- 🌐 **Speedsolving Wiki**: https://www.speedsolving.com/wiki/index.php/Notation
  - Advanced notation: slice moves (M, E, S), wide moves (Fw, Rw)

**Background Reading:**
- 📖 **Wikipedia - Rubik's Cube**: https://en.wikipedia.org/wiki/Rubik%27s_Cube
  - Read: Structure section, Mathematics section
- 📖 **Wikipedia - Optimal Solutions**: https://en.wikipedia.org/wiki/Optimal_solutions_for_Rubik%27s_Cube
  - Overview of all major algorithms

---

## 🟡 **PHASE 2: CORE CUBE IMPLEMENTATION** (Weeks 3-4)

### Tasks
- Create RubiksCube class
- Implement all 18 basic moves
- Add visualization
- Write comprehensive tests

### **💻 Repositories to Reference:**

**Primary Cube Representations:**
1. **pglass/cube** (Python - Cubie representation)
   - 🔗 https://github.com/pglass/cube
   - 📦 Install: `pip install rubik-cube`
   - 👀 **Files to study:**
     - `rubik/cube.py` - Core Cube class with piece-based model
     - `rubik/solve.py` - Layer-by-layer solver
     - `rubik/optimize.py` - Move sequence optimizer
   - ⭐ **Why useful:** Clean piece-based architecture, rotation matrices

2. **PyCuber** (Python - Facelet representation)
   - 🔗 https://github.com/adrianliaw/PyCuber
   - 📦 Install: `pip install pycuber`
   - 👀 **Files to study:**
     - `pycuber/cube.py` - 54-facelet model
     - `pycuber/formula.py` - Move manipulation
   - ⭐ **Why useful:** Clean OOP design, easy to visualize

3. **magiccube** (Python - NxN support)
   - 🔗 https://github.com/trincaog/magiccube
   - 📦 Install: `pip install magiccube`
   - 👀 **Focus on:** Coordinate-based representation for any cube size

**Visualization Examples:**
4. **V-Wong/CubeSim** (2D Pygame)
   - 🔗 https://github.com/V-Wong/CubeSim
   - 👀 **Files to study:**
     - `src/cube.py` - 2D array representation
     - `src/cube_renderer.py` - Pygame rendering
     - `tests/` - Comprehensive pytest suite

5. **davidwhogg/MagicCube** (3D matplotlib)
   - 🔗 https://github.com/davidwhogg/MagicCube
   - 👀 **Files to study:**
     - `cube_interactive.py` - Quaternion-based 3D rendering
   - ⭐ **Why useful:** No OpenGL needed, uses only matplotlib

### **📚 Tutorial to Follow:**

6. **DePrince Lab Coordinate Tutorial**
   - 🌐 https://deprincelab.github.io/tutorials/rubiks_cube_python/index.html
   - 🔗 GitHub: https://github.com/edeprince3/super_coding_fun_time/tree/main/rubiks_cube
   - 📖 **What to learn:** 3D coordinate system, indexing scheme, VPython visualization

---

## 🎯 **PHASE 3: THISTLETHWAITE ALGORITHM** (Weeks 5-7)

### Tasks
- Implement 4-phase group reduction (G₀→G₁→G₂→G₃→G₄)
- Generate pattern databases for each phase
- Implement IDA* search per phase
- Achieve max 45-52 move solutions

### **💻 Primary Implementation References:**

1. **benbotto/rubiks-cube-cracker** (C++ - BEST DOCUMENTATION)
   - 🔗 https://github.com/benbotto/rubiks-cube-cracker
   - 👀 **Critical files to study:**
     - `Model/World/RubiksCube/Thistlethwaite/G0G1Solver.cpp` - Phase 1 (edge orientation)
     - `Model/World/RubiksCube/Thistlethwaite/G1G2Solver.cpp` - Phase 2 (corner orientation)
     - `Model/World/RubiksCube/Thistlethwaite/G2G3Solver.cpp` - Phase 3 (corner/edge pairing)
     - `Model/World/RubiksCube/Thistlethwaite/G3G4Solver.cpp` - Phase 4 (final solve)
     - `Model/PatternDatabase/Thistlethwaite/` - All pattern databases
   - 📖 **README sections:** "Thistlethwaite's Algorithm" - explains all 4 phases in detail

2. **itsdaveba/cube-solver** (Python - Complete Thistlethwaite + Kociemba)
   - 🔗 https://github.com/itsdaveba/cube-solver
   - 📦 Install: `pip install cube-solver`
   - 📚 Docs: https://cube-solver.readthedocs.io
   - 👀 **Files to study:**
     - `cube_solver/thistlethwaite/` - Complete Python implementation
     - `cube_solver/thistlethwaite/coordinates.py` - All coordinate systems
     - `cube_solver/thistlethwaite/tables.py` - Pattern database generation
   - ⭐ **Why useful:** ONLY complete Python Thistlethwaite implementation

3. **dfinnis/Rubik** (Go - Excellent documentation)
   - 🔗 https://github.com/dfinnis/Rubik
   - 📖 **README:** Best explanation of group transitions and state space sizes

4. **itaysadeh/rubiks-cube-solver** (C++ - Clean implementation)
   - 🔗 https://github.com/itaysadeh/rubiks-cube-solver
   - 👀 **Study:** 5 subgroups (G0-G4) with lookup tables

### **📚 Theory & Documentation:**

5. **Jaap's Puzzle Page - Thistlethwaite**
   - 🌐 https://www.jaapsch.net/puzzles/thistle.htm
   - 📖 **What to read:**
     - Original 1981 letter scans from Thistlethwaite to Singmaster
     - Move tables for each stage
     - Optimization from 52 to 45 moves

6. **Medium Article by Ben Botto**
   - 🌐 https://medium.com/@benjamin.botto/implementing-an-optimal-rubiks-cube-solver-using-korf-s-algorithm-bf750b332cf9
   - 📖 **Sections to read:** Algorithm comparison, Thistlethwaite vs Korf explanation

### **📄 Academic Reference:**

7. **Wikipedia - Optimal Solutions**
   - 🌐 https://en.wikipedia.org/wiki/Optimal_solutions_for_Rubik%27s_Cube
   - 📖 **Section:** "Thistlethwaite's algorithm" with detailed phase breakdown

---

## 🚀 **PHASE 4: KOCIEMBA ALGORITHM** (Weeks 8-10)

### Tasks
- Implement 2-phase approach (G₀→G₁→solved)
- Generate ~80MB pruning tables
- Achieve <19 move average solutions
- Solve in <5 seconds per cube

### **💻 Primary Implementations (MUST STUDY):**

1. **hkociemba/RubiksCube-TwophaseSolver** (Official Implementation)
   - 🔗 https://github.com/hkociemba/RubiksCube-TwophaseSolver
   - 📦 Install: `pip install RubikTwoPhase`
   - 👀 **CRITICAL FILES TO STUDY (in order):**
     - `coord.py` - **START HERE** - All 6 coordinate systems
       - Corner orientation, edge orientation, slice position for Phase 1
       - Corner permutation, edge permutation for Phase 2
     - `cubie.py` - Low-level cubie representation
     - `moves.py` - Move table generation for coordinates
     - `prunetables.py` - Pattern database generation (~80MB, BFS)
     - `solver.py` - Phase 1 and Phase 2 IDA* implementations
     - `symmetries.py` - 48-symmetry reduction (16x memory reduction)
   - ⭐ **Why essential:** Created by Herbert Kociemba himself, production-quality code

2. **muodov/kociemba** (Fast C++ version)
   - 🔗 https://github.com/muodov/kociemba
   - 📦 Install: `pip install kociemba`
   - ⭐ **Why useful:** Fastest solving, used in real robot solvers

3. **tcbegley/cube-solver** (Pure Python for learning)
   - 🔗 https://github.com/tcbegley/cube-solver
   - 👀 **Files to study:**
     - `twophase/coords.py` - Clean coordinate implementations
     - `twophase/pruning.py` - Pruning table generation with BFS
     - `twophase/solve.py` - IDA* for both phases
   - ⭐ **Why useful:** Most readable Python code, no C dependencies

4. **itsdaveba/cube-solver** (Comparison framework)
   - 🔗 https://github.com/itsdaveba/cube-solver
   - ⭐ **Why useful:** Side-by-side Thistlethwaite vs Kociemba comparison

### **📚 Official Documentation:**

5. **Kociemba's Official Website**
   - 🌐 Main: https://kociemba.org/cube.htm
   - 🌐 **Two-Phase Math Details**: https://kociemba.org/math/twophase.htm
     - Phase 1: G₀ → G₁ (2.2 billion states, max 12 moves)
     - Phase 2: G₁ → solved (19.5 million states, max 18 moves)
   - 🌐 **Implementation Details**: https://kociemba.org/math/imptwophase.htm
   - 💾 **Cube Explorer Software**: https://kociemba.org/download.htm

6. **Jaap's Puzzle Page - Computer Solving**
   - 🌐 https://www.jaapsch.net/puzzles/compcube.htm
   - 📖 **Sections to read:**
     - Kociemba's algorithm explanation
     - Implementation details for pattern databases
     - Pseudocode examples
     - Tree search and IDA* coverage

### **📄 Academic Papers:**

7. **Kociemba Original Paper** (1992)
   - Title: "Close to God's algorithm"
   - Published in: Cubism For Fun
   - 📖 **What to understand:** How combining Thistlethwaite's first 2 phases and last 2 phases works

---

## 📏 **PHASE 5: DISTANCE ESTIMATOR** (Weeks 11-12)

### Tasks
- Implement pattern database-based distance estimation
- Create multiple heuristic approaches
- Test accuracy on known-distance positions
- Calculate Mean Absolute Error

### **💻 Implementations to Reference:**

1. **Use Korf Pattern Databases** (from Phase 6 below)
   - Corner database → estimates minimum moves for corners
   - Edge databases → estimates minimum moves for edges
   - `max(corner_dist, edge1_dist, edge2_dist)` = lower bound estimate

2. **BenSDuggan/CubeAI** (Multiple heuristics)
   - 🔗 https://github.com/BenSDuggan/CubeAI
   - 👀 **Files to study:**
     - `Heuristic.py` - Manhattan distance, Hamming distance, simple heuristic
     - `ManhattanCube.py` - 3D Manhattan calculation
   - ⭐ **Why useful:** Compare multiple heuristic approaches

### **📚 Theory & Guidance:**

3. **Stack Overflow - Pattern Database Creation**
   - 🌐 https://stackoverflow.com/questions/58860280/how-to-create-a-pattern-database-for-solving-rubiks-cube
   - 📖 **What to learn:**
     - BFS generation process
     - Lexicographic indexing for permutations
     - Memory optimization strategies
     - Why 8-edge database is too large (2.4GB)

4. **Stack Overflow - Heuristic Functions for A***
   - 🌐 https://stackoverflow.com/questions/60130124/heuristic-function-for-rubiks-cube-in-a-algorithm-artificial-intelligence
   - 📖 **What to learn:**
     - Pattern databases vs Manhattan distance
     - Admissibility requirements
     - Why Manhattan distance is weak for Rubik's Cube
     - Corner database: 88M positions = 44MB
     - Edge database: would need 500GB for 12 edges (use 7-edge split instead)

5. **Stack Overflow - General Heuristics**
   - 🌐 https://stackoverflow.com/questions/36490073/heuristic-for-rubiks-cube
   - 📖 **What to learn:**
     - Manhattan distance must be divided by 8 for admissibility
     - Corner/edge distances divided by 4
     - Move pruning techniques

### **📄 Validation Data:**

6. **cube20.org - Known Distance Positions**
   - 🌐 http://www.cube20.org/
   - 📖 **Use for:** Testing estimator accuracy on positions with known optimal distance
   - Download distance-20 positions to test worst-case estimation

---

## 🎖️ **PHASE 6: KORF OPTIMAL SOLVER** (Weeks 13-16)

### Tasks
- Generate pattern databases (~794MB total)
- Implement Lehmer code indexing
- Implement IDA* with additive heuristics
- Achieve optimal solutions (≤20 moves)

### **💻 Primary Implementations:**

1. **benbotto/rubiks-cube-cracker** (C++ - Most complete)
   - 🔗 https://github.com/benbotto/rubiks-cube-cracker
   - 👀 **CRITICAL FILES (study in order):**
     - `Util/RubiksCubePermutationIndexer.h` + `.cpp` - **LINEAR Lehmer code** (O(n) not O(n²))
     - `Model/PatternDatabase/Korf/CornerPatternDatabase.cpp` - 88M positions, ~42MB
     - `Model/PatternDatabase/Korf/EdgePatternDatabase.cpp` - 7-edge databases, ~244MB each
     - `Model/PatternDatabase/Korf/EdgePermutationDatabase.cpp` - ~228MB
     - `Controller/Command/Solver/KorfCubeSolver.cpp` - Complete IDA* implementation
   - ⭐ **Why essential:** Most thoroughly documented, uses linear Lehmer algorithm

2. **hkociemba/RubiksCube-OptimalSolver** (Python)
   - 🔗 https://github.com/hkociemba/RubiksCube-OptimalSolver
   - 📦 Install: `pip install RubikOptimal`
   - 👀 **Files to study:**
     - `patterndb.py` - Pattern database generation and lookup
     - `solver.py` - IDA* with pattern database heuristics
     - `reid.py` - Michael Reid's superior coordinate system
   - ⚠️ **Performance:** 10 cubes = 8 hours (CPython) or 13 minutes (PyPy)
   - ⭐ **Why useful:** Working Python reference, PyPI package

3. **AdamHayse/optimal-solve-rubikscube** (C - Configurable)
   - 🔗 https://github.com/AdamHayse/optimal-solve-rubikscube
   - 👀 **Files to study:**
     - `generateCDB.c` - Corner database generation with BFS
     - `generateEDB.c` - Edge database (compile with `-D TRACKED_EDGES=7`)
     - `cdatabase.c` / `edatabase.c` - State-to-index conversion
     - `IDAstar.c` - IDA* search with additive heuristics
     - `mymath.c` - Lehmer encoding/decoding
   - 🔧 **Compile for 7-edge:**
     ```bash
     gcc -D TRACKED_EDGES=7 do_search.c searchmoves.c edatabase.c cdatabase.c mymath.c database.c IDAstar.c -std=c99 -O2 -o IDAstar7
     ```
   - ⭐ **Why useful:** Choose database size (6/7/8 edges), multi-threading support

4. **FarhanShoukat/Rubiks-Cube-Solver** (Python - Educational)
   - 🔗 https://github.com/FarhanShoukat/Rubiks-Cube-Solver
   - 👀 **Focus on:** Pattern database generation with BFS, integration with IDA*
   - 📄 **Research report** included comparing IDA* with/without pattern databases

### **📄 Essential Papers:**

5. **Korf's Original Paper** (MUST READ)
   - 📄 **"Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"** (AAAI 1997)
   - 🔗 https://www.cs.princeton.edu/courses/archive/fall06/cos402/papers/korfrubik.pdf
   - 📖 **What to read:**
     - Pattern database concept and theory
     - Admissible heuristic characterization
     - Memory-time tradeoff: t ≈ n/m (time × memory = state space constant)
     - Corner database: 88M positions
     - Edge databases: why split into two 7-edge sets
     - Performance analysis
   - ⭐ **Most important paper for your thesis**

6. **Linear Lehmer Code Algorithm**
   - 📄 **"Large-Scale Parallel Breadth-First Search"** (AAAI 2005) by Korf et al.
   - 🔗 https://www.aaai.org/Papers/AAAI/2005/AAAI05-219.pdf
   - 📖 **What to learn:** O(n) linear algorithm for permutation indexing vs O(n²) quadratic
   - ⭐ **Critical for efficient database generation**

7. **Korf's Publication List**
   - 🌐 https://web.cs.ucla.edu/~korf/publications.html
   - 📖 **Additional papers on:**
     - IDA* algorithm
     - Pattern databases for other puzzles
     - Breadth-first search parallelization

### **📚 Technical Documentation:**

8. **Ben Botto's Medium Article on Lehmer Codes**
   - 🌐 https://medium.com/@benjamin.botto/sequentially-indexing-permutations-a-linear-algorithm-for-computing-lexicographic-rank-a22220ffd6e3
   - 📖 **What to learn:** Complete explanation of linear Lehmer code algorithm

9. **Jaap's Puzzle Page - Implementation Details**
   - 🌐 https://www.jaapsch.net/puzzles/compcube.htm
   - 📖 **Sections:**
     - Pattern database implementation
     - Tree search techniques
     - IDA* pseudocode
     - Database generation
     - Symmetry reduction

### **📊 Performance Benchmarks:**

10. **PyPI - RubikOptimal Package**
    - 🌐 https://pypi.org/project/RubikOptimal/
    - 📖 **What to note:**
      - Hardest position (20 moves): ~3 hours solving time
      - ~2.5 million nodes/second (CPython)
      - Depth 17: ~120 billion nodes
      - PyPy: 10x speedup over CPython

---

## 🧠 **PHASE 7: A* WITH HEURISTICS** (Weeks 17-19)

### Tasks
- Implement A* and IDA*
- Compare multiple heuristics
- Design novel heuristic (research contribution)
- Demonstrate why IDA* dominates for Rubik's Cube

### **💻 Implementations:**

1. **BenSDuggan/CubeAI** (Multi-heuristic comparison)
   - 🔗 https://github.com/BenSDuggan/CubeAI
   - 👀 **CRITICAL FILES:**
     - `AIs.py` - Both A* and IDA* implementations with State class
     - `Heuristic.py` - Manhattan distance, Hamming distance, simple heuristic
     - `ManhattanCube.py` - 3D Manhattan calculation
     - `Cube.py` - Core representation for NxN cubes
   - 📊 **Key finding:** A* solved 40-50 cubes vs IDA* solved 5000+ (demonstrates memory issue)
   - ⭐ **Why essential:** Direct A* vs IDA* comparison with multiple heuristics

2. **yakupbilen/drl-rubiks-cube** (Deep RL + A* hybrid)
   - 🔗 https://github.com/yakupbilen/drl-rubiks-cube
   - 👀 **Files to study:**
     - `run_solve.py` - A* with neural network heuristic
     - Neural network approximates cost-to-go function
   - ⭐ **Why interesting:** Modern machine learning approach to heuristic design

3. **espipj/Rubik** (Multi-language A*)
   - 🔗 https://github.com/espipj/Rubik
   - 👀 **Both Prolog and Java implementations of A*** - compare approaches

### **📄 Search Algorithm Papers:**

4. **IDA* Original Paper** (Korf 1985)
   - 📄 **"Depth-first iterative-deepening: an optimal admissible tree search"**
   - Published in: Artificial Intelligence journal
   - 📖 **What to learn:**
     - Why IDA* uses less memory than A*
     - Iterative deepening with admissible heuristic
     - Depth-first vs breadth-first search

5. **Pattern Database Papers by Felner & Korf:**
   - 📄 **"Disjoint Pattern Database Heuristics"** - Artificial Intelligence (2002)
     - 🔗 https://www.sciencedirect.com/science/article/pii/S0004370201000923
     - 📖 **Learn:** How to partition problems into independent subproblems
   
   - 📄 **"Additive Pattern Database Heuristics"** - JAIR (2004)
     - 🔗 https://dl.acm.org/doi/10.5555/1622487.1622496
     - 📖 **Learn:** Why you can sum disjoint pattern database heuristics
   
   - 📄 **"Analyzing the Performance of Pattern Database Heuristics"** - AAAI 2007
     - 📖 **Learn:** Theoretical models for predicting IDA* performance

6. **Original Pattern Database Concept**
   - 📄 **"Pattern Databases"** by Culberson & Schaeffer (1998)
   - Published in: Computational Intelligence
   - 📖 **Learn:** First application to 15-puzzle, foundational concepts

### **📚 Stack Overflow Discussions:**

7. **Heuristic Function Design**
   - 🌐 https://stackoverflow.com/questions/60130124/heuristic-function-for-rubiks-cube-in-a-algorithm-artificial-intelligence
   - 📖 **Key insights:**
     - Pattern databases vs Manhattan distance comparison
     - Admissibility requirements explained
     - Why Manhattan is weak for Rubik's Cube
     - Specific calculations for database sizes

8. **Manhattan Distance for Rubik's Cube**
   - 🌐 https://stackoverflow.com/questions/36490073/heuristic-for-rubiks-cube
   - 📖 **Implementation guidance:**
     - Must divide by 8 for admissibility
     - Corner/edge distances divided by 4
     - Move pruning techniques

### **📖 Tutorial Articles:**

9. **Towards Data Science - IDA* Tutorial**
   - 🌐 https://towardsdatascience.com/rubiks-cube-solver-96fa6c56fbe4/
   - 🔗 GitHub: https://github.com/bellerb/RubiksCube_Solver
   - 📖 **What to learn:**
     - Step-by-step IDA* implementation
     - Heuristic lookup table generation with BFS
     - Why IDA* preferred over A* for memory

10. **Brad Hodkinson's Algorithm Survey**
    - 🌐 https://medium.com/@brad.hodkinson2/writing-code-to-solve-a-rubiks-cube-7bf9c08de01f
    - 📖 **Sections to read:**
      - Representation methods comparison
      - A* vs IDA* vs neural networks
      - Optimal vs fast solution trade-offs

---

## 📊 **PHASE 8: COMPREHENSIVE TESTING** (Weeks 20-22)

### Tasks
- Test all algorithms on 1000 scrambles
- Generate comparison tables and graphs
- Statistical analysis
- Create all thesis figures

### **💻 Comparison Frameworks:**

1. **The-Semicolons/AnalysisofRubiksCubeSolvingAlgorithm**
   - 🔗 https://github.com/The-Semicolons/AnalysisofRubiksCubeSolvingAlgorithm
   - 👀 **What to use:**
     - Framework for comparing Thistlethwaite, Kociemba, Korf, Rokicki
     - Time complexity, space complexity, move count analysis
     - Markov-chain scrambling algorithm for test cases
   - ⭐ **Why useful:** Rigorous comparative analysis framework

2. **itsdaveba/cube-solver** (Built-in comparisons)
   - 🔗 https://github.com/itsdaveba/cube-solver
   - ⭐ **Feature:** Side-by-side Thistlethwaite vs Kociemba testing

### **📊 Validation Data:**

3. **cube20.org** (Official God's Number proof)
   - 🌐 Main: http://www.cube20.org/
   - 🌐 QTM version: http://www.cube20.org/qtm
   - 📖 **What to use:**
     - Distance distribution data (94% of cubes require 17-18 moves)
     - Specific distance-20 positions for testing
     - Methodology for coset analysis
     - Complete source code downloads
   - 📊 **Key statistics:**
     - Total positions: 43,252,003,274,489,856,000
     - Distance 20 positions: ~490 million
     - Average optimal: ~17.8 moves

4. **Semantic Scholar - God's Number Paper**
   - 🔗 https://www.semanticscholar.org/paper/The-Diameter-of-the-Rubik's-Cube-Group-Is-Twenty-Rokicki-Kociemba/fa91120d3a50632287b03c7bf220a12adb5f21af
   - 📄 Full paper with distance distributions

### **📚 Comparison References:**

5. **Wikipedia - Algorithm Comparison Table**
   - 🌐 https://en.wikipedia.org/wiki/Optimal_solutions_for_Rubik%27s_Cube
   - 📊 **Use tables:**
     - Branching factors for each algorithm
     - Memory requirements comparison
     - Typical solution lengths
     - Symmetry exploitation (48-fold, 16-fold, none)

6. **CubingHistory - Algorithm Evolution**
   - 🌐 https://www.cubinghistory.com/3x3/3x3ComputerAlgorithms
   - 📖 **Timeline data:** Upper bound reductions from 277 moves (1979) to 20 moves (2010)

---

## 🎨 **PHASE 9: DEMOS & UI** (Week 23)

### **💻 Visualization Examples:**

1. **V-Wong/CubeSim** (2D Pygame)
   - 🔗 https://github.com/V-Wong/CubeSim
   - 👀 **Use for:** 2D visualization, keyboard controls

2. **davidwhogg/MagicCube** (3D matplotlib)
   - 🔗 https://github.com/davidwhogg/MagicCube
   - 👀 **Use for:** 3D rendering without OpenGL

3. **mtking2/PyCube** (3D OpenGL)
   - 🔗 https://github.com/mtking2/PyCube
   - 👀 **Use for:** Realistic 3D rendering with PyOpenGL

4. **benbotto/rubiks-cube-cracker** (OpenGL with algorithm comparison)
   - 🔗 https://github.com/benbotto/rubiks-cube-cracker
   - 👀 **Feature:** Press F1 for Thistlethwaite, F2 for Korf - side-by-side comparison

---

## 📝 **PHASE 10: THESIS WRITING** (Throughout)

### **📚 Academic Sources:**

1. **God's Number Definitive Proof**
   - 📄 **"The Diameter of the Rubik's Cube Group Is Twenty"**
   - Published: SIAM Journal on Discrete Mathematics (2013) and SIAM Review (2014)
   - 🔗 https://dl.acm.org/doi/abs/10.1137/140973499
   - 📖 **What to cite:** Proof that 20 moves suffice from any position

2. **MIT Complexity Analysis**
   - 📄 **"Algorithms for Solving Rubik's Cubes"**
   - 🔗 arXiv: https://arxiv.org/abs/1106.5736
   - 🔗 MIT DSpace: https://dspace.mit.edu/handle/1721.1/73771
   - 🔗 Springer: https://link.springer.com/chapter/10.1007/978-3-642-23719-5_58
   - 📖 **What to cite:** NP-hardness proof, asymptotic bounds for nxn cubes

3. **Machine Learning Approaches:**
   - 📄 **"Solving the Rubik's Cube Without Human Knowledge"** (2018)
     - 🔗 https://arxiv.org/abs/1805.07470
     - Autodidactic Iteration, 100% solve rate, 30 moves median
   
   - 📄 **"Solving the Rubik's Cube with Deep Reinforcement Learning and Search"**
     - Published: Nature Machine Intelligence (2019)
     - 🔗 https://www.nature.com/articles/s42256-019-0070-z
     - DeepCubeA system, 60.3% optimal solutions
   
   - 📄 **Recent 2024 papers:**
     - "Without Tricky Sampling": https://arxiv.org/html/2411.19583v1
     - "Using Graph Structure": https://arxiv.org/html/2408.07945v1

### **📖 Theses for Reference:**

4. **KTH Royal Institute (Sweden)** - Bachelor level, very relevant!
   - 📄 "Algorithms for solving the Rubik's cube" by Harpreet Kaur (2015)
   - 🔗 https://www.diva-portal.org/smash/get/diva2:816583/FULLTEXT01.pdf
   - 📖 **Why important:** Compares Thistlethwaite vs IDA*, bachelor-level work, 41 pages

5. **University of Linz (Austria)**
   - 📄 "Using Group Theory for solving Rubik's Cube"
   - 🔗 http://www.algebra.uni-linz.ac.at/Projects/FurtherProjects/Kainberger/Using_Group_Theory_for_solving_Rubik's_Cube.pdf
   - 📖 **What to learn:** Pure mathematical group theory approach using GAP software

### **📕 Textbook:**

6. **"Adventures in Group Theory"** by David Joyner
   - 🔗 Amazon: https://www.amazon.com/Adventures-Group-Theory-Merlins-Mathematical/dp/0801890136
   - 🔗 JHU Press: https://www.press.jhu.edu/books/title/9554/adventures-group-theory
   - 📖 **Chapters to read:**
     - 1-12: Group theory foundations via Rubik's Cube
     - 15: God's algorithm analysis

---

## 🎯 **QUICK START PRIORITY**

### **Week 1 - Start with these:**
1. ✅ **MIT Group Theory Notes**: https://web.mit.edu/sp.268/www/rubik.pdf
2. ✅ **Notation Guide**: https://ruwix.com/the-rubiks-cube/notation/
3. ✅ **pglass/cube repo**: https://github.com/pglass/cube
4. ✅ **Wikipedia Overview**: https://en.wikipedia.org/wiki/Optimal_solutions_for_Rubik%27s_Cube

### **Week 2 - Core Algorithms:**
5. ✅ **hkociemba Kociemba**: https://github.com/hkociemba/RubiksCube-TwophaseSolver
6. ✅ **benbotto Thistlethwaite**: https://github.com/benbotto/rubiks-cube-cracker
7. ✅ **Korf's Paper**: https://www.cs.princeton.edu/courses/archive/fall06/cos402/papers/korfrubik.pdf

### **Week 3 - Distance Estimation:**
8. ✅ **Pattern DB Stack Overflow**: https://stackoverflow.com/questions/58860280
9. ✅ **Heuristic Stack Overflow**: https://stackoverflow.com/questions/60130124

### **Week 4 - A* and Testing:**
10. ✅ **BenSDuggan/CubeAI**: https://github.com/BenSDuggan/CubeAI
11. ✅ **cube20.org**: http://www.cube20.org/
12. ✅ **KTH Thesis**: https://www.diva-portal.org/smash/get/diva2:816583/FULLTEXT01.pdf

---

This gives you every resource organized by phase with specific files to study and why each is important! 🚀