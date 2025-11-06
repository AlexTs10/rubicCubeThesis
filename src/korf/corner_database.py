"""
Corner Pattern Database

This module implements a pattern database for the 8 corner pieces of the Rubik's Cube.
The corner database considers both the position and orientation of all corners,
ignoring edge pieces entirely.

State Space:
- 8 corners with permutation: 8! = 40,320 states
- 7 independent orientations (8th is determined by parity): 3^7 = 2,187 states
- Total: 8! × 3^7 = 88,179,840 states ≈ 88M states

Memory Usage:
- Storing in nibbles (4 bits): ~44 MB
- Maximum distance from solved: typically around 11-12 moves

This database provides an admissible heuristic - it never overestimates the
actual distance to solve the corners.
"""

import numpy as np
from typing import List
from ..kociemba.cubie import CubieCube, ALL_MOVES
from ..kociemba.coord import (
    get_corner_orientation,
    get_corner_permutation,
    set_corner_orientation,
    set_corner_permutation,
    factorial
)
from .pattern_database import PatternDatabase, bfs_generate_pattern_database


# Size of corner pattern database: 8! × 3^7
CORNER_DB_SIZE = factorial(8) * (3 ** 7)  # 88,179,840


def corner_index(cubie: CubieCube) -> int:
    """
    Compute the index for a corner state.

    The index is a unique integer from 0 to 88,179,839 that represents
    the corner configuration (position and orientation).

    Index formula: corner_permutation * 3^7 + corner_orientation

    Args:
        cubie: Cubie cube state

    Returns:
        Corner pattern index (0 to CORNER_DB_SIZE-1)
    """
    perm = get_corner_permutation(cubie)
    orient = get_corner_orientation(cubie)

    # Combine: each permutation has 3^7 orientation variants
    index = perm * 2187 + orient

    return index


def index_to_corner_state(index: int) -> CubieCube:
    """
    Convert a corner index back to a cubie state.

    Args:
        index: Corner pattern index

    Returns:
        Cubie cube with the specified corner configuration
    """
    # Extract permutation and orientation
    perm = index // 2187
    orient = index % 2187

    # Create cubie with this corner state
    cubie = CubieCube()
    set_corner_permutation(cubie, perm)
    set_corner_orientation(cubie, orient)

    return cubie


def apply_move_to_corner_index(index: int, move: str) -> int:
    """
    Apply a move to a corner state index.

    Args:
        index: Corner pattern index
        move: Move to apply (e.g., 'U', 'R2', "F'")

    Returns:
        New corner pattern index after the move
    """
    # Convert index to state
    cubie = index_to_corner_state(index)

    # Apply move
    if move not in ALL_MOVES:
        raise ValueError(f"Invalid move: {move}")

    cubie = cubie.multiply(ALL_MOVES[move])

    # Convert back to index
    return corner_index(cubie)


class CornerPatternDatabase(PatternDatabase):
    """
    Pattern database for corner pieces only.

    This database stores the minimum number of moves needed to solve
    all 8 corners from any configuration.
    """

    def __init__(self):
        """Initialize the corner pattern database."""
        super().__init__("corner", CORNER_DB_SIZE)

    def get_corner_distance(self, cubie: CubieCube) -> int:
        """
        Get the distance estimate for solving the corners.

        Args:
            cubie: Cubie cube state

        Returns:
            Minimum number of moves to solve corners (0-15)
        """
        index = corner_index(cubie)
        return self.get_distance(index)

    def generate(self, verbose: bool = True) -> None:
        """
        Generate the corner pattern database using BFS.

        Args:
            verbose: Print progress messages
        """
        if verbose:
            print(f"Generating Corner Pattern Database...")
            print(f"  Total states: {self.size:,}")
            print(f"  Memory: {self.data.nbytes / (1024*1024):.2f} MB")

        # BFS from solved state
        solved_cubie = CubieCube()
        solved_index = corner_index(solved_cubie)

        if verbose:
            print(f"  Solved state index: {solved_index}")
            print(f"  Starting BFS...")

        bfs_generate_pattern_database(
            db=self,
            index_func=corner_index,
            move_func=apply_move_to_corner_index,
            solved_index=solved_index
        )

        if verbose:
            print(f"  Generation complete!")
            print(self)


def create_corner_database(load_if_exists: bool = True, save_path: str = None) -> CornerPatternDatabase:
    """
    Create or load a corner pattern database.

    Args:
        load_if_exists: If True and save_path exists, load from disk
        save_path: Path to save/load the database (default: data/pattern_databases/corner_db.pkl)

    Returns:
        Corner pattern database
    """
    import os

    if save_path is None:
        save_path = "data/pattern_databases/corner_db.pkl"

    # Try to load if it exists
    if load_if_exists and os.path.exists(save_path):
        print(f"Loading corner database from {save_path}...")
        db = PatternDatabase.load(save_path)
        # Convert to CornerPatternDatabase
        corner_db = CornerPatternDatabase()
        corner_db.data = db.data
        corner_db.max_depth = db.max_depth
        corner_db.states_at_depth = db.states_at_depth
        print("  Loaded successfully!")
        return corner_db

    # Generate new database
    print(f"Generating new corner database...")
    corner_db = CornerPatternDatabase()
    corner_db.generate(verbose=True)

    # Save to disk
    if save_path:
        print(f"Saving to {save_path}...")
        corner_db.save(save_path)
        print("  Saved successfully!")

    return corner_db
