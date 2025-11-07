# Essential Resources for Your Rubik's Cube Thesis

Here are all the key sources organized by category:

## 🎓 **Core Academic Papers**

### God's Number Proof
- **The definitive proof**: https://dl.acm.org/doi/abs/10.1137/140973499
- **Official website with code**: http://www.cube20.org/
- **Semantic Scholar version**: https://www.semanticscholar.org/paper/The-Diameter-of-the-Rubik's-Cube-Group-Is-Twenty-Rokicki-Kociemba/fa91120d3a50632287b03c7bf220a12adb5f21af

### Korf's Pattern Database Paper
- **Original AAAI paper** (THE most important): https://www.cs.princeton.edu/courses/archive/fall06/cos402/papers/korfrubik.pdf
- **Korf's publications page**: https://web.cs.ucla.edu/~korf/publications.html

### Pattern Database Theory
- **Additive Pattern Databases**: https://dl.acm.org/doi/10.5555/1622487.1622496
- **Disjoint Pattern Databases**: https://www.sciencedirect.com/science/article/pii/S0004370201000923

### Complexity Analysis
- **MIT Paper - Algorithms for Solving Rubik's Cubes**: https://arxiv.org/abs/1106.5736
- **MIT DSpace**: https://dspace.mit.edu/handle/1721.1/73771
- **Springer version**: https://link.springer.com/chapter/10.1007/978-3-642-23719-5_58

---

## 💻 **Python Implementations (ESSENTIAL)**

### Kociemba Algorithm
- **Official by Herbert Kociemba**: https://github.com/hkociemba/RubiksCube-TwophaseSolver
  - PyPI: `pip install RubikTwoPhase`
  - Solves in <19 moves, <1 second with PyPy
  
- **Alternative implementation**: https://github.com/muodov/kociemba
  - PyPI: `pip install kociemba`
  - Pure Python + C versions

### Optimal Solver (Korf's Algorithm)
- **Official by Herbert Kociemba**: https://github.com/hkociemba/RubiksCube-OptimalSolver
  - PyPI: `pip install RubikOptimal`
  - True optimal solutions (20 moves max)
  - Requires 794MB pruning tables

### General Python Solvers
- **pglass/cube**: https://github.com/pglass/cube
- **trincaog/magiccube**: https://github.com/trincaog/magiccube

---

## 🔧 **C++ Implementations**

### Complete with Visualization
- **Korf + Thistlethwaite with OpenGL**: https://github.com/benbotto/rubiks-cube-cracker
  - Best for understanding both algorithms
  - Includes visualization
  - Medium article: https://medium.com/@benjamin.botto/implementing-an-optimal-rubiks-cube-solver-using-korf-s-algorithm-bf750b332cf9

### Thistlethwaite Implementations
- **With OpenGL**: https://github.com/ldehaudt/Rubik_Solver
- **C++ clean version**: https://github.com/itaysadeh/rubiks-cube-solver
- **Modern C++17**: https://github.com/cedrikaagaard/thistlethwaite
- **Go implementation**: https://github.com/dfinnis/Rubik

---

## 📚 **Prolog Implementations**

- **Comprehensive with 5 approaches**: https://github.com/lanzv/RubikSolver
  - BFS, 3 A* variants, human algorithm
  - BEST for comparing different approaches
  
- **Classic by Dennis Merritt**: https://www.amzi.com/articles/rubik.htm
  - Educational article on Prolog approach

---

## 📖 **Academic Theses**

- **KTH Royal Institute (Sweden)**: https://www.diva-portal.org/smash/get/diva2:816583/FULLTEXT01.pdf
  - Compares Thistlethwaite vs IDA*
  - Bachelor level, very relevant!

- **University of Linz (Austria)**: http://www.algebra.uni-linz.ac.at/Projects/FurtherProjects/Kainberger/Using_Group_Theory_for_solving_Rubik's_Cube.pdf
  - Group theory approach

---

## 🧮 **Mathematical Foundations & Theory**

### Group Theory Course Materials
- **MIT SP.268**: https://web.mit.edu/sp.268/www/rubik.pdf
  - Complete introduction via Rubik's Cube
  
- **Harvard notes**: http://people.math.harvard.edu/~jjchen/docs/Group%20Theory%20and%20the%20Rubik's%20Cube.pdf

### Technical Documentation
- **Kociemba's official site**: https://kociemba.org/math/twophase.htm
  - Two-phase algorithm details
  - Cube Explorer software: https://kociemba.org/cube.htm

