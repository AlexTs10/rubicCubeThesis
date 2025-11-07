"""
Cubie-Level Representation for Kociemba Algorithm

This module provides a cubie-level representation of the Rubik's Cube,
tracking individual corner and edge pieces with their positions and orientations.

Representation:
- 8 corners, each with position (0-7) and orientation (0-2)
- 12 edges, each with position (0-11) and orientation (0-1)

Corner numbering (URF=0):
  URF=0, UFL=1, ULB=2, UBR=3, DFR=4, DLF=5, DBL=6, DRB=7

Edge numbering (UR=0):
  UR=0, UF=1, UL=2, UB=3, DR=4, DF=5, DL=6, DB=7, FR=8, FL=9, BL=10, BR=11
"""

import numpy as np
from typing import List, Tuple
from ..cube.rubik_cube import RubikCube, Face


# Corner positions in standard notation (URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB)
CORNER_NAMES = ['URF', 'UFL', 'ULB', 'UBR', 'DFR', 'DLF', 'DBL', 'DRB']

# Edge positions in standard notation
EDGE_NAMES = ['UR', 'UF', 'UL', 'UB', 'DR', 'DF', 'DL', 'DB', 'FR', 'FL', 'BL', 'BR']


class CubieCube:
    """
    Cubie-level representation of a Rubik's Cube.

    This representation tracks the actual corner and edge pieces,
    including their positions and orientations.
    """

    def __init__(self):
        """Initialize a solved cube."""
        # Corner permutation: corner_perm[i] = which corner is at position i
        self.corner_perm = np.arange(8, dtype=np.int8)

        # Corner orientation: 0, 1, or 2 (clockwise twist count)
        # 0 = correct orientation, 1 = twisted clockwise, 2 = twisted counter-clockwise
        self.corner_orient = np.zeros(8, dtype=np.int8)

        # Edge permutation: edge_perm[i] = which edge is at position i
        self.edge_perm = np.arange(12, dtype=np.int8)

        # Edge orientation: 0 or 1 (flip)
        # 0 = correct orientation, 1 = flipped
        self.edge_orient = np.zeros(12, dtype=np.int8)

    def copy(self) -> 'CubieCube':
        """Create a deep copy of this cubie cube."""
        new_cube = CubieCube()
        new_cube.corner_perm = self.corner_perm.copy()
        new_cube.corner_orient = self.corner_orient.copy()
        new_cube.edge_perm = self.edge_perm.copy()
        new_cube.edge_orient = self.edge_orient.copy()
        return new_cube

    def multiply(self, other: 'CubieCube') -> 'CubieCube':
        """
        Multiply this cube by another (apply other's transformation to this).

        This is used to apply moves to the cube.

        Args:
            other: Another cubie cube (typically a move)

        Returns:
            Result of multiplication
        """
        result = CubieCube()

        # Apply corner permutation
        for i in range(8):
            result.corner_perm[i] = self.corner_perm[other.corner_perm[i]]
            # Add orientations mod 3
            result.corner_orient[i] = (self.corner_orient[other.corner_perm[i]] +
                                       other.corner_orient[i]) % 3

        # Apply edge permutation
        for i in range(12):
            result.edge_perm[i] = self.edge_perm[other.edge_perm[i]]
            # Add orientations mod 2
            result.edge_orient[i] = (self.edge_orient[other.edge_perm[i]] +
                                     other.edge_orient[i]) % 2

        return result

    def is_solved(self) -> bool:
        """Check if the cube is solved."""
        return (np.array_equal(self.corner_perm, np.arange(8)) and
                np.array_equal(self.corner_orient, np.zeros(8)) and
                np.array_equal(self.edge_perm, np.arange(12)) and
                np.array_equal(self.edge_orient, np.zeros(12)))

    def __eq__(self, other: 'CubieCube') -> bool:
        """Check equality of two cubie cubes."""
        if not isinstance(other, CubieCube):
            return False
        return (np.array_equal(self.corner_perm, other.corner_perm) and
                np.array_equal(self.corner_orient, other.corner_orient) and
                np.array_equal(self.edge_perm, other.edge_perm) and
                np.array_equal(self.edge_orient, other.edge_orient))

    def __hash__(self) -> int:
        """Hash the cubie cube state."""
        return hash((self.corner_perm.tobytes(),
                    self.corner_orient.tobytes(),
                    self.edge_perm.tobytes(),
                    self.edge_orient.tobytes()))


