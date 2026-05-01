"""
Edge Pattern Databases

This module implements Korf-style pattern databases for tracked edge groups.
For a 6-edge group we must encode:

- which 6 of the 12 edge positions contain the tracked pieces: C(12, 6) = 924
- the permutation of the tracked pieces within those positions: 6! = 720
- the orientations of the tracked pieces: 2^6 = 64

That yields 924 * 720 * 64 = 42,577,920 states per 6-edge database.

The previous abstraction only ranked the tracked pieces relative to one another,
which collapsed distinct states whenever the same tracked edges occupied
different positions on the cube. It also read orientations from home positions
instead of from the tracked pieces' current positions. Both behaviors are
invalid for an admissible edge pattern database.
"""

import numpy as np
from typing import List
from ..kociemba.cubie import CubieCube, ALL_MOVES
from ..kociemba.coord import (
    binomial,
    combination_to_rank,
    rank_to_combination,
    permutation_to_rank,
    rank_to_permutation,
    factorial
)
from .pattern_database import PatternDatabase, bfs_generate_pattern_database


def edge_orientation_to_coord(tracked_orient: np.ndarray) -> int:
    """
    Convert tracked edge orientations to a coordinate.

    Args:
        tracked_orient: Orientations for tracked edges ordered by tracked position

    Returns:
        Orientation coordinate (0 to 2^n - 1)
    """
    coord = 0
    for orient in tracked_orient:
        coord = coord * 2 + int(orient)
    return coord


def coord_to_edge_orientation(coord: int, n_edges: int) -> np.ndarray:
    """
    Convert a coordinate to edge orientations.

    Args:
        coord: Orientation coordinate
        n_edges: Number of edges

    Returns:
        Array of orientations
    """
    orient = np.zeros(n_edges, dtype=np.int8)

    for i in range(n_edges - 1, -1, -1):
        orient[i] = coord % 2
        coord //= 2

    return orient


