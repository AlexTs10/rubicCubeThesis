"""
Pruning Tables for Kociemba's Two-Phase Algorithm

Pruning tables store the minimum number of moves needed to reach the goal
from each coordinate state. They are generated using BFS and provide
admissible heuristics for IDA* search.

To keep memory usage reasonable (~80MB instead of ~400GB), we use:
- Phase 1: Two tables combining pairs of coordinates
  * Corner Orientation + Edge Orientation (2187 * 2048 ≈ 4.5M entries)
  * Edge Orientation + UD-Slice (2048 * 495 ≈ 1M entries)

- Phase 2: Two tables combining pairs of coordinates
  * Corner Permutation + Edge Permutation (40320 * 40320 ≈ 1.6B entries) - too large
  * Instead: Separate tables for each coordinate
  * Corner Permutation (40320 entries)
  * Edge Permutation (40320 entries)
  * UD-Slice Permutation (24 entries)

The heuristic is the maximum of the individual table lookups.
"""

import numpy as np
import os
import pickle
from collections import deque
from typing import List
from .moves import ALL_MOVE_NAMES, PHASE2_MOVES, get_move_tables


class PruningTables:
    """
    Pruning tables for both phases of Kociemba's algorithm.
    """

    def __init__(self, cache_dir: str = "data/pruning_tables"):
        """
        Initialize pruning tables.

        Args:
            cache_dir: Directory to cache precomputed tables
        """
        self.cache_dir = cache_dir

        # Phase 1 pruning tables
        self.phase1_co_eo = None  # Corner Orient + Edge Orient [2187 * 2048]
        self.phase1_eo_slice = None  # Edge Orient + UD-Slice [2048 * 495]

        # Phase 2 pruning tables (separate for memory efficiency)
        self.phase2_cp = None  # Corner Permutation [40320]
        self.phase2_ep = None  # Edge Permutation [40320]
        self.phase2_sp = None  # UD-Slice Permutation [24]

        self._loaded = False
        self.move_tables = None

    def load(self, force_regenerate: bool = False, max_depth: int = 12) -> None:
        """
        Load or generate pruning tables.

        Args:
            force_regenerate: If True, regenerate tables even if cached
            max_depth: Maximum depth for BFS (typically 12 for Phase 1, 15 for Phase 2)
        """
        if self._loaded and not force_regenerate:
            return

        # Load move tables first
        self.move_tables = get_move_tables()
        self.move_tables.load()

        cache_file = os.path.join(self.cache_dir, "pruning_tables.pkl")

        if not force_regenerate and os.path.exists(cache_file):
            print(f"Loading pruning tables from {cache_file}...")
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                self.phase1_co_eo = data['phase1_co_eo']
                self.phase1_eo_slice = data['phase1_eo_slice']
                self.phase2_cp = data['phase2_cp']
                self.phase2_ep = data['phase2_ep']
                self.phase2_sp = data['phase2_sp']
            print("Pruning tables loaded successfully!")
        else:
            print("Generating pruning tables (this may take several minutes)...")
            self._generate_tables(max_depth)
            print("Pruning tables generated!")

            # Save to cache
            os.makedirs(self.cache_dir, exist_ok=True)
            print(f"Saving pruning tables to {cache_file}...")
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'phase1_co_eo': self.phase1_co_eo,
                    'phase1_eo_slice': self.phase1_eo_slice,
                    'phase2_cp': self.phase2_cp,
                    'phase2_ep': self.phase2_ep,
                    'phase2_sp': self.phase2_sp
                }, f)
            print("Pruning tables saved!")

        self._loaded = True

    def _generate_tables(self, max_depth: int) -> None:
        """Generate all pruning tables using BFS."""

        # Phase 1 tables
        print("  Generating Phase 1 Corner Orient + Edge Orient table...")
        self.phase1_co_eo = self._generate_phase1_co_eo(max_depth)

        print("  Generating Phase 1 Edge Orient + UD-Slice table...")
        self.phase1_eo_slice = self._generate_phase1_eo_slice(max_depth)

        # Phase 2 tables
        print("  Generating Phase 2 Corner Permutation table...")
        self.phase2_cp = self._generate_phase2_coord(40320, 'corner_perm', max_depth)

        print("  Generating Phase 2 Edge Permutation table...")
        self.phase2_ep = self._generate_phase2_coord(40320, 'edge_perm', max_depth)

        print("  Generating Phase 2 UD-Slice Permutation table...")
        self.phase2_sp = self._generate_phase2_coord(24, 'slice_perm', max_depth)

    def _generate_phase1_co_eo(self, max_depth: int) -> np.ndarray:
        """
        Generate pruning table for Corner Orient + Edge Orient.

        Uses BFS to find minimum distance to goal (0, 0).
        """
        # Initialize table with -1 (unvisited)
        table = np.full((2187, 2048), -1, dtype=np.int8)

        # Goal state: (0, 0) - all oriented
        queue = deque([(0, 0, 0)])  # (co, eo, depth)
        table[0, 0] = 0

        moves = self.move_tables.corner_orient_moves, self.move_tables.edge_orient_moves

        while queue:
            co, eo, depth = queue.popleft()

            if depth >= max_depth:
                continue

            # Try all 18 moves
            for move_idx in range(18):
                new_co = moves[0][co, move_idx]
                new_eo = moves[1][eo, move_idx]

                if table[new_co, new_eo] == -1:
                    table[new_co, new_eo] = depth + 1
                    queue.append((new_co, new_eo, depth + 1))

        # Fill remaining unvisited states with max_depth
        table[table == -1] = max_depth

        return table

    def _generate_phase1_eo_slice(self, max_depth: int) -> np.ndarray:
        """
        Generate pruning table for Edge Orient + UD-Slice.

        Uses BFS to find minimum distance to goal (0, 0).
        """
        # Initialize table with -1 (unvisited)
        table = np.full((2048, 495), -1, dtype=np.int8)

        # Goal state: (0, 0)
        queue = deque([(0, 0, 0)])  # (eo, slice, depth)
        table[0, 0] = 0

        moves = self.move_tables.edge_orient_moves, self.move_tables.udslice_moves

        while queue:
            eo, slice_coord, depth = queue.popleft()

            if depth >= max_depth:
                continue

            # Try all 18 moves
            for move_idx in range(18):
                new_eo = moves[0][eo, move_idx]
                new_slice = moves[1][slice_coord, move_idx]

                if table[new_eo, new_slice] == -1:
                    table[new_eo, new_slice] = depth + 1
                    queue.append((new_eo, new_slice, depth + 1))

        # Fill remaining unvisited states with max_depth
        table[table == -1] = max_depth

        return table

    def _generate_phase2_coord(
        self,
        num_states: int,
        coord_name: str,
        max_depth: int
    ) -> np.ndarray:
        """
        Generate a single-coordinate pruning table for Phase 2.

        Args:
            num_states: Number of coordinate states
            coord_name: Name of coordinate ('corner_perm', 'edge_perm', 'slice_perm')
            max_depth: Maximum depth for BFS

        Returns:
            Pruning table
        """
        # Initialize table with -1 (unvisited)
        table = np.full(num_states, -1, dtype=np.int8)

        # Goal state: 0 (solved)
        queue = deque([(0, 0)])  # (coord, depth)
        table[0] = 0

        # Select appropriate move table
        if coord_name == 'corner_perm':
            moves = self.move_tables.corner_perm_moves
        elif coord_name == 'edge_perm':
            moves = self.move_tables.edge_perm_moves
        elif coord_name == 'slice_perm':
            moves = self.move_tables.udslice_perm_moves
        else:
            raise ValueError(f"Unknown coordinate: {coord_name}")

        num_moves = len(PHASE2_MOVES)

        while queue:
            coord, depth = queue.popleft()

            if depth >= max_depth:
                continue

            # Try all Phase 2 moves
            for move_idx in range(num_moves):
                new_coord = moves[coord, move_idx]

                if table[new_coord] == -1:
                    table[new_coord] = depth + 1
                    queue.append((new_coord, depth + 1))

        # Fill remaining unvisited states with max_depth
        table[table == -1] = max_depth

        return table

    def get_phase1_heuristic(
        self,
        corner_orient: int,
        edge_orient: int,
        udslice: int
    ) -> int:
        """
        Get Phase 1 heuristic (minimum moves to reach G1).

        Uses maximum of two table lookups.

        Args:
            corner_orient: Corner orientation coordinate
            edge_orient: Edge orientation coordinate
            udslice: UD-slice coordinate

        Returns:
            Estimated minimum moves to G1
        """
        if not self._loaded:
            raise RuntimeError("Pruning tables not loaded. Call load() first.")

        h1 = self.phase1_co_eo[corner_orient, edge_orient]
        h2 = self.phase1_eo_slice[edge_orient, udslice]

        return max(h1, h2)

    def get_phase2_heuristic(
        self,
        corner_perm: int,
        edge_perm: int,
        udslice_perm: int
    ) -> int:
        """
        Get Phase 2 heuristic (minimum moves to solved state).

        Uses maximum of three table lookups.

        Args:
            corner_perm: Corner permutation coordinate
            edge_perm: Edge permutation coordinate
            udslice_perm: UD-slice permutation coordinate

        Returns:
            Estimated minimum moves to solved state
        """
        if not self._loaded:
            raise RuntimeError("Pruning tables not loaded. Call load() first.")

        h1 = self.phase2_cp[corner_perm]
        h2 = self.phase2_ep[edge_perm]
        h3 = self.phase2_sp[udslice_perm]

        return max(h1, h2, h3)


# Global pruning tables instance
_pruning_tables = None


def get_pruning_tables(cache_dir: str = "data/pruning_tables") -> PruningTables:
    """
    Get the global pruning tables instance.

    Args:
        cache_dir: Directory to cache tables

    Returns:
        PruningTables instance
    """
    global _pruning_tables
    if _pruning_tables is None:
        _pruning_tables = PruningTables(cache_dir)
    return _pruning_tables