# Move definitions as cubie transformations
# Each move is defined by how it permutes and orients corners and edges

def create_move_U() -> CubieCube:
    """Create the U move cubie transformation."""
    move = CubieCube()
    # Corner permutation: UBR -> URF -> UFL -> ULB -> UBR
    move.corner_perm = np.array([3, 0, 1, 2, 4, 5, 6, 7], dtype=np.int8)
    move.corner_orient = np.zeros(8, dtype=np.int8)
    # Edge permutation: UB -> UR -> UF -> UL -> UB
    move.edge_perm = np.array([3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], dtype=np.int8)
    move.edge_orient = np.zeros(12, dtype=np.int8)
    return move


def create_move_D() -> CubieCube:
    """Create the D move cubie transformation."""
    move = CubieCube()
    # Corner permutation matches RubikCube.move_D (clockwise when looking at D face)
    move.corner_perm = np.array([0, 1, 2, 3, 5, 6, 7, 4], dtype=np.int8)
    move.corner_orient = np.zeros(8, dtype=np.int8)
    # Edge permutation: DF -> DL -> DB -> DR -> DF
    move.edge_perm = np.array([0, 1, 2, 3, 5, 6, 7, 4, 8, 9, 10, 11], dtype=np.int8)
    move.edge_orient = np.zeros(12, dtype=np.int8)
    return move


def create_move_R() -> CubieCube:
    """Create the R move cubie transformation."""
    move = CubieCube()
    # Corner permutation: URF -> DFR -> DRB -> UBR -> URF
    # Corners twist when moving through R layer
    move.corner_perm = np.array([4, 1, 2, 0, 7, 5, 6, 3], dtype=np.int8)
    move.corner_orient = np.array([2, 0, 0, 1, 1, 0, 0, 2], dtype=np.int8)
    # Edge permutation: UR -> FR -> DR -> BR -> UR
    move.edge_perm = np.array([8, 1, 2, 3, 11, 5, 6, 7, 4, 9, 10, 0], dtype=np.int8)
    move.edge_orient = np.zeros(12, dtype=np.int8)
    return move


def create_move_L() -> CubieCube:
    """Create the L move cubie transformation."""
    move = CubieCube()
    # Corner permutation: UFL -> ULB -> DBL -> DLF -> UFL
    move.corner_perm = np.array([0, 2, 6, 3, 4, 1, 5, 7], dtype=np.int8)
    move.corner_orient = np.array([0, 1, 2, 0, 0, 2, 1, 0], dtype=np.int8)
    # Edge permutation: UL -> BL -> DL -> FL -> UL
    move.edge_perm = np.array([0, 1, 10, 3, 4, 5, 9, 7, 8, 2, 6, 11], dtype=np.int8)
    move.edge_orient = np.zeros(12, dtype=np.int8)
    return move


def create_move_F() -> CubieCube:
    """Create the F move cubie transformation."""
    move = CubieCube()
    # Corner permutation: URF -> UFL -> DLF -> DFR -> URF
    move.corner_perm = np.array([1, 5, 2, 3, 0, 4, 6, 7], dtype=np.int8)
    move.corner_orient = np.array([1, 2, 0, 0, 2, 1, 0, 0], dtype=np.int8)
    # Edge permutation: UF -> FL -> DF -> FR -> UF
    # Edges flip when moving through F layer
    move.edge_perm = np.array([0, 9, 2, 3, 4, 8, 6, 7, 1, 5, 10, 11], dtype=np.int8)
    move.edge_orient = np.array([0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0], dtype=np.int8)
    return move


def create_move_B() -> CubieCube:
    """Create the B move cubie transformation."""
    move = CubieCube()
    # Corner permutation: UBR -> ULB -> DBL -> DRB -> UBR
    move.corner_perm = np.array([0, 1, 3, 7, 4, 5, 2, 6], dtype=np.int8)
    move.corner_orient = np.array([0, 0, 1, 2, 0, 0, 2, 1], dtype=np.int8)
    # Edge permutation: UB -> BR -> DB -> BL -> UB
    move.edge_perm = np.array([0, 1, 2, 11, 4, 5, 6, 10, 8, 9, 3, 7], dtype=np.int8)
    move.edge_orient = np.array([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1], dtype=np.int8)
    return move


