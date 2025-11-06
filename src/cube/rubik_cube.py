"""
Rubik's Cube Representation

This module provides the core representation of a 3x3x3 Rubik's Cube using
a facelet-based approach with Singmaster notation for moves.

Cube State Representation:
- 6 faces: U (Up/White), D (Down/Yellow), F (Front/Green),
           B (Back/Blue), L (Left/Orange), R (Right/Red)
- Each face has 9 facelets indexed 0-8:
    0 1 2
    3 4 5
    6 7 8

Singmaster Notation:
- Basic moves: U, D, F, B, L, R (90° clockwise)
- Prime moves: U', D', F', B', L', R' (90° counter-clockwise)
- Double moves: U2, D2, F2, B2, L2, R2 (180°)
"""

import numpy as np
from typing import List, Tuple, Optional
from enum import Enum
import copy


class Face(Enum):
    """Enumeration of cube faces."""
    U = 0  # Up (White)
    D = 1  # Down (Yellow)
    F = 2  # Front (Green)
    B = 3  # Back (Blue)
    L = 4  # Left (Orange)
    R = 5  # Right (Red)


class Color(Enum):
    """Enumeration of facelet colors."""
    WHITE = 'W'
    YELLOW = 'Y'
    GREEN = 'G'
    BLUE = 'B'
    ORANGE = 'O'
    RED = 'R'


# Mapping from faces to colors (standard orientation)
FACE_COLORS = {
    Face.U: Color.WHITE,
    Face.D: Color.YELLOW,
    Face.F: Color.GREEN,
    Face.B: Color.BLUE,
    Face.L: Color.ORANGE,
    Face.R: Color.RED
}


