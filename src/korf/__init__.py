"""
Korf's Pattern Database Distance Estimator

This module implements pattern database-based distance estimation for Rubik's Cube,
following Richard Korf's approach from his 1997 paper "Finding Optimal Solutions
to Rubik's Cube Using Pattern Databases".

Main Components:
- Pattern Databases: Precomputed distances for corner and edge subsets
- Heuristic Functions: Manhattan, Hamming, and simple heuristics
- Distance Estimator: Combines databases and heuristics for accurate estimates

Usage Example:
    from src.korf import create_estimator
    from src.cube.rubik_cube import RubikCube

    # Create estimator (will load/generate databases)
    estimator = create_estimator(load_databases=True)

    # Estimate distance for a scrambled cube
    cube = RubikCube()
    cube.scramble(20)
    distance = estimator.estimate(cube)
    print(f"Estimated distance: {distance}")

References:
- Korf, R. (1997). Finding Optimal Solutions to Rubik's Cube Using Pattern Databases
- Culberson, J. & Schaeffer, J. (1998). Pattern Databases
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
]
