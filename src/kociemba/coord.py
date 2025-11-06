"""
Coordinate Systems for Kociemba's Two-Phase Algorithm

This module implements the six coordinate systems used in Kociemba's algorithm:

Phase 1 Coordinates (G0 -> G1):
1. Corner Orientation (0-2186): 3^7 = 2187 states
2. Edge Orientation (0-2047): 2^11 = 2048 states
3. UD-Slice Position (0-494): C(12,4) = 495 states

Phase 2 Coordinates (G1 -> Solved):
4. Corner Permutation (0-40319): 8! = 40320 states
5. Edge Permutation (0-40319): 8! for U/D edges = 40320 states
6. UD-Slice Permutation (0-23): 4! = 24 states

Total Phase 1 space: 2187 * 2048 * 495 = 2,217,093,120 states
Total Phase 2 space: 40320 * 40320 * 24 = 19,508,428,800 states
"""

import numpy as np
from typing import Tuple
from .cubie import CubieCube


# Utility functions for permutation arithmetic

def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def binomial(n: int, k: int) -> int:
    """Calculate binomial coefficient C(n, k)."""
    if k > n or k < 0:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def permutation_to_rank(perm: np.ndarray) -> int:
    """
    Convert a permutation to its lexicographic rank.

    Args:
        perm: Permutation array (0 to n-1)

    Returns:
        Rank (0 to n!-1)
    """
    n = len(perm)
    rank = 0
    for i in range(n):
        rank *= (n - i)
        for j in range(i + 1, n):
            if perm[i] > perm[j]:
                rank += 1
    return rank


def rank_to_permutation(rank: int, n: int) -> np.ndarray:
    """
    Convert a lexicographic rank to a permutation.

    Args:
        rank: Rank (0 to n!-1)
        n: Size of permutation

    Returns:
        Permutation array
    """
    perm = list(range(n))
    result = []
    for i in range(n):
        fact = factorial(n - 1 - i)
        idx = rank // fact
        result.append(perm[idx])
        perm.pop(idx)
        rank %= fact
    return np.array(result, dtype=np.int8)


def combination_to_rank(positions: np.ndarray, k: int) -> int:
    """
    Convert a combination to its rank using binomial coefficients.

    This is used for the UD-slice coordinate.

    Args:
        positions: Binary array where 1 indicates chosen position
        k: Number of chosen positions

    Returns:
        Rank of the combination (0 to C(n,k)-1)
    """
    n = len(positions)
    rank = 0
    count = k

    for i in range(n - 1, -1, -1):
        if positions[i]:
            rank += binomial(i, count)
            count -= 1
            if count == 0:
                break

    return rank


def rank_to_combination(rank: int, n: int, k: int) -> np.ndarray:
    """
    Convert a rank to a combination.

    Args:
        rank: Rank (0 to C(n,k)-1)
        n: Total number of positions
        k: Number of chosen positions

    Returns:
        Binary array where 1 indicates chosen position
    """
    positions = np.zeros(n, dtype=np.int8)
    count = k

    for i in range(n - 1, -1, -1):
        binom = binomial(i, count)
        if rank >= binom:
            positions[i] = 1
            rank -= binom
            count -= 1
            if count == 0:
                break

    return positions


# ============================================================================
# PHASE 1 COORDINATES (G0 -> G1)
# ============================================================================

def get_corner_orientation(cubie: CubieCube) -> int:
    """
    Get corner orientation coordinate (0-2186).

    In Phase 1, we want all corners to be oriented correctly.
    Only 7 corners matter (8th is determined by parity).

    Args:
        cubie: Cubie cube state

    Returns:
        Corner orientation coordinate (base-3 number)
    """
    coord = 0
    for i in range(7):  # Only first 7 corners (8th is parity)
        coord = coord * 3 + int(cubie.corner_orient[i])
    return int(coord)


