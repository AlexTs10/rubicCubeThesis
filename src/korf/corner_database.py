"""
Corner Pattern Database

This module implements a pattern database for the 8 corner pieces of the Rubik's
Cube. The corner database considers both the position and orientation of all
corners, ignoring edge pieces entirely.

State Space:
- 8 corners with permutation: 8! = 40,320 states
- 7 independent orientations (8th is determined by parity): 3^7 = 2,187 states
- Total: 8! × 3^7 = 88,179,840 states

Memory Usage:
- Exact-safe byte storage: ~84.1 MiB for the distance array

This database provides an admissible heuristic - it never overestimates the
actual distance to solve the corners.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Optional

import numpy as np

from ..kociemba.cubie import ALL_MOVES, CubieCube
from ..kociemba.coord import (
    get_corner_orientation,
    get_corner_permutation,
    set_corner_orientation,
    set_corner_permutation,
    factorial
)
from ..kociemba.moves import ALL_MOVE_NAMES, get_move_tables
from .pattern_database import PatternDatabase

try:
    from numba import njit
except ImportError:  # pragma: no cover - optional acceleration only.
    njit = None


CORNER_ORIENTATION_STATES = 3 ** 7
CORNER_PERMUTATION_STATES = factorial(8)

# Size of corner pattern database: 8! × 3^7
CORNER_DB_SIZE = CORNER_PERMUTATION_STATES * CORNER_ORIENTATION_STATES
DEFAULT_CORNER_DB_PATH = "data/pattern_databases/corner_db.pkl"
DEFAULT_NATIVE_EXACT_CACHE_DIR = "data/pattern_databases/native_exact"
CORNER_PERMUTATION_MOVE_TABLE_FILENAME = "corner_permutation_all_moves_v1.pkl"
BYTE_UNINITIALIZED = np.uint8(0xFF)


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
    index = perm * CORNER_ORIENTATION_STATES + orient

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
    perm = index // CORNER_ORIENTATION_STATES
    orient = index % CORNER_ORIENTATION_STATES

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
        Generate the corner pattern database using a specialized frontier BFS.

        Args:
            verbose: Print progress messages
        """
        self.generate_full(verbose=verbose)

    def generate_full(
        self,
        verbose: bool = True,
        *,
        max_depth: Optional[int] = None,
        frontier_chunk_size: int = 250_000,
        move_cache_dir: str = DEFAULT_NATIVE_EXACT_CACHE_DIR,
    ) -> None:
        """
        Generate the corner pattern database using coordinate transitions.

        This specialized generator avoids the generic Python BFS scaffolding in
        `pattern_database.py`, which does not scale to 88M states.

        Args:
            verbose: Print progress messages.
            max_depth: Optional depth cutoff used only for tests and profiling.
            frontier_chunk_size: Number of frontier states to expand per chunk.
            move_cache_dir: Directory for cached auxiliary move tables.
        """
        if frontier_chunk_size <= 0:
            raise ValueError("frontier_chunk_size must be positive")

        self.data.fill(self.BYTE_UNINITIALIZED)
        self.max_depth = 0
        self.states_at_depth = {}

        solved_index = corner_index(CubieCube())
        self.set_distance(solved_index, 0)
        self.states_at_depth[0] = 1

        corner_perm_moves = _load_or_build_corner_permutation_all_move_table(
            cache_dir=move_cache_dir,
            verbose=verbose,
        )
        move_tables = get_move_tables()
        move_tables.load()
        corner_orient_moves = np.asarray(move_tables.corner_orient_moves, dtype=np.int32)

        frontier = np.array([solved_index], dtype=np.uint32)
        initialized_states = 1
        depth = 0

        if verbose:
            print("Generating Corner Pattern Database...")
            print(f"  Total states: {self.size:,}")
            print(f"  Distance array memory: {self.data.nbytes / (1024 * 1024):.2f} MiB")
            print(f"  Solved state index: {solved_index}")
            print(f"  Frontier chunk size: {frontier_chunk_size:,}")
            print(f"  Accelerator: {'numba' if njit is not None else 'python'}")
            if max_depth is not None:
                print(f"  Depth limit: {max_depth}")

        while frontier.size:
            if max_depth is not None and depth >= max_depth:
                break

            depth += 1
            next_chunks = []
            next_count = 0

            for start in range(0, int(frontier.size), frontier_chunk_size):
                stop = min(start + frontier_chunk_size, int(frontier.size))
                expanded = _expand_corner_frontier_chunk(
                    frontier[start:stop],
                    self.data,
                    corner_perm_moves,
                    corner_orient_moves,
                    depth,
                )
                if expanded.size == 0:
                    continue
                next_chunks.append(expanded)
                next_count += int(expanded.size)

            if next_count == 0:
                frontier = np.empty(0, dtype=np.uint32)
                break

            self.max_depth = depth
            self.states_at_depth[depth] = next_count
            initialized_states += next_count

            if len(next_chunks) == 1:
                frontier = next_chunks[0]
            else:
                frontier = np.concatenate(next_chunks)

            if verbose:
                pct = 100.0 * initialized_states / self.size
                print(
                    f"  Depth {depth:2d}: +{next_count:>10,} states "
                    f"(total {initialized_states:,}, {pct:5.2f}%)"
                )

        if verbose:
            if self.is_complete():
                print("  Generation complete!")
            else:
                print(
                    "  Generation stopped before covering the full state space "
                    f"({initialized_states:,}/{self.size:,} states initialized)."
                )
            print(self)