class RubikCube:
    """
    Represents a 3x3x3 Rubik's Cube state.

    The cube is represented as 6 faces, each with 9 facelets.
    State is stored as a numpy array of shape (6, 9) where each
    element represents the color at that facelet position.
    """

    def __init__(self, state: Optional[np.ndarray] = None):
        """
        Initialize a Rubik's Cube.

        Args:
            state: Optional pre-existing state. If None, creates a solved cube.
        """
        if state is not None:
            self.state = state.copy()
        else:
            # Create solved cube: each face shows its own color
            self.state = np.zeros((6, 9), dtype=int)
            for face in Face:
                self.state[face.value, :] = face.value

    def copy(self) -> 'RubikCube':
        """Create a deep copy of the cube."""
        return RubikCube(state=self.state.copy())

    def is_solved(self) -> bool:
        """Check if the cube is in solved state."""
        for face in Face:
            if not np.all(self.state[face.value] == face.value):
                return False
        return True

    def get_face(self, face: Face) -> np.ndarray:
        """Get the state of a specific face."""
        return self.state[face.value]

    def _rotate_face_clockwise(self, face: Face) -> None:
        """
        Rotate a face 90 degrees clockwise.

        Face rotation pattern:
        0 1 2    6 3 0
        3 4 5 -> 7 4 1
        6 7 8    8 5 2
        """
        face_state = self.state[face.value]
        self.state[face.value] = np.array([
            face_state[6], face_state[3], face_state[0],
            face_state[7], face_state[4], face_state[1],
            face_state[8], face_state[5], face_state[2]
        ])

    def _rotate_face_counter_clockwise(self, face: Face) -> None:
        """Rotate a face 90 degrees counter-clockwise."""
        # Counter-clockwise is same as 3 clockwise rotations
        for _ in range(3):
            self._rotate_face_clockwise(face)

    def move_U(self) -> None:
        """Execute U move (rotate Up face clockwise)."""
        self._rotate_face_clockwise(Face.U)

        # Rotate edge: F -> L -> B -> R -> F
        temp = self.state[Face.F.value, 0:3].copy()
        self.state[Face.F.value, 0:3] = self.state[Face.R.value, 0:3]
        self.state[Face.R.value, 0:3] = self.state[Face.B.value, 0:3]
        self.state[Face.B.value, 0:3] = self.state[Face.L.value, 0:3]
        self.state[Face.L.value, 0:3] = temp

    def move_D(self) -> None:
        """Execute D move (rotate Down face clockwise)."""
        self._rotate_face_clockwise(Face.D)

        # Rotate edge: F -> R -> B -> L -> F
        temp = self.state[Face.F.value, 6:9].copy()
        self.state[Face.F.value, 6:9] = self.state[Face.L.value, 6:9]
        self.state[Face.L.value, 6:9] = self.state[Face.B.value, 6:9]
        self.state[Face.B.value, 6:9] = self.state[Face.R.value, 6:9]
        self.state[Face.R.value, 6:9] = temp

    def move_F(self) -> None:
        """Execute F move (rotate Front face clockwise)."""
        self._rotate_face_clockwise(Face.F)

        # Rotate edge cycle
        temp = self.state[Face.U.value, [6, 7, 8]].copy()
        self.state[Face.U.value, [6, 7, 8]] = self.state[Face.L.value, [8, 5, 2]]
        self.state[Face.L.value, [8, 5, 2]] = self.state[Face.D.value, [2, 1, 0]]
        self.state[Face.D.value, [2, 1, 0]] = self.state[Face.R.value, [0, 3, 6]]
        self.state[Face.R.value, [0, 3, 6]] = temp

    def move_B(self) -> None:
        """Execute B move (rotate Back face clockwise)."""
        self._rotate_face_clockwise(Face.B)

        # Rotate edge cycle
        temp = self.state[Face.U.value, [0, 1, 2]].copy()
        self.state[Face.U.value, [0, 1, 2]] = self.state[Face.R.value, [2, 5, 8]]
        self.state[Face.R.value, [2, 5, 8]] = self.state[Face.D.value, [8, 7, 6]]
        self.state[Face.D.value, [8, 7, 6]] = self.state[Face.L.value, [6, 3, 0]]
        self.state[Face.L.value, [6, 3, 0]] = temp

    def move_L(self) -> None:
        """Execute L move (rotate Left face clockwise)."""
        self._rotate_face_clockwise(Face.L)

        # Rotate edge cycle
        temp = self.state[Face.U.value, [0, 3, 6]].copy()
        self.state[Face.U.value, [0, 3, 6]] = self.state[Face.B.value, [8, 5, 2]]
        self.state[Face.B.value, [8, 5, 2]] = self.state[Face.D.value, [0, 3, 6]]
        self.state[Face.D.value, [0, 3, 6]] = self.state[Face.F.value, [0, 3, 6]]
        self.state[Face.F.value, [0, 3, 6]] = temp

    def move_R(self) -> None:
        """Execute R move (rotate Right face clockwise)."""
        self._rotate_face_clockwise(Face.R)

        # Rotate edge cycle
        temp = self.state[Face.U.value, [2, 5, 8]].copy()
        self.state[Face.U.value, [2, 5, 8]] = self.state[Face.F.value, [2, 5, 8]]
        self.state[Face.F.value, [2, 5, 8]] = self.state[Face.D.value, [2, 5, 8]]
        self.state[Face.D.value, [2, 5, 8]] = self.state[Face.B.value, [6, 3, 0]]
        self.state[Face.B.value, [6, 3, 0]] = temp

    def apply_move(self, move: str) -> None:
        """
        Apply a move in Singmaster notation.

        Args:
            move: Move string like 'U', 'R\'', 'F2', etc.
        """
        # Parse move
        if len(move) == 0:
            return

        base_move = move[0]
        modifier = move[1:] if len(move) > 1 else ''

        # Get move function
        move_functions = {
            'U': self.move_U,
            'D': self.move_D,
            'F': self.move_F,
            'B': self.move_B,
            'L': self.move_L,
            'R': self.move_R
        }

        if base_move not in move_functions:
            raise ValueError(f"Invalid move: {move}")

        move_func = move_functions[base_move]

        # Apply move with modifier
        if modifier == '':
            move_func()
        elif modifier == "'":
            # Prime: apply 3 times
            for _ in range(3):
                move_func()
        elif modifier == '2':
            # Double: apply 2 times
            for _ in range(2):
                move_func()
        else:
            raise ValueError(f"Invalid move modifier: {move}")

    def apply_moves(self, moves: List[str]) -> None:
        """
        Apply a sequence of moves.

        Args:
            moves: List of move strings
        """
        for move in moves:
            self.apply_move(move)

    def apply_move_sequence(self, sequence: str) -> None:
        """
        Apply a sequence of moves from a space-separated string.

        Args:
            sequence: Space-separated move sequence like "R U R' U'"
        """
        moves = sequence.strip().split()
        self.apply_moves(moves)

    def scramble(self, moves: int = 20, seed: Optional[int] = None) -> List[str]:
        """
        Scramble the cube with random moves.

        Args:
            moves: Number of random moves to apply
            seed: Optional random seed for reproducibility

        Returns:
            List of moves applied
        """
        if seed is not None:
            np.random.seed(seed)

        all_moves = ['U', 'U\'', 'U2', 'D', 'D\'', 'D2',
                     'F', 'F\'', 'F2', 'B', 'B\'', 'B2',
                     'L', 'L\'', 'L2', 'R', 'R\'', 'R2']

        scramble_sequence = []
        for _ in range(moves):
            move = np.random.choice(all_moves)
            scramble_sequence.append(move)
            self.apply_move(move)

        return scramble_sequence

    def __str__(self) -> str:
        """String representation of the cube state."""
        lines = []
        lines.append("Rubik's Cube State:")
        lines.append(f"Solved: {self.is_solved()}")
        lines.append("")

        for face in Face:
            face_state = self.state[face.value]
            color_map = {i: list(Face)[i].name for i in range(6)}

            lines.append(f"{face.name} face:")
            for row in range(3):
                row_str = " ".join(color_map[face_state[row * 3 + col]]
                                  for col in range(3))
                lines.append(f"  {row_str}")
            lines.append("")

        return "\n".join(lines)

    def __eq__(self, other: 'RubikCube') -> bool:
        """Check equality of two cube states."""
        if not isinstance(other, RubikCube):
            return False
        return np.array_equal(self.state, other.state)

    def __hash__(self) -> int:
        """Hash the cube state for use in sets and dictionaries."""
        return hash(self.state.tobytes())