def set_corner_orientation(cubie: CubieCube, coord: int) -> None:
    """
    Set corner orientation from coordinate.

    Args:
        cubie: Cubie cube to modify
        coord: Corner orientation coordinate
    """
    total = 0
    for i in range(6, -1, -1):
        cubie.corner_orient[i] = coord % 3
        total += cubie.corner_orient[i]
        coord //= 3
    # 8th corner determined by parity (sum must be 0 mod 3)
    cubie.corner_orient[7] = (3 - (total % 3)) % 3


def get_edge_orientation(cubie: CubieCube) -> int:
    """
    Get edge orientation coordinate (0-2047).

    In Phase 1, we want all edges to be oriented correctly.
    Only 11 edges matter (12th is determined by parity).

    Args:
        cubie: Cubie cube state

    Returns:
        Edge orientation coordinate (binary number)
    """
    coord = 0
    for i in range(11):  # Only first 11 edges (12th is parity)
        coord = coord * 2 + int(cubie.edge_orient[i])
    return int(coord)


def set_edge_orientation(cubie: CubieCube, coord: int) -> None:
    """
    Set edge orientation from coordinate.

    Args:
        cubie: Cubie cube to modify
        coord: Edge orientation coordinate
    """
    total = 0
    for i in range(10, -1, -1):
        cubie.edge_orient[i] = coord % 2
        total += cubie.edge_orient[i]
        coord //= 2
    # 12th edge determined by parity (sum must be 0 mod 2)
    cubie.edge_orient[11] = total % 2


def get_udslice(cubie: CubieCube) -> int:
    """
    Get UD-slice coordinate (0-494).

    The UD-slice consists of 4 edges: FR, FL, BL, BR (indices 8, 9, 10, 11).
    This coordinate represents which 4 positions out of 12 contain these edges,
    regardless of their order.

    C(12, 4) = 495 states

    Coordinate 0 = solved state (edges 8,9,10,11 in positions 8,9,10,11)
    Coordinate 494 = maximally scrambled (edges in positions 0,1,2,3)

    Args:
        cubie: Cubie cube state

    Returns:
        UD-slice coordinate
    """
    # Create binary array: 1 if position contains UD-slice edge
    positions = np.zeros(12, dtype=np.int8)
    for i in range(12):
        if 8 <= cubie.edge_perm[i] <= 11:
            positions[i] = 1

    # Reverse ranking so solved state (positions 8-11) gives 0
    rank = combination_to_rank(positions, 4)
    return 494 - rank


def set_udslice(cubie: CubieCube, coord: int) -> None:
    """
    Set UD-slice from coordinate.

    Args:
        cubie: Cubie cube to modify
        coord: UD-slice coordinate
    """
    # Reverse the coord to match get_udslice
    rank = 494 - coord
    positions = rank_to_combination(rank, 12, 4)

    # Fill in slice edges at marked positions
    slice_idx = 0
    other_idx = 0
    for i in range(12):
        if positions[i]:
            cubie.edge_perm[i] = 8 + slice_idx
            slice_idx += 1
        else:
            cubie.edge_perm[i] = other_idx
            other_idx += 1
            if other_idx >= 8:
                other_idx = 8


# ============================================================================
# PHASE 2 COORDINATES (G1 -> Solved)
# ============================================================================

def get_corner_permutation(cubie: CubieCube) -> int:
    """
    Get corner permutation coordinate (0-40319).

    Represents the permutation of all 8 corners.
    8! = 40320 states

    Args:
        cubie: Cubie cube state

    Returns:
        Corner permutation coordinate
    """
    return permutation_to_rank(cubie.corner_perm)


def set_corner_permutation(cubie: CubieCube, coord: int) -> None:
    """
    Set corner permutation from coordinate.

    Args:
        cubie: Cubie cube to modify
        coord: Corner permutation coordinate
    """
    cubie.corner_perm = rank_to_permutation(coord, 8)


