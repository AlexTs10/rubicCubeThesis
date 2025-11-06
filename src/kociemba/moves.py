"""
Move Tables for Kociemba's Two-Phase Algorithm

This module precomputes how each of the 18 moves affects each coordinate.
This allows O(1) coordinate updates during search instead of recomputing.

Move tables are generated once and cached for efficiency.
"""

import numpy as np
import os
import pickle
from typing import Dict, List
from .cubie import CubieCube, ALL_MOVES, apply_move_to_cubie
from .coord import (
    get_corner_orientation, set_corner_orientation,
    get_edge_orientation, set_edge_orientation,
    get_udslice, set_udslice,
    get_corner_permutation, set_corner_permutation,
    get_edge_permutation, set_edge_permutation,
    get_udslice_permutation, set_udslice_permutation
)


# Move names
ALL_MOVE_NAMES = ['U', 'U2', "U'", 'D', 'D2', "D'",
                  'R', 'R2', "R'", 'L', 'L2', "L'",
                  'F', 'F2', "F'", 'B', 'B2', "B'"]

# Phase 1 moves: all 18 moves
PHASE1_MOVES = ALL_MOVE_NAMES

# Phase 2 moves: only half-turns of F, B and quarter-turns of U, D, R, L
PHASE2_MOVES = ['U', 'U2', "U'", 'D', 'D2', "D'",
                'R2', 'L2', 'F2', 'B2']


