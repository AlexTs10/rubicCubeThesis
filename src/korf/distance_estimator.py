"""
Distance Estimator for Rubik's Cube

This module provides a comprehensive distance estimation system that combines:
1. Pattern databases (corners and edges)
2. Multiple heuristic functions
3. Optimal combining strategies

The main estimator uses max(corner_db, edge1_db, edge2_db) as the primary
estimate, which provides an admissible lower bound on the actual distance.

Usage:
    estimator = DistanceEstimator()
    estimator.load_databases()  # Load or generate pattern databases

    cube = RubikCube()
    cube.scramble(20)

    # Get distance estimate
    distance = estimator.estimate(cube)

    # Get detailed breakdown
    details = estimator.estimate_detailed(cube)

References:
- Korf (1997): Pattern database combining strategies
- Culberson & Schaeffer (1998): Additive pattern databases
"""

import numpy as np
from typing import Dict, Optional, Tuple
from ..cube.rubik_cube import RubikCube
from ..kociemba.cubie import from_facelet_cube, CubieCube
from .pattern_database import PatternDatabase
from .corner_database import CornerPatternDatabase, create_corner_database
from .edge_database import EdgePatternDatabase, create_edge_database
from .heuristics import (
    simple_heuristic,
    hamming_distance,
    manhattan_distance,
    manhattan_distance_corner,
    manhattan_distance_edge,
    HeuristicEvaluator
)