def get_edge_permutation(cubie: CubieCube) -> int:
    """
    Get U/D edge permutation coordinate (0-40319).

    In Phase 2 (G1), the UD-slice edges are in their slice, and we only
    care about the permutation of the 8 U/D face edges (indices 0-7).

    8! = 40320 states

    Args:
        cubie: Cubie cube state

    Returns:
        Edge permutation coordinate for U/D edges
    """
    # Extract only U/D edges (positions 0-7)
    ud_edges = cubie.edge_perm[:8].copy()
    return permutation_to_rank(ud_edges)


def set_edge_permutation(cubie: CubieCube, coord: int) -> None:
    """
    Set U/D edge permutation from coordinate.

    Args:
        cubie: Cubie cube to modify
        coord: Edge permutation coordinate
    """
    perm = rank_to_permutation(coord, 8)
    cubie.edge_perm[:8] = perm


def get_udslice_permutation(cubie: CubieCube) -> int:
    """
    Get UD-slice permutation coordinate (0-23).

    In Phase 2, the 4 UD-slice edges (FR, FL, BL, BR) are in their slice
    (positions 8-11), and we only care about their ordering.

    4! = 24 states

    Args:
        cubie: Cubie cube state

    Returns:
        UD-slice permutation coordinate
    """
    # Extract slice edges (positions 8-11) and normalize to 0-3
    slice_edges = cubie.edge_perm[8:12].copy() - 8
    return permutation_to_rank(slice_edges)


def set_udslice_permutation(cubie: CubieCube, coord: int) -> None:
    """
    Set UD-slice permutation from coordinate.

    Args:
        cubie: Cubie cube to modify
        coord: UD-slice permutation coordinate
    """
    perm = rank_to_permutation(coord, 4)
    cubie.edge_perm[8:12] = perm + 8


# ============================================================================
# COORDINATE REPRESENTATION
# ============================================================================

class CoordCube:
    """
    Coordinate representation of a cube state.

    Stores all 6 coordinates for efficient state comparison and hashing.
    """

    def __init__(self, cubie: CubieCube):
        """
        Initialize coordinates from a cubie cube.

        Args:
            cubie: Cubie cube state
        """
        # Phase 1 coordinates
        self.corner_orient = get_corner_orientation(cubie)
        self.edge_orient = get_edge_orientation(cubie)
        self.udslice = get_udslice(cubie)

        # Phase 2 coordinates
        self.corner_perm = get_corner_permutation(cubie)
        self.edge_perm = get_edge_permutation(cubie)
        self.udslice_perm = get_udslice_permutation(cubie)

    def is_phase1_solved(self) -> bool:
        """Check if cube is in G1 (Phase 1 complete)."""
        return (self.corner_orient == 0 and
                self.edge_orient == 0 and
                self.udslice == 0)

    def is_solved(self) -> bool:
        """Check if cube is completely solved."""
        return (self.corner_orient == 0 and
                self.edge_orient == 0 and
                self.udslice == 0 and
                self.corner_perm == 0 and
                self.edge_perm == 0 and
                self.udslice_perm == 0)

    def __eq__(self, other: 'CoordCube') -> bool:
        """Check equality of coordinate cubes."""
        if not isinstance(other, CoordCube):
            return False
        return (self.corner_orient == other.corner_orient and
                self.edge_orient == other.edge_orient and
                self.udslice == other.udslice and
                self.corner_perm == other.corner_perm and
                self.edge_perm == other.edge_perm and
                self.udslice_perm == other.udslice_perm)

    def __hash__(self) -> int:
        """Hash coordinate cube for use in sets/dicts."""
        return hash((self.corner_orient, self.edge_orient, self.udslice,
                    self.corner_perm, self.edge_perm, self.udslice_perm))

    def __str__(self) -> str:
        """String representation of coordinates."""
        return (f"CoordCube(CO={self.corner_orient}, EO={self.edge_orient}, "
                f"UDS={self.udslice}, CP={self.corner_perm}, "
                f"EP={self.edge_perm}, UDSP={self.udslice_perm})")