- **Jaap's Puzzle Page** (INCREDIBLY DETAILED):
  - Thistlethwaite algorithm: https://www.jaapsch.net/puzzles/thistle.htm
  - Computer solving overview: https://www.jaapsch.net/puzzles/compcube.htm

- **Cubing History**: https://www.cubinghistory.com/3x3/3x3ComputerAlgorithms

---

## 🤖 **Machine Learning Approaches (Modern)**

### Deep Reinforcement Learning
- **DeepCubeA (Nature 2019)**: https://www.nature.com/articles/s42256-019-0070-z
  - Near-optimal with deep RL + A*
  
- **Solving Without Human Knowledge**: https://arxiv.org/abs/1805.07470
  - Pure self-learning approach

- **Recent 2024 papers**:
  - Without tricky sampling: https://arxiv.org/html/2411.19583v1
  - Using graph structure: https://arxiv.org/html/2408.07945v1

### Implementation
- **DRL + A* hybrid**: https://github.com/yakupbilen/drl-rubiks-cube

---

## 🔍 **Stack Overflow Q&A (Implementation Help)**

- **Pattern database creation**: https://stackoverflow.com/questions/58860280/how-to-create-a-pattern-database-for-solving-rubiks-cube
- **Heuristic functions for A***: https://stackoverflow.com/questions/60130124/heuristic-function-for-rubiks-cube-in-a-algorithm-artificial-intelligence
- **Algorithm complexity discussion**: https://cs.stackexchange.com/questions/167182/time-complexity-o-notation-for-kociemba-korf-and-thistlethwaites-algorithms

---

## 📊 **Comparison & Analysis Tools**

- **Algorithm comparison framework**: https://github.com/The-Semicolons/AnalysisofRubiksCubeSolvingAlgorithm
  - Compares Thistlethwaite, Kociemba, Korf, Rokicki
  - Time/space complexity analysis

- **Multiple algorithms in Python**: https://github.com/BenSDuggan/CubeAI
  - BFS, A*, IDA*, MiniMax
  - Different heuristics
  - pygame visualization

---

## 📕 **Book**

- **Adventures in Group Theory** by David Joyner
  - Amazon: https://www.amazon.com/Adventures-Group-Theory-Merlins-Mathematical/dp/0801890136
  - Johns Hopkins Press: https://www.press.jhu.edu/books/title/9554/adventures-group-theory

---

## 🌐 **Wikipedia & General Resources**

- **Optimal solutions article**: https://en.wikipedia.org/wiki/Optimal_solutions_for_the_Rubik%27s_Cube
- **Rubik's Cube main**: https://en.wikipedia.org/wiki/Rubik%27s_Cube
- **Notation guide**: https://ruwix.com/the-rubiks-cube/notation/
- **Speedsolving wiki**: https://www.speedsolving.com/wiki/index.php/Kociemba's_Algorithm

---

## 🎯 **PRIORITY RECOMMENDATIONS FOR YOUR THESIS**

### Start Here (Foundation):
1. **Korf's paper**: https://www.cs.princeton.edu/courses/archive/fall06/cos402/papers/korfrubik.pdf
2. **God's Number**: http://www.cube20.org/
3. **Wikipedia overview**: https://en.wikipedia.org/wiki/Optimal_solutions_for_the_Rubik%27s_Cube
4. **MIT group theory notes**: https://web.mit.edu/sp.268/www/rubik.pdf

### For Implementation:
1. **Kociemba Python**: https://github.com/hkociemba/RubiksCube-TwophaseSolver
2. **Korf Python**: https://github.com/hkociemba/RubiksCube-OptimalSolver
3. **Thistlethwaite C++**: https://github.com/benbotto/rubiks-cube-cracker
4. **Pattern database help**: https://stackoverflow.com/questions/58860280

### For A* Heuristics:
1. **Korf's pattern database paper** (same as above)
2. **Heuristic discussion**: https://stackoverflow.com/questions/60130124
3. **Jaap's technical page**: https://www.jaapsch.net/puzzles/compcube.htm

### For Comparison/Analysis:
1. **KTH thesis**: https://www.diva-portal.org/smash/get/diva2:816583/FULLTEXT01.pdf
2. **Algorithm comparison**: https://github.com/The-Semicolons/AnalysisofRubiksCubeSolvingAlgorithm

All these sources are verified and working. Good luck with your thesis! 🎓