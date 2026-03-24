"""
Admissible coordinate heuristics for the native exact solver.

This module builds small exact distance tables for coordinate abstractions that
are valid lower bounds under the repository's move metric. The first version
uses only full-move-safe coordinates whose transitions are already available in
the Kociemba move-table cache:

- corner orientation,
- edge orientation,
- UD-slice position.

These heuristics are weaker than Korf's full corner/edge pattern databases, but
they are native, fast to generate, and fully admissible. When a completed full
corner pattern database is available on disk, this module can compose it with
the smaller coordinate bounds using `max(...)`.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import pickle
from typing import Callable, Dict

import numpy as np

from ..kociemba.coord import (
    get_corner_orientation,
    get_corner_permutation,
    get_edge_orientation,
    get_udslice,
    set_corner_permutation,
)
from ..kociemba.cubie import CubieCube, apply_move_to_cubie
from ..kociemba.moves import ALL_MOVE_NAMES, get_move_tables
from .corner_database import DEFAULT_CORNER_DB_PATH, CornerPatternDatabase, create_corner_database


class NativeCoordinateHeuristic:
    """
    Admissible heuristic built from exact coordinate distance tables.

    The heuristic value is the maximum of the component lower bounds.
    """

    FORMAT_VERSION = 1

    def __init__(
        self,
        cache_dir: str = "data/pattern_databases/native_exact",
        *,
        corner_db: CornerPatternDatabase | None = None,
        corner_db_path: str | None = DEFAULT_CORNER_DB_PATH,
        load_corner_db_if_available: bool = True,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.corner_db = corner_db
        self.corner_db_path = corner_db_path

        move_tables = get_move_tables()
        move_tables.load()

        self.corner_orientation_table = self._load_or_build(
            name="corner_orientation",
            move_table=move_tables.corner_orient_moves,
        )
        self.edge_orientation_table = self._load_or_build(
            name="edge_orientation",
            move_table=move_tables.edge_orient_moves,
        )
        self.udslice_table = self._load_or_build(
            name="udslice_position",
            move_table=move_tables.udslice_moves,
        )
        self.corner_permutation_table = self._load_or_build(
            name="corner_permutation",
            move_table_builder=lambda: self._build_coord_move_table(
                40320,
                get_corner_permutation,
                set_corner_permutation,
            ),
        )

        if self.corner_db is None and load_corner_db_if_available and corner_db_path is not None:
            self.corner_db = self._load_corner_db_if_available(corner_db_path)

    def __call__(self, cubie: CubieCube) -> int:
        """Return an admissible lower bound for the supplied cubie state."""
        return max(self.breakdown(cubie).values())

    def breakdown(self, cubie: CubieCube) -> Dict[str, int]:
        """Return the component lower bounds used by the heuristic."""
        return {
            "corner_orientation": int(self.corner_orientation_table[get_corner_orientation(cubie)]),
            "edge_orientation": int(self.edge_orientation_table[get_edge_orientation(cubie)]),
            "udslice_position": int(self.udslice_table[get_udslice(cubie)]),
            "corner_permutation": int(self.corner_permutation_table[get_corner_permutation(cubie)]),
            **(
                {"corner_pattern_db": int(self.corner_db.get_corner_distance(cubie))}
                if self.corner_db is not None
                else {}
            ),
        }

    def estimate_components(self, cubie: CubieCube) -> Dict[str, int]:
        """Alias used by tests and higher-level reporting."""
        return self.breakdown(cubie)

    def get_statistics(self) -> Dict[str, Dict[str, int]]:
        """Return simple metadata about the generated coordinate tables."""
        tables = {
            "corner_orientation": self.corner_orientation_table,
            "edge_orientation": self.edge_orientation_table,
            "udslice_position": self.udslice_table,
            "corner_permutation": self.corner_permutation_table,
        }
        statistics = {
            name: {
                "size": int(table.shape[0]),
                "max_depth": int(table.max()),
                "memory_bytes": int(table.nbytes),
            }
            for name, table in tables.items()
        }
        if self.corner_db is not None:
            statistics["corner_pattern_db"] = self.corner_db.get_statistics()
        return statistics

    def _cache_path(self, name: str) -> Path:
        return self.cache_dir / f"{name}_v{self.FORMAT_VERSION}.pkl"

    def _load_or_build(
        self,
        *,
        name: str,
        move_table: np.ndarray | None = None,
        move_table_builder: Callable[[], np.ndarray] | None = None,
    ) -> np.ndarray:
        path = self._cache_path(name)
        if path.exists():
            with open(path, "rb") as fh:
                payload = pickle.load(fh)
            if payload.get("format_version") == self.FORMAT_VERSION:
                return payload["distance_table"]

        if move_table is None:
            if move_table_builder is None:
                raise ValueError(f"No move table source provided for {name}")
            move_table = move_table_builder()

        distance_table = self._build_distance_table(move_table)
        with open(path, "wb") as fh:
            pickle.dump(
                {
                    "format_version": self.FORMAT_VERSION,
                    "name": name,
                    "distance_table": distance_table,
                },
                fh,
                protocol=pickle.HIGHEST_PROTOCOL,
            )
        return distance_table

    @staticmethod
    def _build_distance_table(move_table: np.ndarray) -> np.ndarray:
        """Breadth-first search from the solved coordinate."""
        size = int(move_table.shape[0])
        distance_table = np.full(size, 255, dtype=np.uint8)
        distance_table[0] = 0

        queue = deque([0])
        while queue:
            coord = queue.popleft()
            next_distance = int(distance_table[coord]) + 1
            for next_coord in move_table[coord]:
                next_coord = int(next_coord)
                if distance_table[next_coord] != 255:
                    continue
                distance_table[next_coord] = next_distance
                queue.append(next_coord)

        return distance_table

    @staticmethod
    def _build_coord_move_table(num_states, get_coord, set_coord) -> np.ndarray:
        """Build a full 18-move coordinate transition table."""
        table = np.zeros((num_states, len(ALL_MOVE_NAMES)), dtype=np.int32)
        for coord in range(num_states):
            cubie = CubieCube()
            set_coord(cubie, coord)
            for move_idx, move_name in enumerate(ALL_MOVE_NAMES):
                next_cubie = apply_move_to_cubie(cubie, move_name)
                table[coord, move_idx] = get_coord(next_cubie)
        return table

    @staticmethod
    def _load_corner_db_if_available(corner_db_path: str) -> CornerPatternDatabase | None:
        """Load the full corner database only when a complete cache already exists."""
        try:
            return create_corner_database(
                load_if_exists=True,
                save_path=corner_db_path,
                generate_if_missing=False,
                require_complete=True,
                verbose=False,
            )
        except (FileNotFoundError, ValueError):
            return None


def create_native_coordinate_heuristic(
    cache_dir: str = "data/pattern_databases/native_exact",
    auto_generate: bool = True,
    *,
    corner_db: CornerPatternDatabase | None = None,
    corner_db_path: str | None = DEFAULT_CORNER_DB_PATH,
    load_corner_db_if_available: bool = True,
) -> NativeCoordinateHeuristic:
    """Convenience constructor for the native coordinate heuristic."""
    del auto_generate  # Small coordinate tables are always generated if missing.
    return NativeCoordinateHeuristic(
        cache_dir=cache_dir,
        corner_db=corner_db,
        corner_db_path=corner_db_path,
        load_corner_db_if_available=load_corner_db_if_available,
    )
