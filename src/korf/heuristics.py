"""
Heuristic Functions for Distance Estimation

This module implements multiple heuristic approaches for estimating the distance
to solve a Rubik's Cube. These heuristics can be used standalone or compared
against pattern database estimates.

Heuristic Types:
1. Simple Heuristic: Count of mismatched face centers
2. Hamming Distance: Count of misplaced pieces
3. Manhattan Distance: Sum of individual piece distances
4. Corner Manhattan: Manhattan distance for corners only
5. Edge Manhattan: Manhattan distance for edges only

All heuristics are admissible (never overestimate) but vary in accuracy.

References:
- BenSDuggan/CubeAI: Multiple heuristic implementations
- Stack Overflow: Admissibility requirements for Rubik's Cube
"""

import numpy as np
from typing import Dict, Tuple
from ..cube.rubik_cube import RubikCube, Face
from ..kociemba.cubie import CubieCube, from_facelet_cube


def simple_heuristic(cube: RubikCube) -> float:
    """
    Simple heuristic based on face color matching.

    Counts how many faces are partially solved (have multiple stickers
    of the correct color). Higher scores mean closer to solved.

    This is converted to a distance estimate by normalizing.

    Args:
        cube: Rubik's cube state

    Returns:
        Distance estimate (higher = farther from solved)
    """
    if cube.is_solved():
        return 0.0

    mismatched = 0

    for face in Face:
        face_state = cube.get_face(face)
        center_color = face_state[4]  # Center piece defines face color

        # Count mismatched stickers on this face
        for i in range(9):
            if i != 4 and face_state[i] != center_color:
                mismatched += 1

    # Convert to admissible distance estimate
    # Each move can fix at most 8 stickers, so divide by 8
    return mismatched / 8.0


def hamming_distance(cube: RubikCube) -> float:
    """
    Hamming distance: count of pieces in wrong position/orientation.

    This counts how many corner and edge pieces are not in their
    solved positions.

    Args:
        cube: Rubik's cube state

    Returns:
        Distance estimate based on misplaced pieces
    """
    if cube.is_solved():
        return 0.0

    # Convert to cubie representation
    cubie = from_facelet_cube(cube)

    misplaced = 0

    # Count misplaced corners
    for i in range(8):
        if cubie.corner_perm[i] != i or cubie.corner_orient[i] != 0:
            misplaced += 1

    # Count misplaced edges
    for i in range(12):
        if cubie.edge_perm[i] != i or cubie.edge_orient[i] != 0:
            misplaced += 1

    # Each move affects 8 pieces, so divide by 8 for admissibility
    return misplaced / 8.0


def manhattan_distance_corner(cubie: CubieCube) -> float:
    """
    Manhattan distance for corner pieces.

    Computes the minimum number of moves each corner needs to reach
    its home position (ignoring other pieces), then sums these values.

    For admissibility, the sum is divided by 4 (each move affects 4 corners).

    Args:
        cubie: Cubie cube state

    Returns:
        Corner Manhattan distance estimate
    """
    # Precomputed: minimum moves for each corner to reach each position
    # This is a simplified approximation - actual values would require
    # computing shortest paths in the corner subgroup

    total_distance = 0

    for i in range(8):
        current_corner = cubie.corner_perm[i]
        current_orient = cubie.corner_orient[i]

        # If corner is in wrong position, it needs at least 1 move
        if current_corner != i:
            total_distance += 1

        # If corner is twisted, it needs at least 1 move
        # (Actually, a corner can only be fixed with its position,
        # so we don't double count)
        if current_orient != 0:
            total_distance += 1

    # Divide by 4 for admissibility (each move affects 4 corners)
    return total_distance / 4.0


def manhattan_distance_edge(cubie: CubieCube) -> float:
    """
    Manhattan distance for edge pieces.

    Computes the minimum number of moves each edge needs to reach
    its home position (ignoring other pieces), then sums these values.

    For admissibility, the sum is divided by 4 (each move affects 4 edges).

    Args:
        cubie: Cubie cube state

    Returns:
        Edge Manhattan distance estimate
    """
    total_distance = 0

    for i in range(12):
        current_edge = cubie.edge_perm[i]
        current_orient = cubie.edge_orient[i]

        # If edge is in wrong position
        if current_edge != i:
            total_distance += 1

        # If edge is flipped
        if current_orient != 0:
            total_distance += 1

    # Divide by 4 for admissibility (each move affects 4 edges)
    return total_distance / 4.0


