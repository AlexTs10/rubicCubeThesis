# Code-to-Thesis Mapping

> Working reference, updated for the March 2026 verification pass. For publication-facing benchmark claims, use `results/benchmarks/thesis/thesis_results_combined.json` and `thesis/chapters/07_evaluation.tex` as the source of truth.

Quick reference: what code to cite for each thesis section.

---

## Chapter 2: Theoretical Background

### Cube Representation
| Topic | File | Key Functions/Classes |
|-------|------|----------------------|
| Facelet model | `src/cube/rubik_cube.py` | `RubikCube`, `Face`, `Color` |
| Move application | `src/cube/rubik_cube.py` / `src/cube/moves.py` | `RubikCube.apply_move()`, `RubikCube.apply_moves()`, `inverse_move()` |
| Singmaster notation | `src/cube/moves.py` | `parse_move_sequence()`, `format_move_sequence()` |
| Cubie model | `src/kociemba/cubie.py` | `CubieCube`, `Corner`, `Edge` |

### Search Algorithms
| Topic | File | Key Functions |
|-------|------|---------------|
| A* implementation | `src/korf/a_star.py` | `AStarSolver.solve()` |
| IDA* implementation | `src/korf/a_star.py` | `IDAStarSolver.solve()` |
| Pattern databases | `src/korf/pattern_database.py` | `PatternDatabase` class |

---

## Chapter 3: Thistlethwaite Algorithm

| Topic | File | What to Reference |
|-------|------|-------------------|
| Main solver | `src/thistlethwaite/solver.py` | `ThistlethwaiteSolver` class |
| Phase definitions | `src/thistlethwaite/moves.py` | `PHASE_0_MOVES`, `PHASE_1_MOVES`, `PHASE_2_MOVES`, `PHASE_3_MOVES`, `ALL_PHASE_MOVES` |
| Coordinates | `src/thistlethwaite/coordinates.py` | `CubeCoordinates.get_edge_orientation_coord()`, `CubeCoordinates.get_corner_orientation_coord()`, `CubeCoordinates.get_e_slice_coord()` |
| IDA* search | `src/thistlethwaite/ida_star.py` | `IDAStarSearch.search()` |
| Pattern tables | `src/thistlethwaite/tables.py` | Table generation functions |

**Test data:**
- `tests/unit/test_thistlethwaite.py` - 35 test cases

---

## Chapter 4: Kociemba Algorithm

| Topic | File | What to Reference |
|-------|------|-------------------|
| Main solver | `src/kociemba/solver.py` | `KociembaSolver` class |
| Cubie representation | `src/kociemba/cubie.py` | `CubieCube` class |
| Coordinates | `src/kociemba/coord.py` | `CoordCube`, coordinate functions |
| Move tables | `src/kociemba/moves.py` | `MoveTables` class |
| Pruning tables | `src/kociemba/pruning.py` | `PruningTables` class |

**Key code snippet for thesis (Phase 1 check):**
```python
# From src/kociemba/coord.py
def is_phase1_solved(coord_cube):
    """Check if cube is in G1 subgroup"""
    return (coord_cube.corner_orient == 0 and
            coord_cube.edge_orient == 0 and
            coord_cube.ud_slice == 0)
```

**Test data:**
- `tests/unit/test_kociemba.py` - 25 test cases

---

## Chapter 5: Korf Algorithm

| Topic | File | What to Reference |
|-------|------|-------------------|
| Exact benchmark solver | `src/korf/optimal_solver.py` | `KorfOptimalSolver` |
| Native exact solver | `src/korf/native_exact_solver.py` | `NativeExactSolver`, `solve_exact_native()`, `optimal_distance_native()` |
| Native admissible heuristic | `src/korf/native_coordinate_heuristic.py` | `NativeCoordinateHeuristic` |
| Internal heuristic search | `src/korf/a_star.py` | `IDAStarSolver` |
| Pattern database base | `src/korf/pattern_database.py` | `PatternDatabase` class |
| Corner database | `src/korf/corner_database.py` | `CornerPatternDatabase` |
| Edge database | `src/korf/edge_database.py` | `EdgePatternDatabase` |
| Heuristic functions | `src/korf/heuristics.py` | Exploratory / low-cost heuristics |
| Composite heuristic | `src/korf/composite_heuristic.py` | Exploratory composite path |