# Create all basic moves
MOVE_CUBES = {
    'U': create_move_U(),
    'D': create_move_D(),
    'R': create_move_R(),
    'L': create_move_L(),
    'F': create_move_F(),
    'B': create_move_B(),
}

# Generate all 18 moves (including prime and double moves)
ALL_MOVES = {}
for name, move in MOVE_CUBES.items():
    # Basic move
    ALL_MOVES[name] = move
    # Double move (apply twice)
    ALL_MOVES[name + '2'] = move.multiply(move)
    # Prime move (apply three times)
    ALL_MOVES[name + "'"] = move.multiply(move).multiply(move)


def apply_move_to_cubie(cube: CubieCube, move: str) -> CubieCube:
    """
    Apply a move to a cubie cube.

    Args:
        cube: Input cubie cube
        move: Move string (e.g., 'U', 'R2', "F'")

    Returns:
        New cubie cube after applying the move
    """
    if move not in ALL_MOVES:
        raise ValueError(f"Invalid move: {move}")
    return cube.multiply(ALL_MOVES[move])


def from_facelet_cube(facelet_cube: RubikCube) -> CubieCube:
    """
    Convert a facelet-based RubikCube to a cubie-level representation.

    Args:
        facelet_cube: Facelet representation

    Returns:
        Cubie representation
    """
    cubie = CubieCube()

    # Extract corner pieces from facelets
    # Each corner is defined by three facelets
    corner_facelets = [
        # URF = 0
        ((Face.U, 8), (Face.R, 0), (Face.F, 2)),
        # UFL = 1
        ((Face.U, 6), (Face.F, 0), (Face.L, 2)),
        # ULB = 2
        ((Face.U, 0), (Face.L, 0), (Face.B, 2)),
        # UBR = 3
        ((Face.U, 2), (Face.B, 0), (Face.R, 2)),
        # DFR = 4
        ((Face.D, 2), (Face.F, 8), (Face.R, 6)),
        # DLF = 5
        ((Face.D, 0), (Face.L, 8), (Face.F, 6)),
        # DBL = 6
        ((Face.D, 6), (Face.B, 8), (Face.L, 6)),
        # DRB = 7
        ((Face.D, 8), (Face.R, 8), (Face.B, 6)),
    ]

    # Extract corners
    for pos, (f1, f2, f3) in enumerate(corner_facelets):
        colors = [
            facelet_cube.state[f1[0].value, f1[1]],
            facelet_cube.state[f2[0].value, f2[1]],
            facelet_cube.state[f3[0].value, f3[1]]
        ]

        found = False

        # Find which corner this is
        for corner_idx, (ref_f1, ref_f2, ref_f3) in enumerate(corner_facelets):
            ref_colors = [ref_f1[0].value, ref_f2[0].value, ref_f3[0].value]

            # Check all 3 rotations
            for rot in range(3):
                rotated_colors = [colors[(0 + rot) % 3], colors[(1 + rot) % 3], colors[(2 + rot) % 3]]
                if rotated_colors == ref_colors:
                    cubie.corner_perm[pos] = corner_idx
                    cubie.corner_orient[pos] = rot
                    found = True
                    break

            if found:
                break

        if not found:
            raise ValueError(
                f"Invalid cube state: no matching corner for colors {colors} at position {pos}"
            )

    # Extract edge pieces from facelets
    edge_facelets = [
        # UR = 0
        ((Face.U, 5), (Face.R, 1)),
        # UF = 1
        ((Face.U, 7), (Face.F, 1)),
        # UL = 2
        ((Face.U, 3), (Face.L, 1)),
        # UB = 3
        ((Face.U, 1), (Face.B, 1)),
        # DR = 4
        ((Face.D, 5), (Face.R, 7)),
        # DF = 5
        ((Face.D, 1), (Face.F, 7)),
        # DL = 6
        ((Face.D, 3), (Face.L, 7)),
        # DB = 7
        ((Face.D, 7), (Face.B, 7)),
        # FR = 8
        ((Face.F, 5), (Face.R, 3)),
        # FL = 9
        ((Face.F, 3), (Face.L, 5)),
        # BL = 10
        ((Face.B, 5), (Face.L, 3)),
        # BR = 11
        ((Face.B, 3), (Face.R, 5)),
    ]

    # Extract edges
    for pos, (f1, f2) in enumerate(edge_facelets):
        colors = [
            facelet_cube.state[f1[0].value, f1[1]],
            facelet_cube.state[f2[0].value, f2[1]]
        ]

        found = False

        # Find which edge this is
        for edge_idx, (ref_f1, ref_f2) in enumerate(edge_facelets):
            ref_colors = [ref_f1[0].value, ref_f2[0].value]

            if colors == ref_colors:
                cubie.edge_perm[pos] = edge_idx
                cubie.edge_orient[pos] = 0
                found = True
                break
            if colors == [ref_colors[1], ref_colors[0]]:
                cubie.edge_perm[pos] = edge_idx
                cubie.edge_orient[pos] = 1
                found = True
                break

        if not found:
            raise ValueError(
                f"Invalid cube state: no matching edge for colors {colors} at position {pos}"
            )

    return cubie


