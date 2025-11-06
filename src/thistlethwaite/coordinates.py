"""
Coordinate Systems for Thistlethwaite Algorithm

This module implements coordinate systems to represent different aspects
of the Rubik's Cube state for each phase of Thistlethwaite's algorithm.

Each coordinate system maps a specific aspect of the cube to an integer,
allowing efficient representation and lookup in pattern databases.
"""

import numpy as np
from typing import Tuple
from ..cube.rubik_cube import RubikCube, Face


# Permutation to rank conversion utilities
def factorial(n: int) -> int:
    """Calculate factorial."""
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
        perm: Permutation array (values 0 to n-1)

    Returns:
        Rank (0 to n!-1)
    """
    n = len(perm)
    rank = 0
    for i in range(n - 1):
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
    return np.array(result)


def combination_to_rank(positions: np.ndarray, n: int) -> int:
    """
    Convert a combination to its rank.

    Args:
        positions: Sorted array of chosen positions
        n: Total number of positions

    Returns:
        Rank of the combination
    """
    rank = 0
    k = len(positions)
    for i, pos in enumerate(positions):
        if i == 0:
            start = 0
        else:
            start = positions[i - 1] + 1
        for j in range(start, pos):
            rank += binomial(n - j - 1, k - i - 1)
    return rank


# Edge position mapping (standard cube notation)
# Edge indices: UF=0, UR=1, UB=2, UL=3, DF=4, DR=5, DB=6, DL=7, FR=8, FL=9, BR=10, BL=11
EDGE_POSITIONS = {
    'UF': 0, 'UR': 1, 'UB': 2, 'UL': 3,
    'DF': 4, 'DR': 5, 'DB': 6, 'DL': 7,
    'FR': 8, 'FL': 9, 'BR': 10, 'BL': 11
}

# Corner indices: UFL=0, UFR=1, UBR=2, UBL=3, DFL=4, DFR=5, DBR=6, DBL=7
CORNER_POSITIONS = {
    'UFL': 0, 'UFR': 1, 'UBR': 2, 'UBL': 3,
    'DFL': 4, 'DFR': 5, 'DBR': 6, 'DBL': 7
}


class CubeCoordinates:
    """
    Coordinate system for representing cube state.

    Extracts various coordinate values from a RubikCube state
    for use in the Thistlethwaite algorithm.
    """

    def __init__(self, cube: RubikCube):
        """Initialize coordinates from a cube state."""
        self.cube = cube
        self._extract_pieces()

    def _extract_pieces(self):
        """Extract edge and corner pieces from the cube."""
        # This is a simplified extraction - in practice, you'd need to
        # map the facelet representation to edge/corner permutations and orientations

        # For edges: 12 edges, each can be in one of 12 positions with 2 orientations
        # For corners: 8 corners, each can be in one of 8 positions with 3 orientations

        # Initialize with solved state
        self.edge_permutation = np.arange(12)
        self.edge_orientation = np.zeros(12, dtype=int)
        self.corner_permutation = np.arange(8)
        self.corner_orientation = np.zeros(8, dtype=int)

        # Extract from facelet representation
        # This is a complex mapping that needs to be implemented properly
        self._extract_edges_from_facelets()
        self._extract_corners_from_facelets()

    def _extract_edges_from_facelets(self):
        """Extract edge permutation and orientation from facelets."""
        # Edge mapping from facelets to edge pieces
        # Each edge is defined by two facelets
        edge_facelets = [
            ((Face.U, 7), (Face.F, 1)),  # UF
            ((Face.U, 5), (Face.R, 1)),  # UR
            ((Face.U, 1), (Face.B, 1)),  # UB
            ((Face.U, 3), (Face.L, 1)),  # UL
            ((Face.D, 1), (Face.F, 7)),  # DF
            ((Face.D, 5), (Face.R, 7)),  # DR
            ((Face.D, 7), (Face.B, 7)),  # DB
            ((Face.D, 3), (Face.L, 7)),  # DL
            ((Face.F, 5), (Face.R, 3)),  # FR
            ((Face.F, 3), (Face.L, 5)),  # FL
            ((Face.B, 3), (Face.R, 5)),  # BR
            ((Face.B, 5), (Face.L, 3)),  # BL
        ]

        # For each position, find which edge is there
        for pos, (facelet1, facelet2) in enumerate(edge_facelets):
            face1, idx1 = facelet1
            face2, idx2 = facelet2
            color1 = self.cube.state[face1.value, idx1]
            color2 = self.cube.state[face2.value, idx2]

            # Find which edge this is by matching colors
            # In solved state, facelet1 has face1's color and facelet2 has face2's color
            for edge_idx, (ref_f1, ref_f2) in enumerate(edge_facelets):
                ref_face1, _ = ref_f1
                ref_face2, _ = ref_f2

                if color1 == ref_face1.value and color2 == ref_face2.value:
                    self.edge_permutation[pos] = edge_idx
                    self.edge_orientation[pos] = 0
                    break
                elif color1 == ref_face2.value and color2 == ref_face1.value:
                    self.edge_permutation[pos] = edge_idx
                    self.edge_orientation[pos] = 1
                    break

    def _extract_corners_from_facelets(self):
        """Extract corner permutation and orientation from facelets."""
        # Corner mapping from facelets to corner pieces
        # Each corner is defined by three facelets
        corner_facelets = [
            ((Face.U, 6), (Face.F, 0), (Face.L, 2)),  # UFL
            ((Face.U, 8), (Face.F, 2), (Face.R, 0)),  # UFR
            ((Face.U, 2), (Face.B, 2), (Face.R, 2)),  # UBR
            ((Face.U, 0), (Face.B, 0), (Face.L, 0)),  # UBL
            ((Face.D, 0), (Face.F, 6), (Face.L, 8)),  # DFL
            ((Face.D, 2), (Face.F, 8), (Face.R, 6)),  # DFR
            ((Face.D, 8), (Face.B, 8), (Face.R, 8)),  # DBR
            ((Face.D, 6), (Face.B, 6), (Face.L, 6)),  # DBL
        ]

        for pos, (facelet1, facelet2, facelet3) in enumerate(corner_facelets):
            face1, idx1 = facelet1
            face2, idx2 = facelet2
            face3, idx3 = facelet3
            colors = [
                self.cube.state[face1.value, idx1],
                self.cube.state[face2.value, idx2],
                self.cube.state[face3.value, idx3]
            ]

            # Find which corner this is by matching colors
            for corner_idx, (ref_f1, ref_f2, ref_f3) in enumerate(corner_facelets):
                ref_colors = [ref_f1[0].value, ref_f2[0].value, ref_f3[0].value]

                # Check all rotations
                for rot in range(3):
                    rotated_colors = colors[rot:] + colors[:rot]
                    if rotated_colors[0] == ref_colors[0] and \
                       rotated_colors[1] == ref_colors[1] and \
                       rotated_colors[2] == ref_colors[2]:
                        self.edge_permutation[pos] = corner_idx
                        self.corner_orientation[pos] = rot
                        break

    # Phase 0 → G1: Edge Orientation
    def get_edge_orientation_coord(self) -> int:
        """
        Get edge orientation coordinate (0 to 2047).

        In G1, all edges must be oriented. An edge is oriented if it can
        be solved using only moves from <U, D, F2, B2, L, R>.

        Returns:
            Edge orientation coordinate (11 edges encode 2^11 states)
        """
        # Only 11 edges matter (12th is determined by parity)
        coord = 0
        for i in range(11):
            coord = coord * 2 + self.edge_orientation[i]
        return coord

    # Phase 1 → G2: Corner Orientation + E-slice edges
    def get_corner_orientation_coord(self) -> int:
        """
        Get corner orientation coordinate (0 to 2186).

        In G2, all corners must be oriented. A corner is oriented if
        its U/D facelet is on the U or D face.

        Returns:
            Corner orientation coordinate (7 corners encode 3^7 states)
        """
        coord = 0
        for i in range(7):  # 8th corner determined by parity
            coord = coord * 3 + self.corner_orientation[i]
        return coord

    def get_e_slice_coord(self) -> int:
        """
        Get E-slice edge combination coordinate (0 to 494).

        The E-slice edges are FR, FL, BR, BL (indices 8, 9, 10, 11).
        This coordinate encodes which edges are in the E-slice positions.

        Returns:
            E-slice combination coordinate C(12, 4) = 495
        """
        # Find which edges are in E-slice positions (8, 9, 10, 11)
        e_slice_positions = []
        for pos in range(8, 12):
            if self.edge_permutation[pos] in [8, 9, 10, 11]:
                e_slice_positions.append(pos - 8)

        if len(e_slice_positions) != 4:
            # Not in G2 yet, use full 12 positions
            e_slice_positions = [i for i, e in enumerate(self.edge_permutation) if e in [8, 9, 10, 11]]

        return combination_to_rank(np.array(e_slice_positions), 12)

    # Phase 2 → G3: Corner tetrads + Edge slices
    def get_corner_tetrad_coord(self) -> int:
        """
        Get corner tetrad coordinate.

        Corners are divided into two tetrads (groups of 4).
        This coordinate tracks whether corners stay within their tetrad.

        Returns:
            Corner tetrad coordinate
        """
        # Simplified: check if corners are in correct tetrad positions
        # Tetrad 1: UFL, UFR, DFL, DFR (indices 0, 1, 4, 5)
        # Tetrad 2: UBL, UBR, DBL, DBR (indices 3, 2, 7, 6)
        tetrad1_positions = [0, 1, 4, 5]
        tetrad1_corners = [i for i, c in enumerate(self.corner_permutation) if c in tetrad1_positions]
        return combination_to_rank(np.array(tetrad1_corners), 8)

    def get_edge_slice_coord(self) -> int:
        """
        Get edge slice coordinate for phase 3.

        Tracks which edges are in their correct slices.

        Returns:
            Edge slice coordinate
        """
        # UD-slice edges (UF, UR, UB, UL, DF, DR, DB, DL: 0-7)
        ud_positions = [i for i, e in enumerate(self.edge_permutation) if e < 8]
        return combination_to_rank(np.array(ud_positions), 12)

    # Phase 3 → G4: Full permutation
    def get_corner_permutation_coord(self) -> int:
        """
        Get corner permutation coordinate (0 to 40319).

        Returns:
            Corner permutation rank (8! = 40320 states)
        """
        return permutation_to_rank(self.corner_permutation)

    def get_edge_permutation_coord(self) -> int:
        """
        Get edge permutation coordinate (0 to 479001599).

        Returns:
            Edge permutation rank (12! = 479001600 states)
        """
        return permutation_to_rank(self.edge_permutation)

    def get_ud_edge_permutation_coord(self) -> int:
        """
        Get UD-slice edge permutation coordinate.

        Only considers edges in UD slice for phase 3.

        Returns:
            UD edge permutation coordinate (8! = 40320)
        """
        # Get edges in UD positions
        ud_edges = self.edge_permutation[:8]
        return permutation_to_rank(ud_edges)

    def get_e_edge_permutation_coord(self) -> int:
        """
        Get E-slice edge permutation coordinate.

        Only considers edges in E slice for phase 3.

        Returns:
            E edge permutation coordinate (4! = 24)
        """
        # Get edges in E positions
        e_edges = self.edge_permutation[8:12]
        return permutation_to_rank(e_edges)