**Key distinction:**
```python
# Exact benchmark claims use the external optimal backend.
solver = KorfOptimalSolver()

# Native exact claims use the repository-native API and validation corpus.
distance = optimal_distance_native(cube)

# Internal lightweight heuristics remain useful for experiments,
# but are not the basis for exact optimality claims.
```

**Test data:**
- `tests/unit/test_a_star_solvers.py`
- `tests/unit/test_native_exact_solver.py`
- `tests/unit/test_native_coordinate_heuristic.py`
- `tests/integration/test_native_exact_oracle_agreement.py`

---

## Chapter 6: Distance Estimation & Heuristics

| Topic | File | What to Reference |
|-------|------|-------------------|
| Distance estimator | `src/korf/distance_estimator.py` | `DistanceEstimator` class |
| Basic heuristics | `src/korf/heuristics.py` | `hamming_distance()`, `manhattan_distance()` |
| Composite heuristic | `src/korf/composite_heuristic.py` | `CompositeHeuristic` class |
| State analyzer | `src/korf/composite_heuristic.py` | `StateAnalyzer` class |
| Heuristic factory | `src/korf/composite_heuristic.py` | `HeuristicFactory` |

**Exploratory composite heuristic:**
```python
# From src/korf/composite_heuristic.py
class CompositeHeuristic:
    """Adaptive heuristic for exploratory state-aware estimates"""
    def __call__(self, cube):
        entropy = self.analyzer.calculate_entropy(cube)
        # Select a practical heuristic strategy based on state characteristics
        ...
```

**Test data:**
- `tests/unit/test_composite_heuristic.py` - 25 test cases
- `tests/unit/test_distance_estimator.py` - 21 test cases

---

## Chapter 7: Experimental Evaluation

### Benchmark Data
| Data | File |
|------|------|
| Combined JSON results | `results/benchmarks/thesis/thesis_results_combined.json` |
| Per-depth JSON results | `results/benchmarks/thesis/thesis_bench_d5.json` etc. |
| Native exact validation manifest | `results/validation/native_exact/MANIFEST.json` |
| Native exact validation reports | `results/validation/native_exact/native_exact_validation_*.json` |

### Figures (ready to use)
| Figure | File | Use For |
|--------|------|---------|
| Solution lengths | `thesis/figures/fig1_solution_length_boxplot.png` | Algorithm comparison |
| Time comparison | `thesis/figures/fig2_time_comparison.png` | Performance analysis |
| Memory comparison | `thesis/figures/fig3_memory_comparison.png` | Resource usage |
| Success rate | `thesis/figures/fig4_success_rate.png` | Reliability |
| Solution distribution | `thesis/figures/fig5_solution_distribution.png` | Quality analysis |
| Nodes expanded | `thesis/figures/fig6_nodes_comparison.png` | Search cost |
| Performance vs depth | `thesis/figures/fig7_performance_vs_depth.png` | Scalability |

### Scripts for Generating Data
| Purpose | Script |
|---------|--------|
| Regenerate thesis benchmark set | `scripts/benchmarks/regenerate_thesis_benchmarks.py` |
| LaTeX tables | `scripts/benchmarks/generate_latex_tables.py` |
| Analysis | `scripts/benchmarks/analyze_thesis_data.py` |
| Native exact validation | `scripts/verification/native_exact_validation.py` |

---

## Chapter 8: Implementation

