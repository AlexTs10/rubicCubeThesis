"""
Korf's Pattern Database Distance Estimator + A* Algorithms

This module implements pattern-database-backed and lightweight distance
estimation utilities for Rubik's Cube, following parts of Richard Korf's
pattern database approach from his 1997 paper.

Main Components:
- Pattern Databases: Precomputed distances for corner and edge subsets
- Heuristic Functions: Manhattan, Hamming, simple, and composite estimates
- Distance Estimator: Combines databases and lightweight heuristics
- A* and IDA* Solvers: Search algorithms with configurable heuristics
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
    heuristic = create_heuristic('composite', use_pattern_db=True)
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
from .native_exact_solver import (
    NativeExactSolver,
    solve_exact_native,
    solve_optimal_native,
    optimal_distance_native,
    zero_heuristic,
    make_corner_heuristic,
)
from .native_coordinate_heuristic import (
    NativeCoordinateHeuristic,
    create_native_coordinate_heuristic,
)
from .composite_heuristic import (
    CompositeHeuristic,
    WeightedCompositeHeuristic,
    StateAnalyzer,
    create_heuristic
)

_OPTIONAL_COMPARISON_EXPORTS = []
try:
    from .solver_comparison import (
        SolverComparison,
        SolveResult,
        ComparisonSummary,
        run_quick_comparison,
        run_full_comparison
    )
    _OPTIONAL_COMPARISON_EXPORTS = [
        'SolverComparison',
        'SolveResult',
        'ComparisonSummary',
        'run_quick_comparison',
        'run_full_comparison',
    ]
except ModuleNotFoundError:  # pragma: no cover - depends on optional psutil
    pass
_LAZY_EXPORTS = {
    'KorfOptimalSolver': ('optimal_solver', 'KorfOptimalSolver'),
    'solve_optimal': ('optimal_solver', 'solve_optimal'),
}


def __getattr__(name):
    """Lazily resolve optional optimal-solver exports."""
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _LAZY_EXPORTS[name]
    module = __import__(f"{__name__}.{module_name}", fromlist=[attr_name])
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    """Expose lazily loaded names for interactive use."""
    return sorted(set(globals()) | set(_LAZY_EXPORTS))

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

    # Native Exact Solver
    'NativeExactSolver',
    'solve_exact_native',
    'solve_optimal_native',
    'optimal_distance_native',
    'zero_heuristic',
    'make_corner_heuristic',
    'NativeCoordinateHeuristic',
    'create_native_coordinate_heuristic',

    # Composite Heuristics
    'CompositeHeuristic',
    'WeightedCompositeHeuristic',
    'StateAnalyzer',
    'create_heuristic',

    # Optimal Solver
    'KorfOptimalSolver',
    'solve_optimal',
]

__all__.extend(_OPTIONAL_COMPARISON_EXPORTS)