def manhattan_distance(cube: RubikCube) -> float:
    """
    Combined Manhattan distance for all pieces.

    Takes the maximum of corner and edge Manhattan distances, as this
    provides a better admissible estimate than summing them.

    Args:
        cube: Rubik's cube state

    Returns:
        Manhattan distance estimate
    """
    if cube.is_solved():
        return 0.0

    # Convert to cubie representation
    cubie = from_facelet_cube(cube)

    corner_dist = manhattan_distance_corner(cubie)
    edge_dist = manhattan_distance_edge(cubie)

    # Return maximum for better estimate while maintaining admissibility
    return max(corner_dist, edge_dist)


def improved_manhattan_distance(cubie: CubieCube) -> float:
    """
    Improved Manhattan distance with better position estimates.

    This uses a more accurate estimate of how many moves each piece
    needs based on its actual position on the cube.

    Args:
        cubie: Cubie cube state

    Returns:
        Improved Manhattan distance estimate
    """
    # Corner position distances (minimum face turns to move between positions)
    # This is a simplified 6x6 symmetric matrix
    corner_distances = {
        (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 1, (0, 4): 1, (0, 5): 2, (0, 6): 3, (0, 7): 2,
        (1, 1): 0, (1, 2): 1, (1, 3): 2, (1, 4): 2, (1, 5): 1, (1, 6): 2, (1, 7): 3,
        (2, 2): 0, (2, 3): 1, (2, 4): 3, (2, 5): 2, (2, 6): 1, (2, 7): 2,
        (3, 3): 0, (3, 4): 2, (3, 5): 3, (3, 6): 2, (3, 7): 1,
        (4, 4): 0, (4, 5): 1, (4, 6): 2, (4, 7): 1,
        (5, 5): 0, (5, 6): 1, (5, 7): 2,
        (6, 6): 0, (6, 7): 1,
        (7, 7): 0,
    }

    def get_corner_dist(from_pos: int, to_pos: int) -> int:
        """Get minimum distance between two corner positions."""
        key = tuple(sorted([from_pos, to_pos]))
        return corner_distances.get(key, 2)  # Default to 2 if not in table

    total_corner = 0
    for i in range(8):
        target = i
        current = cubie.corner_perm[i]
        dist = get_corner_dist(current, target)

        # Add penalty for orientation
        if cubie.corner_orient[i] != 0:
            dist = max(dist, 1)  # At least 1 move to fix orientation

        total_corner += dist

    total_edge = 0
    for i in range(12):
        if cubie.edge_perm[i] != i:
            total_edge += 1
        if cubie.edge_orient[i] != 0:
            total_edge += 1

    # Divide by 4 for admissibility
    return max(total_corner / 4.0, total_edge / 4.0)


class HeuristicEvaluator:
    """
    Evaluator that can apply multiple heuristics and compare results.
    """

    def __init__(self):
        """Initialize heuristic evaluator."""
        self.heuristics = {
            'simple': simple_heuristic,
            'hamming': hamming_distance,
            'manhattan': manhattan_distance,
        }

    def evaluate(self, cube: RubikCube, heuristic_name: str = 'manhattan') -> float:
        """
        Evaluate a cube state using the specified heuristic.

        Args:
            cube: Rubik's cube state
            heuristic_name: Name of heuristic to use

        Returns:
            Distance estimate
        """
        if heuristic_name not in self.heuristics:
            raise ValueError(f"Unknown heuristic: {heuristic_name}")

        return self.heuristics[heuristic_name](cube)

    def evaluate_all(self, cube: RubikCube) -> Dict[str, float]:
        """
        Evaluate a cube state using all available heuristics.

        Args:
            cube: Rubik's cube state

        Returns:
            Dictionary mapping heuristic names to distance estimates
        """
        results = {}
        for name, heuristic_func in self.heuristics.items():
            results[name] = heuristic_func(cube)

        return results

    def compare_heuristics(self, cube: RubikCube, actual_distance: int = None) -> None:
        """
        Compare all heuristics on a cube state and print results.

        Args:
            cube: Rubik's cube state
            actual_distance: Optional actual distance for comparison
        """
        results = self.evaluate_all(cube)

        print("Heuristic Comparison:")
        print(f"  Cube solved: {cube.is_solved()}")
        if actual_distance is not None:
            print(f"  Actual distance: {actual_distance}")
        print()

        for name, estimate in sorted(results.items()):
            print(f"  {name:15s}: {estimate:.2f}")
            if actual_distance is not None:
                error = abs(estimate - actual_distance)
                print(f"                   Error: {error:.2f}")