def create_corner_database(
    load_if_exists: bool = True,
    save_path: str = None,
    *,
    generate_if_missing: bool = True,
    require_complete: bool = True,
    verbose: bool = True,
    max_depth: Optional[int] = None,
    frontier_chunk_size: int = 250_000,
    move_cache_dir: str = DEFAULT_NATIVE_EXACT_CACHE_DIR,
) -> CornerPatternDatabase:
    """
    Create or load a corner pattern database.

    Args:
        load_if_exists: If True and save_path exists, load from disk
        save_path: Path to save/load the database (default: data/pattern_databases/corner_db.pkl)
        generate_if_missing: Whether to build the database when it is not cached
        require_complete: Whether loading should reject incomplete databases
        verbose: Whether to print progress messages
        max_depth: Optional generation cutoff used only for tests and profiling
        frontier_chunk_size: Frontier expansion chunk size for generation
        move_cache_dir: Directory for cached auxiliary move tables

    Returns:
        Corner pattern database
    """
    if save_path is None:
        save_path = DEFAULT_CORNER_DB_PATH
    save_path = Path(save_path)

    # Try to load if it exists
    if load_if_exists and save_path.exists():
        if verbose:
            print(f"Loading corner database from {save_path}...")
        db = PatternDatabase.load(str(save_path))
        # Convert to CornerPatternDatabase
        corner_db = CornerPatternDatabase()
        corner_db.copy_storage_from(db)
        if require_complete and not corner_db.is_complete():
            raise ValueError(
                f"Corner database at {save_path} is incomplete "
                f"({corner_db.initialized_count():,}/{corner_db.size:,} states)"
            )
        if verbose:
            print("  Loaded successfully!")
        return corner_db

    if not generate_if_missing:
        raise FileNotFoundError(f"Corner database not found: {save_path}")

    # Generate new database
    if verbose:
        print("Generating new corner database...")
    corner_db = CornerPatternDatabase()
    corner_db.generate_full(
        verbose=verbose,
        max_depth=max_depth,
        frontier_chunk_size=frontier_chunk_size,
        move_cache_dir=move_cache_dir,
    )

    # Save to disk
    if save_path:
        if verbose:
            print(f"Saving to {save_path}...")
        corner_db.save(str(save_path))
        if verbose:
            print("  Saved successfully!")

    return corner_db


def _load_or_build_corner_permutation_all_move_table(
    *,
    cache_dir: str,
    verbose: bool,
) -> np.ndarray:
    """Load or build the full 18-move corner-permutation transition table."""
    cache_path = Path(cache_dir) / CORNER_PERMUTATION_MOVE_TABLE_FILENAME
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists():
        with open(cache_path, "rb") as fh:
            payload = pickle.load(fh)
        return np.asarray(payload["move_table"], dtype=np.int32)

    if verbose:
        print("  Building corner permutation move table (40320 x 18)...")

    move_table = np.zeros((CORNER_PERMUTATION_STATES, len(ALL_MOVE_NAMES)), dtype=np.int32)
    for coord in range(CORNER_PERMUTATION_STATES):
        cubie = CubieCube()
        set_corner_permutation(cubie, coord)
        for move_idx, move_name in enumerate(ALL_MOVE_NAMES):
            next_cubie = cubie.multiply(ALL_MOVES[move_name])
            move_table[coord, move_idx] = get_corner_permutation(next_cubie)

    with open(cache_path, "wb") as fh:
        pickle.dump(
            {"move_table": move_table},
            fh,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    return move_table


if njit is not None:

    @njit(cache=True)
    def _expand_corner_frontier_chunk(
        frontier: np.ndarray,
        distance_table: np.ndarray,
        corner_perm_moves: np.ndarray,
        corner_orient_moves: np.ndarray,
        next_depth: int,
    ) -> np.ndarray:
        """Expand one BFS frontier chunk using precomputed corner coordinates."""
        num_moves = corner_perm_moves.shape[1]
        buffer = np.empty(frontier.shape[0] * num_moves, dtype=np.uint32)
        count = 0

        for frontier_idx in range(frontier.shape[0]):
            state_index = int(frontier[frontier_idx])
            corner_perm = state_index // CORNER_ORIENTATION_STATES
            corner_orient = state_index - corner_perm * CORNER_ORIENTATION_STATES

            for move_idx in range(num_moves):
                next_index = (
                    int(corner_perm_moves[corner_perm, move_idx]) * CORNER_ORIENTATION_STATES
                    + int(corner_orient_moves[corner_orient, move_idx])
                )
                if distance_table[next_index] != BYTE_UNINITIALIZED:
                    continue
                distance_table[next_index] = next_depth
                buffer[count] = next_index
                count += 1

        return buffer[:count]

else:

    def _expand_corner_frontier_chunk(
        frontier: np.ndarray,
        distance_table: np.ndarray,
        corner_perm_moves: np.ndarray,
        corner_orient_moves: np.ndarray,
        next_depth: int,
    ) -> np.ndarray:
        """Python fallback for environments without numba."""
        num_moves = int(corner_perm_moves.shape[1])
        buffer = np.empty(int(frontier.shape[0]) * num_moves, dtype=np.uint32)
        count = 0

        for state_index in frontier:
            state_index = int(state_index)
            corner_perm = state_index // CORNER_ORIENTATION_STATES
            corner_orient = state_index % CORNER_ORIENTATION_STATES

            for move_idx in range(num_moves):
                next_index = (
                    int(corner_perm_moves[corner_perm, move_idx]) * CORNER_ORIENTATION_STATES
                    + int(corner_orient_moves[corner_orient, move_idx])
                )
                if distance_table[next_index] != BYTE_UNINITIALIZED:
                    continue
                distance_table[next_index] = next_depth
                buffer[count] = next_index
                count += 1

        return buffer[:count]