def to_facelet_cube(cubie: CubieCube) -> RubikCube:
    """
    Convert a cubie-level representation to a facelet-based RubikCube.

    Args:
        cubie: Cubie representation

    Returns:
        Facelet representation
    """
    cube = RubikCube()

    facelet_state = cube.state.copy()

    corner_facelets = [
        ((Face.U, 8), (Face.R, 0), (Face.F, 2)),
        ((Face.U, 6), (Face.F, 0), (Face.L, 2)),
        ((Face.U, 0), (Face.L, 0), (Face.B, 2)),
        ((Face.U, 2), (Face.B, 0), (Face.R, 2)),
        ((Face.D, 2), (Face.F, 8), (Face.R, 6)),
        ((Face.D, 0), (Face.L, 8), (Face.F, 6)),
        ((Face.D, 6), (Face.B, 8), (Face.L, 6)),
        ((Face.D, 8), (Face.R, 8), (Face.B, 6)),
    ]

    for pos, (target_f1, target_f2, target_f3) in enumerate(corner_facelets):
        corner_idx = int(cubie.corner_perm[pos])
        orient = int(cubie.corner_orient[pos]) % 3

        home_faces = corner_facelets[corner_idx]
        home_colors = [home_faces[0][0].value, home_faces[1][0].value, home_faces[2][0].value]

        colors = [home_colors[(i - orient) % 3] for i in range(3)]

        for rel_idx, (face, index) in enumerate((target_f1, target_f2, target_f3)):
            facelet_state[face.value, index] = colors[rel_idx]

    edge_facelets = [
        ((Face.U, 5), (Face.R, 1)),
        ((Face.U, 7), (Face.F, 1)),
        ((Face.U, 3), (Face.L, 1)),
        ((Face.U, 1), (Face.B, 1)),
        ((Face.D, 5), (Face.R, 7)),
        ((Face.D, 1), (Face.F, 7)),
        ((Face.D, 3), (Face.L, 7)),
        ((Face.D, 7), (Face.B, 7)),
        ((Face.F, 5), (Face.R, 3)),
        ((Face.F, 3), (Face.L, 5)),
        ((Face.B, 5), (Face.L, 3)),
        ((Face.B, 3), (Face.R, 5)),
    ]

    for pos, (target_f1, target_f2) in enumerate(edge_facelets):
        edge_idx = int(cubie.edge_perm[pos])
        orient = int(cubie.edge_orient[pos]) % 2

        home_faces = edge_facelets[edge_idx]
        home_colors = [home_faces[0][0].value, home_faces[1][0].value]

        if orient == 0:
            colors = home_colors
        else:
            colors = [home_colors[1], home_colors[0]]

        for rel_idx, (face, index) in enumerate((target_f1, target_f2)):
            facelet_state[face.value, index] = colors[rel_idx]

    return RubikCube(state=facelet_state)