class DistanceEstimator:
    """
    Comprehensive distance estimator for Rubik's Cube.

    This class provides multiple estimation strategies:
    1. Pattern database estimates (corner, edge1, edge2)
    2. Combined pattern database estimate: max(corner, edge1, edge2)
    3. Alternative heuristics (Manhattan, Hamming, simple)
    """

    def __init__(self,
                 corner_db: Optional[CornerPatternDatabase] = None,
                 edge1_db: Optional[EdgePatternDatabase] = None,
                 edge2_db: Optional[EdgePatternDatabase] = None):
        """
        Initialize the distance estimator.

        Args:
            corner_db: Corner pattern database (optional)
            edge1_db: First edge pattern database (optional)
            edge2_db: Second edge pattern database (optional)
        """
        self.corner_db = corner_db
        self.edge1_db = edge1_db
        self.edge2_db = edge2_db
        self.heuristic_eval = HeuristicEvaluator()

        self.use_pattern_dbs = False

    def load_databases(self,
                       load_corner: bool = True,
                       load_edges: bool = True,
                       corner_path: str = None,
                       edge1_path: str = None,
                       edge2_path: str = None,
                       generate_if_missing: bool = True) -> None:
        """
        Load pattern databases from disk or generate them.

        Args:
            load_corner: Whether to load corner database
            load_edges: Whether to load edge databases
            corner_path: Path to corner database
            edge1_path: Path to first edge database
            edge2_path: Path to second edge database
            generate_if_missing: If True, generate databases if not found
        """
        print("Loading pattern databases...")

        if load_corner:
            try:
                self.corner_db = create_corner_database(
                    load_if_exists=True,
                    save_path=corner_path
                )
                print("✓ Corner database loaded")
            except Exception as e:
                if generate_if_missing:
                    print(f"! Corner database not found, generating...")
                    self.corner_db = create_corner_database(
                        load_if_exists=False,
                        save_path=corner_path
                    )
                else:
                    print(f"✗ Failed to load corner database: {e}")

        if load_edges:
            try:
                self.edge1_db = create_edge_database(
                    edge_group=1,
                    load_if_exists=True,
                    save_path=edge1_path
                )
                print("✓ Edge1 database loaded")
            except Exception as e:
                if generate_if_missing:
                    print(f"! Edge1 database not found, generating...")
                    self.edge1_db = create_edge_database(
                        edge_group=1,
                        load_if_exists=False,
                        save_path=edge1_path
                    )
                else:
                    print(f"✗ Failed to load edge1 database: {e}")

            try:
                self.edge2_db = create_edge_database(
                    edge_group=2,
                    load_if_exists=True,
                    save_path=edge2_path
                )
                print("✓ Edge2 database loaded")
            except Exception as e:
                if generate_if_missing:
                    print(f"! Edge2 database not found, generating...")
                    self.edge2_db = create_edge_database(
                        edge_group=2,
                        load_if_exists=False,
                        save_path=edge2_path
                    )
                else:
                    print(f"✗ Failed to load edge2 database: {e}")

        # Update flag
        self.use_pattern_dbs = (
            self.corner_db is not None or
            self.edge1_db is not None or
            self.edge2_db is not None
        )

        if self.use_pattern_dbs:
            print("Pattern databases ready!")
        else:
            print("Warning: No pattern databases loaded, will use heuristics only")

    def estimate_from_pattern_dbs(self, cubie: CubieCube) -> Tuple[int, Dict[str, int]]:
        """
        Estimate distance using pattern databases.

        Uses max(corner_db, edge1_db, edge2_db) strategy.

        Args:
            cubie: Cubie cube state

        Returns:
            Tuple of (max_distance, individual_distances_dict)
        """
        distances = {}

        if self.corner_db is not None:
            distances['corner'] = self.corner_db.get_corner_distance(cubie)

        if self.edge1_db is not None:
            distances['edge1'] = self.edge1_db.get_edge_distance(cubie)

        if self.edge2_db is not None:
            distances['edge2'] = self.edge2_db.get_edge_distance(cubie)

        if not distances:
            raise ValueError("No pattern databases available")

        max_distance = max(distances.values())

        return max_distance, distances

    def estimate(self, cube: RubikCube, method: str = 'pattern_db') -> float:
        """
        Estimate the distance to solve a cube.

        Args:
            cube: Rubik's cube state
            method: Estimation method ('pattern_db', 'manhattan', 'hamming', 'simple')

        Returns:
            Distance estimate (lower bound on actual distance)
        """
        if cube.is_solved():
            return 0.0

        if method == 'pattern_db':
            if not self.use_pattern_dbs:
                raise ValueError("Pattern databases not loaded. Call load_databases() first.")

            cubie = from_facelet_cube(cube)
            distance, _ = self.estimate_from_pattern_dbs(cubie)
            return float(distance)

        elif method in ['manhattan', 'hamming', 'simple']:
            return self.heuristic_eval.evaluate(cube, method)

        else:
            raise ValueError(f"Unknown method: {method}")

    def estimate_detailed(self, cube: RubikCube) -> Dict:
        """
        Get detailed distance estimates using all available methods.

        Args:
            cube: Rubik's cube state

        Returns:
            Dictionary with detailed estimates
        """
        result = {
            'is_solved': cube.is_solved(),
            'pattern_db': None,
            'pattern_db_breakdown': {},
            'heuristics': {}
        }

        if cube.is_solved():
            result['pattern_db'] = 0
            result['heuristics'] = {name: 0.0 for name in ['simple', 'hamming', 'manhattan']}
            return result

        # Get pattern database estimates
        if self.use_pattern_dbs:
            try:
                cubie = from_facelet_cube(cube)
                distance, breakdown = self.estimate_from_pattern_dbs(cubie)
                result['pattern_db'] = distance
                result['pattern_db_breakdown'] = breakdown
            except Exception as e:
                result['pattern_db_error'] = str(e)

        # Get heuristic estimates
        result['heuristics'] = self.heuristic_eval.evaluate_all(cube)

        return result

    def compare_methods(self, cube: RubikCube, actual_distance: Optional[int] = None) -> None:
        """
        Compare all estimation methods on a cube state.

        Args:
            cube: Rubik's cube state
            actual_distance: Optional actual distance for error calculation
        """
        print("=" * 60)
        print("Distance Estimation Comparison")
        print("=" * 60)

        details = self.estimate_detailed(cube)

        print(f"Cube state: {'SOLVED' if details['is_solved'] else 'SCRAMBLED'}")
        if actual_distance is not None:
            print(f"Actual distance: {actual_distance}")
        print()

        # Pattern database estimates
        if details['pattern_db'] is not None:
            print("Pattern Database Estimates:")
            print(f"  Combined (max): {details['pattern_db']}")
            for name, dist in details['pattern_db_breakdown'].items():
                print(f"    {name:10s}: {dist}")
                if actual_distance is not None:
                    error = abs(dist - actual_distance)
                    print(f"              error: {error}")
            print()

        # Heuristic estimates
        print("Heuristic Estimates:")
        for name, estimate in sorted(details['heuristics'].items()):
            print(f"  {name:15s}: {estimate:.2f}")
            if actual_distance is not None:
                error = abs(estimate - actual_distance)
                print(f"                   error: {error:.2f}")

        print("=" * 60)

    def get_statistics(self) -> Dict:
        """
        Get statistics about loaded databases.

        Returns:
            Dictionary with database statistics
        """
        stats = {
            'databases_loaded': self.use_pattern_dbs,
            'corner_db': None,
            'edge1_db': None,
            'edge2_db': None
        }

        if self.corner_db is not None:
            stats['corner_db'] = self.corner_db.get_statistics()

        if self.edge1_db is not None:
            stats['edge1_db'] = self.edge1_db.get_statistics()

        if self.edge2_db is not None:
            stats['edge2_db'] = self.edge2_db.get_statistics()

        return stats


def create_estimator(load_databases: bool = True,
                     generate_if_missing: bool = False) -> DistanceEstimator:
    """
    Create a distance estimator with optional database loading.

    Args:
        load_databases: Whether to load pattern databases
        generate_if_missing: Whether to generate databases if not found

    Returns:
        Configured distance estimator
    """
    estimator = DistanceEstimator()

    if load_databases:
        estimator.load_databases(generate_if_missing=generate_if_missing)

    return estimator
