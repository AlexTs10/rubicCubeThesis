"""
Edge Pattern Databases

This module implements pattern databases for edge pieces of the Rubik's Cube.
Since a full 12-edge database would require ~500GB of memory, we split the
edges into two separate 7-edge databases.

State Space per 7-edge database:
- Choose 7 edges from 12: C(12, 7) = 792 ways
- Permutation of 7 edges: 7! = 5,040 states
- Orientation of 7 edges: 2^7 = 128 states
- However, we only track edges within the chosen subset
- For a specific 7-edge subset: 7! × 2^7 = 645,120 states

For simplicity and following Korf's approach, we use:
- Edge Group 1: First 6 edges (UR, UF, UL, UB, DR, DF)
- Edge Group 2: Last 6 edges (DL, DB, FR, FL, BL, BR)

This gives us two databases of approximately equal size, each storing
distances for 6 edges, totaling about 244 MB each.

References:
- Korf (1997): Uses 6-6 split for edges
- Stack Overflow: Explains why 12-edge DB is too large
"""

import numpy as np
from typing import List, Set
from ..kociemba.cubie import CubieCube, ALL_MOVES
from ..kociemba.coord import (
    permutation_to_rank,
    rank_to_permutation,
    factorial
)
from .pattern_database import PatternDatabase, bfs_generate_pattern_database


def edge_orientation_to_coord(edge_orient: np.ndarray, edge_subset: List[int]) -> int:
    """
    Convert edge orientations to a coordinate.

    Args:
        edge_orient: Array of edge orientations (0 or 1)
        edge_subset: List of edge indices to consider

    Returns:
        Orientation coordinate (0 to 2^n - 1 where n = len(edge_subset))
    """
    coord = 0
    for edge_idx in edge_subset[:-1]:  # Last edge determined by parity
        coord = coord * 2 + int(edge_orient[edge_idx])
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
    total = 0

    for i in range(n_edges - 1, 0, -1):
        orient[i] = coord % 2
        total += orient[i]
        coord //= 2

    # First edge determined by parity
    orient[0] = total % 2

    return orient


def normalize_edge_permutation(edge_perm: np.ndarray, edge_subset: List[int]) -> np.ndarray:
    """
    Normalize edge permutation for a subset of edges.

    This maps the actual edge indices to 0..n-1 for ranking.

    Args:
        edge_perm: Full edge permutation array
        edge_subset: List of edge indices to consider

    Returns:
        Normalized permutation (values 0 to n-1)
    """
    # Extract subset
    subset_perm = []
    for i in range(12):
        if edge_perm[i] in edge_subset:
            # Map to 0..n-1
            subset_perm.append(edge_subset.index(edge_perm[i]))

    return np.array(subset_perm, dtype=np.int8)


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
        n_edges = len(edge_subset)

        # Size: n! × 2^(n-1) for n edges
        # We use n-1 for orientation due to parity constraint
        size = factorial(n_edges) * (2 ** (n_edges - 1))

        super().__init__(name, size)

    def edge_index(self, cubie: CubieCube) -> int:
        """
        Compute the index for an edge state.

        Args:
            cubie: Cubie cube state

        Returns:
            Edge pattern index for this subset
        """
        # Get normalized permutation for our subset
        normalized_perm = normalize_edge_permutation(cubie.edge_perm, self.edge_subset)
        perm_rank = permutation_to_rank(normalized_perm)

        # Get orientation coordinate
        n_edges = len(self.edge_subset)
        orient_coord = edge_orientation_to_coord(cubie.edge_orient, self.edge_subset)

        # Combine: each permutation has 2^(n-1) orientation variants
        orient_size = 2 ** (n_edges - 1)
        index = perm_rank * orient_size + orient_coord

        return index

    def get_edge_distance(self, cubie: CubieCube) -> int:
        """
        Get the distance estimate for solving this edge subset.

        Args:
            cubie: Cubie cube state

        Returns:
            Minimum number of moves to solve these edges (0-15)
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
        n_edges = len(self.edge_subset)
        orient_size = 2 ** (n_edges - 1)

        # Extract permutation and orientation
        perm_rank = index // orient_size
        orient_coord = index % orient_size

        # Create cubie state
        cubie = CubieCube()

        # Set permutation
        normalized_perm = rank_to_permutation(perm_rank, n_edges)

        # Map back to actual edge indices
        actual_perm = [0] * 12
        other_edges = [e for e in range(12) if e not in self.edge_subset]
        subset_pos = 0
        other_pos = 0

        for i in range(12):
            if i in self.edge_subset:
                actual_perm[i] = self.edge_subset[normalized_perm[subset_pos]]
                subset_pos += 1
            else:
                actual_perm[i] = other_edges[other_pos]
                other_pos += 1

        cubie.edge_perm = np.array(actual_perm, dtype=np.int8)

        # Set orientation
        orient = coord_to_edge_orientation(orient_coord, n_edges)
        for i, edge_idx in enumerate(self.edge_subset):
            cubie.edge_orient[edge_idx] = orient[i]

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
    save_path: str = None
) -> EdgePatternDatabase:
    """
    Create or load an edge pattern database.

    Args:
        edge_group: Which edge group (1 or 2)
        load_if_exists: If True and save_path exists, load from disk
        save_path: Path to save/load the database

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
        print(f"Loading {name} database from {save_path}...")
        db = PatternDatabase.load(save_path)
        # Convert to EdgePatternDatabase
        edge_db = EdgePatternDatabase(edge_subset, name)
        edge_db.data = db.data
        edge_db.max_depth = db.max_depth
        edge_db.states_at_depth = db.states_at_depth
        print("  Loaded successfully!")
        return edge_db

    # Generate new database
    print(f"Generating new {name} database...")
    edge_db = EdgePatternDatabase(edge_subset, name)
    edge_db.generate(verbose=True)

    # Save to disk
    if save_path:
        print(f"Saving to {save_path}...")
        edge_db.save(save_path)
        print("  Saved successfully!")

    return edge_db