class MoveTables:
    """
    Precomputed move tables for all coordinates.

    Each table maps (coordinate, move) -> new_coordinate.
    """

    def __init__(self, cache_dir: str = "data/move_tables"):
        """
        Initialize move tables.

        Args:
            cache_dir: Directory to cache precomputed tables
        """
        self.cache_dir = cache_dir

        # Phase 1 coordinate move tables
        self.corner_orient_moves = None  # [2187][18]
        self.edge_orient_moves = None    # [2048][18]
        self.udslice_moves = None        # [495][18]

        # Phase 2 coordinate move tables
        self.corner_perm_moves = None    # [40320][10] (Phase 2 moves only)
        self.edge_perm_moves = None      # [40320][10]
        self.udslice_perm_moves = None   # [24][10]

        self._loaded = False

    def load(self, force_regenerate: bool = False) -> None:
        """
        Load or generate move tables.

        Args:
            force_regenerate: If True, regenerate tables even if cached
        """
        if self._loaded and not force_regenerate:
            return

        cache_file = os.path.join(self.cache_dir, "move_tables.pkl")

        if not force_regenerate and os.path.exists(cache_file):
            print(f"Loading move tables from {cache_file}...")
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                self.corner_orient_moves = data['corner_orient']
                self.edge_orient_moves = data['edge_orient']
                self.udslice_moves = data['udslice']
                self.corner_perm_moves = data['corner_perm']
                self.edge_perm_moves = data['edge_perm']
                self.udslice_perm_moves = data['udslice_perm']
            print("Move tables loaded successfully!")
        else:
            print("Generating move tables...")
            self._generate_tables()
            print("Move tables generated!")

            # Save to cache
            os.makedirs(self.cache_dir, exist_ok=True)
            print(f"Saving move tables to {cache_file}...")
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'corner_orient': self.corner_orient_moves,
                    'edge_orient': self.edge_orient_moves,
                    'udslice': self.udslice_moves,
                    'corner_perm': self.corner_perm_moves,
                    'edge_perm': self.edge_perm_moves,
                    'udslice_perm': self.udslice_perm_moves
                }, f)
            print("Move tables saved!")

        self._loaded = True

    def _generate_tables(self) -> None:
        """Generate all move tables by brute force."""

        # Phase 1 tables (all 18 moves)
        print("  Generating corner orientation table (2187 states)...")
        self.corner_orient_moves = self._generate_coord_table(
            2187, ALL_MOVE_NAMES,
            get_corner_orientation, set_corner_orientation
        )

        print("  Generating edge orientation table (2048 states)...")
        self.edge_orient_moves = self._generate_coord_table(
            2048, ALL_MOVE_NAMES,
            get_edge_orientation, set_edge_orientation
        )

        print("  Generating UD-slice table (495 states)...")
        self.udslice_moves = self._generate_coord_table(
            495, ALL_MOVE_NAMES,
            get_udslice, set_udslice
        )

        # Phase 2 tables (10 moves only)
        print("  Generating corner permutation table (40320 states)...")
        self.corner_perm_moves = self._generate_coord_table(
            40320, PHASE2_MOVES,
            get_corner_permutation, set_corner_permutation
        )

        print("  Generating edge permutation table (40320 states)...")
        self.edge_perm_moves = self._generate_coord_table(
            40320, PHASE2_MOVES,
            get_edge_permutation, set_edge_permutation
        )

        print("  Generating UD-slice permutation table (24 states)...")
        self.udslice_perm_moves = self._generate_coord_table(
            24, PHASE2_MOVES,
            get_udslice_permutation, set_udslice_permutation
        )

    def _generate_coord_table(
        self,
        num_states: int,
        moves: List[str],
        get_coord,
        set_coord
    ) -> np.ndarray:
        """
        Generate a move table for a specific coordinate.

        Args:
            num_states: Number of possible coordinate values
            moves: List of move names to include
            get_coord: Function to get coordinate from cubie
            set_coord: Function to set coordinate in cubie

        Returns:
            Table of shape [num_states][len(moves)]
        """
        table = np.zeros((num_states, len(moves)), dtype=np.int32)

        for coord in range(num_states):
            # Create a cubie with this coordinate
            cubie = CubieCube()
            set_coord(cubie, coord)

            # Apply each move and record result
            for move_idx, move_name in enumerate(moves):
                new_cubie = apply_move_to_cubie(cubie, move_name)
                new_coord = get_coord(new_cubie)
                table[coord, move_idx] = new_coord

        return table

    def apply_move_to_coords(
        self,
        corner_orient: int,
        edge_orient: int,
        udslice: int,
        move: str
    ) -> tuple:
        """
        Apply a move to Phase 1 coordinates.

        Args:
            corner_orient: Corner orientation coordinate
            edge_orient: Edge orientation coordinate
            udslice: UD-slice coordinate
            move: Move name

        Returns:
            Tuple of (new_corner_orient, new_edge_orient, new_udslice)
        """
        if not self._loaded:
            raise RuntimeError("Move tables not loaded. Call load() first.")

        move_idx = ALL_MOVE_NAMES.index(move)

        return (
            self.corner_orient_moves[corner_orient, move_idx],
            self.edge_orient_moves[edge_orient, move_idx],
            self.udslice_moves[udslice, move_idx]
        )

    def apply_move_to_phase2_coords(
        self,
        corner_perm: int,
        edge_perm: int,
        udslice_perm: int,
        move: str
    ) -> tuple:
        """
        Apply a Phase 2 move to Phase 2 coordinates.

        Args:
            corner_perm: Corner permutation coordinate
            edge_perm: Edge permutation coordinate
            udslice_perm: UD-slice permutation coordinate
            move: Move name (must be in PHASE2_MOVES)

        Returns:
            Tuple of (new_corner_perm, new_edge_perm, new_udslice_perm)
        """
        if not self._loaded:
            raise RuntimeError("Move tables not loaded. Call load() first.")

        if move not in PHASE2_MOVES:
            raise ValueError(f"Move {move} not allowed in Phase 2")

        move_idx = PHASE2_MOVES.index(move)

        return (
            self.corner_perm_moves[corner_perm, move_idx],
            self.edge_perm_moves[edge_perm, move_idx],
            self.udslice_perm_moves[udslice_perm, move_idx]
        )


# Global move tables instance
_move_tables = None


def get_move_tables(cache_dir: str = "data/move_tables") -> MoveTables:
    """
    Get the global move tables instance.

    Args:
        cache_dir: Directory to cache tables

    Returns:
        MoveTables instance
    """
    global _move_tables
    if _move_tables is None:
        _move_tables = MoveTables(cache_dir)
    return _move_tables