### Project Structure
```
src/
├── cube/                 # Ch. 2 - Cube representation
│   ├── rubik_cube.py     # Main cube class
│   ├── moves.py          # Move definitions
│   └── visualization.py  # Visualization helpers
├── thistlethwaite/       # Ch. 3 - Thistlethwaite
│   ├── solver.py
│   ├── coordinates.py
│   └── tables.py
├── kociemba/             # Ch. 4 - Kociemba
│   ├── solver.py
│   ├── cubie.py
│   ├── coord.py
│   └── pruning.py
├── korf/                 # Ch. 5-6 - Korf & Heuristics
│   ├── a_star.py
│   ├── pattern_database.py
│   ├── native_exact_solver.py
│   ├── native_coordinate_heuristic.py
│   ├── composite_heuristic.py
│   └── distance_estimator.py
└── evaluation/           # Ch. 7 - Evaluation
    └── algorithm_comparison.py
```

Current verification commands for this checkout:

- Source and test file counts are reported by `python scripts/thesis_workflow.py status`.
- Full pytest collection is reported by `python -m pytest tests --collect-only -q`.
- The default fast profile is controlled by `pytest.ini`, which excludes `slow`, `external`, and `cache_building` tests unless explicitly selected.

### Web Applications
| App | Location | Technology |
|-----|----------|------------|
| Interactive webapp | `webapp/` | Next.js, React, Three.js |
| Educational UI | `ui/` | Streamlit |

### Test Suite
| Module | Tests | File |
|--------|-------|------|
| Thistlethwaite | covered | `tests/unit/test_thistlethwaite.py` |
| Kociemba | covered | `tests/unit/test_kociemba.py` |
| A* solvers | covered | `tests/unit/test_a_star_solvers.py` |
| Native exact solver | covered | `tests/unit/test_native_exact_solver.py` |
| Native coordinate heuristic | covered | `tests/unit/test_native_coordinate_heuristic.py` |
| Heuristics | covered | `tests/unit/test_composite_heuristic.py` |
| Distance estimator | covered | `tests/unit/test_distance_estimator.py` |
| Integration workflows | covered | `tests/integration/test_workflows.py` |

---

## Demo Scripts (for Appendix/Screenshots)

| Demo | Script | Shows |
|------|--------|-------|
| Basic usage | `demos/basic_usage.py` | Cube creation, moves |
| Thistlethwaite | `demos/thistlethwaite_demo.py` | Algorithm in action |
| Kociemba | `demos/kociemba_demo.py` | Two-phase solving |
| A* comparison | `demos/a_star_comparison_demo.py` | A* vs IDA* |
| Distance estimator | `demos/distance_estimator_demo.py` | Heuristic comparison |
| Visualization | `demos/visualization_demo.py` | 2D/3D cube display |

---

## Jupyter Notebooks (Educational Content)

| Notebook | Content | Use in Thesis |
|----------|---------|---------------|
| `01_Introduction.ipynb` | Cube basics | Ch. 1-2 examples |
| `02_Thistlethwaite.ipynb` | Algorithm walkthrough | Ch. 3 examples |
| `03_Kociemba.ipynb` | Two-phase explanation | Ch. 4 examples |
| `04_Korf.ipynb` | Optimal solving | Ch. 5 examples |
| `05_Algorithm_Comparison.ipynb` | Benchmarks | Ch. 7 data |
| `06_Conclusion.ipynb` | Summary | Ch. 9 summary |

---

## Quick Stats to Cite

```text
Corrected thesis benchmark (100 scrambles, depths 5/10/15/20):
- Thistlethwaite: 100/100 solved, avg 23.62 moves, avg 1.24s
- Kociemba: 100/100 solved, avg 14.33 moves, avg 4.62s
- Korf exact backend: 97/100 solved, avg 9.12 moves on completed runs, 3 requested scramble length 20 timeouts

Important wording:
- Thistlethwaite benchmark path is pure (no fallback)
- Kociemba is the best overall practical compromise
- Korf is exact when solved within the enforced timeout
- CompositeHeuristic is exploratory and not a blanket admissible guarantee
```
