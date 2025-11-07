"""
Korf's Pattern Database Distance Estimator + A* Algorithms

This module implements pattern database-based distance estimation for Rubik's Cube,
following Richard Korf's approach from his 1997 paper "Finding Optimal Solutions
to Rubik's Cube Using Pattern Databases".

Main Components:
- Pattern Databases: Precomputed distances for corner and edge subsets
- Heuristic Functions: Manhattan, Hamming, simple, and novel composite heuristics
- Distance Estimator: Combines databases and heuristics for accurate estimates
- A* and IDA* Solvers: Optimal solving algorithms with heuristics
- Solver Comparison: Framework for comparing A* vs IDA* performance

Usage Example:
    from src.korf import create_estimator, AStarSolver, IDAStarSolver
    from src.korf.composite_heuristic import create_heuristic
    from src.cube.rubik_cube import RubikCube

    # Create estimator (will load/generate databases)
    estimator = create_estimator(load_databases=True)

    # Estimate distance for a scrambled cube
    cube = RubikCube()
    cube.scramble(20)
    distance = estimator.estimate(cube)
    print(f"Estimated distance: {distance}")

    # Solve with A* and composite heuristic
    heuristic = create_heuristic('composite')
    solver = AStarSolver(heuristic=heuristic, max_depth=20)
    solution = solver.solve(cube)

References:
- Korf, R. (1997). Finding Optimal Solutions to Rubik's Cube Using Pattern Databases
- Culberson, J. & Schaeffer, J. (1998). Pattern Databases
- Korf, R. (1985). Depth-first Iterative-Deepening: An Optimal Admissible Tree Search
"""

from .pattern_database import PatternDatabase, bfs_generate_pattern_database
from .corner_database import (
    CornerPatternDatabase,
    create_corner_database,
    corner_index,
    CORNER_DB_SIZE
)
from .edge_database import (
    EdgePatternDatabase,
    create_edge_database,
    EDGE_GROUP_1,
    EDGE_GROUP_2
)
from .heuristics import (
    simple_heuristic,
    hamming_distance,
    manhattan_distance,
    manhattan_distance_corner,
    manhattan_distance_edge,
    HeuristicEvaluator
)
from .distance_estimator import (
    DistanceEstimator,
    create_estimator
)
from .a_star import (
    AStarSolver,
    IDAStarSolver,
    SearchNode
)
from .composite_heuristic import (
    CompositeHeuristic,
    WeightedCompositeHeuristic,
    StateAnalyzer,
    create_heuristic
)
from .solver_comparison import (
    SolverComparison,
    SolveResult,
    ComparisonSummary,
    run_quick_comparison,
    run_full_comparison
)
from .optimal_solver import (
    KorfOptimalSolver,
    solve_optimal
)

__all__ = [
    # Pattern Database Infrastructure
    'PatternDatabase',
    'bfs_generate_pattern_database',

    # Corner Database
    'CornerPatternDatabase',
    'create_corner_database',
    'corner_index',
    'CORNER_DB_SIZE',

    # Edge Database
    'EdgePatternDatabase',
    'create_edge_database',
    'EDGE_GROUP_1',
    'EDGE_GROUP_2',

    # Heuristics
    'simple_heuristic',
    'hamming_distance',
    'manhattan_distance',
    'manhattan_distance_corner',
    'manhattan_distance_edge',
    'HeuristicEvaluator',

    # Distance Estimator
    'DistanceEstimator',
    'create_estimator',

    # A* and IDA* Solvers
    'AStarSolver',
    'IDAStarSolver',
    'SearchNode',

    # Composite Heuristics
    'CompositeHeuristic',
    'WeightedCompositeHeuristic',
    'StateAnalyzer',
    'create_heuristic',

    # Solver Comparison
    'SolverComparison',
    'SolveResult',
    'ComparisonSummary',
    'run_quick_comparison',
    'run_full_comparison',

    # Optimal Solver
    'KorfOptimalSolver',
    'solve_optimal',
]