def project_tracked_edges(
    cubie: CubieCube,
    edge_subset: List[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Project a cube state onto a tracked edge subset.

    The projection encodes:
    - which positions contain tracked edges
    - which tracked edge is in each tracked position
    - the orientation of the tracked edge in each tracked position

    Args:
        cubie: Cubie cube state
        edge_subset: Tracked edge piece ids

    Returns:
        Tuple of (positions mask, normalized tracked permutation, tracked orientations)
    """
    subset_lookup = {edge: idx for idx, edge in enumerate(edge_subset)}
    tracked_positions = np.zeros(12, dtype=np.int8)
    tracked_perm = []
    tracked_orient = []

    for position, piece in enumerate(cubie.edge_perm):
        normalized_piece = subset_lookup.get(int(piece))
        if normalized_piece is None:
            continue
        tracked_positions[position] = 1
        tracked_perm.append(normalized_piece)
        tracked_orient.append(int(cubie.edge_orient[position]))

    return (
        tracked_positions,
        np.array(tracked_perm, dtype=np.int8),
        np.array(tracked_orient, dtype=np.int8),
    )


class EdgePatternDatabase(PatternDatabase):
    """
    Pattern database for a subset of edge pieces.

    This database stores the minimum number of moves needed to solve
    a specific subset of edges (ignoring other edges and corners).
    """

    def __init__(self, edge_subset: List[int], name: str):
        """
        Initialize an edge pattern database for a specific subset.

        Args:
            edge_subset: List of edge indices (0-11) to track
            name: Name for this database (e.g., "edge1", "edge2")
        """
        self.edge_subset = sorted(edge_subset)
        self.n_edges = len(self.edge_subset)
        self.position_states = binomial(12, self.n_edges)
        self.permutation_states = factorial(self.n_edges)
        # Tracked-edge orientations are independent; untracked edges absorb global parity.
        self.orientation_states = 2 ** self.n_edges

        size = (
            self.position_states *
            self.permutation_states *
            self.orientation_states
        )

        super().__init__(name, size)

    def edge_index(self, cubie: CubieCube) -> int:
        """
        Compute the index for an edge state.

        Args:
            cubie: Cubie cube state

        Returns:
            Edge pattern index for this subset
        """
        tracked_positions, normalized_perm, tracked_orient = project_tracked_edges(
            cubie,
            self.edge_subset,
        )
        position_rank = combination_to_rank(tracked_positions, self.n_edges)
        perm_rank = permutation_to_rank(normalized_perm)
        orient_coord = edge_orientation_to_coord(tracked_orient)

        index = (
            (position_rank * self.permutation_states + perm_rank) *
            self.orientation_states +
            orient_coord
        )

        return index

    def get_edge_distance(self, cubie: CubieCube) -> int:
        """
        Get the distance estimate for solving this edge subset.

        Args:
            cubie: Cubie cube state

        Returns:
            Minimum number of moves to solve these edges
        """
        index = self.edge_index(cubie)
        return self.get_distance(index)

    def generate(self, verbose: bool = True) -> None:
        """
        Generate the edge pattern database using BFS.

        Args:
            verbose: Print progress messages
        """
        if verbose:
            print(f"Generating Edge Pattern Database: {self.name}")
            print(f"  Edge subset: {self.edge_subset}")
            print(f"  Total states: {self.size:,}")
            print(f"  Memory: {self.data.nbytes / (1024*1024):.2f} MB")

        # BFS from solved state
        solved_cubie = CubieCube()
        solved_index = self.edge_index(solved_cubie)

        if verbose:
            print(f"  Solved state index: {solved_index}")
            print(f"  Starting BFS...")

        def apply_move_wrapper(idx: int, move: str) -> int:
            """Wrapper to apply move to edge index."""
            return self.apply_move_to_index(idx, move)

        bfs_generate_pattern_database(
            db=self,
            index_func=self.edge_index,
            move_func=apply_move_wrapper,
            solved_index=solved_index
        )

        if verbose:
            print(f"  Generation complete!")
            print(self)

    def index_to_edge_state(self, index: int) -> CubieCube:
        """
        Convert an edge index back to a cubie state.

        Args:
            index: Edge pattern index

        Returns:
            Cubie cube with the specified edge configuration
        """
        orient_coord = index % self.orientation_states
        index //= self.orientation_states
        perm_rank = index % self.permutation_states
        position_rank = index // self.permutation_states

        # Create cubie state
        cubie = CubieCube()
        normalized_perm = rank_to_permutation(perm_rank, self.n_edges)
        tracked_positions = rank_to_combination(position_rank, 12, self.n_edges)
        tracked_orient = coord_to_edge_orientation(orient_coord, self.n_edges)

        actual_perm = [0] * 12
        other_edges = [e for e in range(12) if e not in self.edge_subset]
        tracked_pos = 0
        other_pos = 0

        for position in range(12):
            if tracked_positions[position]:
                actual_perm[position] = self.edge_subset[int(normalized_perm[tracked_pos])]
                cubie.edge_orient[position] = tracked_orient[tracked_pos]
                tracked_pos += 1
            else:
                actual_perm[position] = other_edges[other_pos]
                other_pos += 1

        cubie.edge_perm = np.array(actual_perm, dtype=np.int8)

        return cubie

    def apply_move_to_index(self, index: int, move: str) -> int:
        """
        Apply a move to an edge state index.

        Args:
            index: Edge pattern index
            move: Move to apply

        Returns:
            New edge pattern index after the move
        """
        # Convert index to state
        cubie = self.index_to_edge_state(index)

        # Apply move
        if move not in ALL_MOVES:
            raise ValueError(f"Invalid move: {move}")

        cubie = cubie.multiply(ALL_MOVES[move])

        # Convert back to index
        return self.edge_index(cubie)


# Standard edge splits (Korf's approach)
EDGE_GROUP_1 = [0, 1, 2, 3, 4, 5]  # UR, UF, UL, UB, DR, DF
EDGE_GROUP_2 = [6, 7, 8, 9, 10, 11]  # DL, DB, FR, FL, BL, BR


def create_edge_database(
    edge_group: int,
    load_if_exists: bool = True,
    save_path: str = None,
    *,
    generate_if_missing: bool = True,
    require_complete: bool = True,
    verbose: bool = True,
) -> EdgePatternDatabase:
    """
    Create or load an edge pattern database.

    Args:
        edge_group: Which edge group (1 or 2)
        load_if_exists: If True and save_path exists, load from disk
        save_path: Path to save/load the database
        generate_if_missing: Whether to build the database when it is not cached
        require_complete: Whether loading should reject incomplete databases
        verbose: Whether to print progress messages

    Returns:
        Edge pattern database
    """
    import os

    if edge_group == 1:
        edge_subset = EDGE_GROUP_1
        name = "edge1"
        default_path = "data/pattern_databases/edge1_db.pkl"
    elif edge_group == 2:
        edge_subset = EDGE_GROUP_2
        name = "edge2"
        default_path = "data/pattern_databases/edge2_db.pkl"
    else:
        raise ValueError(f"Invalid edge group: {edge_group} (must be 1 or 2)")

    if save_path is None:
        save_path = default_path

    # Try to load if it exists
    if load_if_exists and os.path.exists(save_path):
        if verbose:
            print(f"Loading {name} database from {save_path}...")
        db = PatternDatabase.load(save_path)
        edge_db = EdgePatternDatabase(edge_subset, name)
        edge_db.copy_storage_from(db)
        if require_complete and not edge_db.is_complete():
            raise ValueError(
                f"Edge database at {save_path} is incomplete "
                f"({edge_db.initialized_count():,}/{edge_db.size:,} states)"
            )
        if verbose:
            print("  Loaded successfully!")
        return edge_db

    if not generate_if_missing:
        raise FileNotFoundError(f"Edge database not found: {save_path}")

    # Generate new database
    if verbose:
        print(f"Generating new {name} database...")
    edge_db = EdgePatternDatabase(edge_subset, name)
    edge_db.generate(verbose=verbose)

    # Save to disk
    if save_path:
        if verbose:
            print(f"Saving to {save_path}...")
        edge_db.save(save_path)
        if verbose:
            print("  Saved successfully!")

    return edge_db
