"""
Pattern Database (Pruning Table) Generation

Generates lookup tables that provide lower bounds on the number of moves
needed to reach the goal state from any given position.

These tables are used as admissible heuristics in the IDA* search.
"""

import numpy as np
import os
import pickle
from typing import Dict, List, Callable, Optional, Set, Tuple
from collections import deque
from ..cube.rubik_cube import RubikCube
from .coordinates import CubeCoordinates
from ..kociemba.moves import (
    ALL_MOVE_NAMES as KOCIEMBA_ALL_MOVES,
    PHASE2_MOVES as KOCIEMBA_PHASE2_MOVES,
    get_move_tables,
)


class PatternDatabase:
    """
    Pattern database for storing pre-computed distances to goal.

    Uses breadth-first search from the goal state to populate the table.
    """

    def __init__(
        self,
        name: str,
        size: int,
        get_coord: Callable[[RubikCube], int],
        moves: List[str],
        cache_dir: str = "data/pattern_databases"
    ):
        """
        Initialize pattern database.

        Args:
            name: Name of this database (for caching)
            size: Size of the coordinate space
            get_coord: Function to extract coordinate from cube state
            moves: Allowed moves for this phase
            cache_dir: Directory to cache generated tables
        """
        self.name = name
        self.size = size
        self.get_coord = get_coord
        self.moves = moves
        self.cache_dir = cache_dir

        # Initialize table with "unknown" (255 = max value for uint8)
        self.table = np.full(size, 255, dtype=np.uint8)

        # Cache file path
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, f"{name}.pkl")

    def generate(self, max_depth: int = 20) -> None:
        """
        Generate the pattern database using BFS from solved state.

        Args:
            max_depth: Maximum depth to search (typically 12-15 for Thistlethwaite)
        """
        print(f"Generating pattern database '{self.name}' (size={self.size})...")

        # Start from solved cube
        solved_cube = RubikCube()
        goal_coord = self.get_coord(solved_cube)

        # BFS queue: (cube_state, depth)
        queue = deque([(solved_cube, 0)])
        self.table[goal_coord] = 0

        visited = {goal_coord}
        nodes_processed = 0

        while queue:
            cube, depth = queue.popleft()
            nodes_processed += 1

            if nodes_processed % 100000 == 0:
                print(f"  Processed {nodes_processed} nodes, depth {depth}, "
                      f"queue size {len(queue)}")

            # Don't expand beyond max depth
            if depth >= max_depth:
                continue

            # Try all moves
            for move in self.moves:
                next_cube = cube.copy()
                next_cube.apply_move(move)

                coord = self.get_coord(next_cube)

                if coord not in visited:
                    visited.add(coord)
                    self.table[coord] = depth + 1
                    queue.append((next_cube, depth + 1))

        print(f"  Completed! Processed {nodes_processed} nodes")
        print(f"  Visited {len(visited)} / {self.size} states "
              f"({100 * len(visited) / self.size:.1f}%)")

    def load_or_generate(self, max_depth: int = 20) -> None:
        """
        Load cached table if available, otherwise generate and cache.

        Args:
            max_depth: Maximum depth for generation
        """
        if os.path.exists(self.cache_file):
            print(f"Loading cached pattern database '{self.name}'...")
            with open(self.cache_file, 'rb') as f:
                self.table = pickle.load(f)
            print(f"  Loaded {self.size} entries")
        else:
            self.generate(max_depth)
            self.save()

    def save(self) -> None:
        """Save table to cache file."""
        print(f"Saving pattern database '{self.name}' to {self.cache_file}...")
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.table, f)
        print(f"  Saved")

    def lookup(self, cube: RubikCube) -> int:
        """
        Look up the heuristic value for a cube state.

        Args:
            cube: Cube state

        Returns:
            Lower bound on number of moves to goal
        """
        coord = self.get_coord(cube)
        value = self.table[coord]

        # Return 0 for unknown states (shouldn't happen with full generation)
        return 0 if value == 255 else int(value)


class ThistlethwaitePatternDatabases:
    """
    Collection of pattern databases for all phases of Thistlethwaite's algorithm.
    """

    def __init__(self, cache_dir: str = "data/pattern_databases"):
        """
        Initialize pattern database collection.

        Args:
            cache_dir: Directory to cache generated tables
        """
        self.cache_dir = cache_dir
        self.databases: Dict[str, PatternDatabase] = {}
        self.phase3_distances: Dict[int, int] = {}
        self.phase3_goal_corner_perms: Set[int] = set()
        self.phase3_goal_edge_perms: Set[int] = set()
        self.phase3_goal_slice_perms: Set[int] = set()
        self.phase2_corner_to_g3: Optional[np.ndarray] = None
        self.phase2_edge_to_g3: Optional[np.ndarray] = None
        self.phase2_slice_to_g3: Optional[np.ndarray] = None
        self.phase3_moves: List[str] = []
        self.phase3_move_indices: List[int] = []

    def initialize_phase_0(self, moves: List[str]) -> PatternDatabase:
        """
        Initialize pattern database for Phase 0 (G0 → G1: Edge Orientation).

        Args:
            moves: Allowed moves for phase 0

        Returns:
            Pattern database for phase 0
        """
        def get_coord(cube: RubikCube) -> int:
            coords = CubeCoordinates(cube)
            return coords.get_edge_orientation_coord()

        db = PatternDatabase(
            name="phase0_edge_orientation_v3",
            size=2048,  # 2^11 edge orientations
            get_coord=get_coord,
            moves=moves,
            cache_dir=self.cache_dir
        )

        self.databases['phase0'] = db
        return db

    def initialize_phase_1(self, moves: List[str]) -> PatternDatabase:
        """
        Initialize pattern database for Phase 1 (G1 → G2).

        This phase has two coordinates: corner orientation and E-slice edges.
        For simplicity, we use corner orientation as the primary heuristic.

        Args:
            moves: Allowed moves for phase 1

        Returns:
            Pattern database for phase 1
        """
        def get_coord(cube: RubikCube) -> int:
            coords = CubeCoordinates(cube)
            # Combine corner orientation and E-slice
            co = coords.get_corner_orientation_coord()
            es = coords.get_e_slice_coord()
            # Combined coordinate (requires more memory)
            return co * 495 + es

        db = PatternDatabase(
            name="phase1_corner_eo_eslice_v3",
            size=2187 * 495,  # 3^7 * C(12,4) = ~1M entries
            get_coord=get_coord,
            moves=moves,
            cache_dir=self.cache_dir
        )

        self.databases['phase1'] = db
        return db

    def initialize_phase_2(self, moves: List[str]) -> PatternDatabase:
        """
        Initialize pattern database for Phase 2 (G2 → G3).

        Uses corner tetrad coordinate as heuristic.

        Args:
            moves: Allowed moves for phase 2

        Returns:
            Pattern database for phase 2
        """
        def get_coord(cube: RubikCube) -> int:
            coords = CubeCoordinates(cube)
            return coords.get_corner_tetrad_coord()

        db = PatternDatabase(
            name="phase2_corner_tetrad_v3",
            size=70,  # C(8,4) = 70 combinations
            get_coord=get_coord,
            moves=moves,
            cache_dir=self.cache_dir
        )

        self.databases['phase2'] = db
        return db

    def initialize_phase_3(self, moves: List[str]) -> PatternDatabase:
        """
        Initialize pattern database for Phase 3 (G3 → G4).

        Uses corner permutation as heuristic.

        Args:
            moves: Allowed moves for phase 3

        Returns:
            Pattern database for phase 3
        """
        def get_coord(cube: RubikCube) -> int:
            coords = CubeCoordinates(cube)
            return coords.get_corner_permutation_coord()

        db = PatternDatabase(
            name="phase3_corner_permutation_v3",
            size=40320,  # 8! = 40,320 corner permutations
            get_coord=get_coord,
            moves=moves,
            cache_dir=self.cache_dir
        )

        self.databases['phase3'] = db
        return db

    @staticmethod
    def pack_phase3_state(corner_perm: int, edge_perm: int, slice_perm: int) -> int:
        """Pack the exact G3 state tuple into a single integer key."""
        return ((corner_perm * 40320) + edge_perm) * 24 + slice_perm

    @staticmethod
    def unpack_phase3_state(key: int) -> Tuple[int, int, int]:
        """Unpack a packed G3 state key into (corner_perm, edge_perm, slice_perm)."""
        slice_perm = key % 24
        key //= 24
        edge_perm = key % 40320
        corner_perm = key // 40320
        return corner_perm, edge_perm, slice_perm

    def _phase3_key_from_cube(self, cube: RubikCube) -> int:
        """Get the packed exact G3-state key for a cube."""
        coords = CubeCoordinates(cube)
        return self.pack_phase3_state(
            coords.get_corner_permutation_coord(),
            coords.get_ud_edge_permutation_coord(),
            coords.get_e_edge_permutation_coord(),
        )

    def _cache_path(self, name: str) -> str:
        """Return the on-disk cache path for a custom table."""
        os.makedirs(self.cache_dir, exist_ok=True)
        return os.path.join(self.cache_dir, f"{name}.pkl")

    @staticmethod
    def _load_cached_table(db: PatternDatabase) -> bool:
        """Load a cached table into the provided database if it exists."""
        if not os.path.exists(db.cache_file):
            return False

        print(f"Loading cached pattern database '{db.name}'...")
        with open(db.cache_file, 'rb') as f:
            db.table = pickle.load(f)
        print(f"  Loaded {db.size} entries")
        return True

    def _generate_phase0_from_move_tables(
        self,
        db: PatternDatabase,
        max_depth: int,
    ) -> None:
        """Generate the Phase 0 edge-orientation table via coordinate BFS."""
        if self._load_cached_table(db):
            return

        print(f"Generating pattern database '{db.name}' (size={db.size})...")
        move_tables = get_move_tables()
        move_tables.load()
        move_indices = [KOCIEMBA_ALL_MOVES.index(move) for move in db.moves]

        table = np.full(db.size, 255, dtype=np.uint8)
        table[0] = 0
        queue = deque([(0, 0)])

        while queue:
            coord, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for move_idx in move_indices:
                next_coord = int(move_tables.edge_orient_moves[coord, move_idx])
                if table[next_coord] == 255:
                    table[next_coord] = depth + 1
                    queue.append((next_coord, depth + 1))

        db.table = table
        known = int(np.count_nonzero(table != 255))
        print(f"  Visited {known} / {db.size} states ({100 * known / db.size:.1f}%)")
        db.save()

    def _generate_phase1_from_move_tables(
        self,
        db: PatternDatabase,
        max_depth: int,
    ) -> None:
        """Generate the Phase 1 corner-orientation/E-slice table via coordinate BFS."""
        if self._load_cached_table(db):
            return

        print(f"Generating pattern database '{db.name}' (size={db.size})...")
        move_tables = get_move_tables()
        move_tables.load()
        move_indices = [KOCIEMBA_ALL_MOVES.index(move) for move in db.moves]

        table = np.full(db.size, 255, dtype=np.uint8)
        table[0] = 0
        queue = deque([(0, 0, 0)])  # (corner_orient, e_slice, depth)

        while queue:
            corner_orient, e_slice, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for move_idx in move_indices:
                next_corner_orient = int(
                    move_tables.corner_orient_moves[corner_orient, move_idx]
                )
                next_e_slice = int(move_tables.udslice_moves[e_slice, move_idx])
                combined = next_corner_orient * 495 + next_e_slice
                if table[combined] == 255:
                    table[combined] = depth + 1
                    queue.append((next_corner_orient, next_e_slice, depth + 1))

        db.table = table
        known = int(np.count_nonzero(table != 255))
        print(f"  Visited {known} / {db.size} states ({100 * known / db.size:.1f}%)")
        db.save()

    def _generate_phase3_from_move_tables(
        self,
        db: PatternDatabase,
        max_depth: int,
    ) -> None:
        """Generate the Phase 3 corner-permutation table via coordinate BFS."""
        if self._load_cached_table(db):
            return

        print(f"Generating pattern database '{db.name}' (size={db.size})...")
        move_tables = get_move_tables()
        move_tables.load()
        move_indices = [KOCIEMBA_PHASE2_MOVES.index(move) for move in db.moves]

        table = np.full(db.size, 255, dtype=np.uint8)
        table[0] = 0
        queue = deque([(0, 0)])

        while queue:
            coord, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for move_idx in move_indices:
                next_coord = int(move_tables.corner_perm_moves[coord, move_idx])
                if table[next_coord] == 255:
                    table[next_coord] = depth + 1
                    queue.append((next_coord, depth + 1))

        db.table = table
        known = int(np.count_nonzero(table != 255))
        print(f"  Visited {known} / {db.size} states ({100 * known / db.size:.1f}%)")
        db.save()

    def _derive_phase3_goal_projections(self) -> None:
        """Project the exact G3 subgroup onto the coordinate spaces used in Phase 2."""
        self.phase3_goal_corner_perms = set()
        self.phase3_goal_edge_perms = set()
        self.phase3_goal_slice_perms = set()

        for key in self.phase3_distances:
            corner_perm, edge_perm, slice_perm = self.unpack_phase3_state(key)
            self.phase3_goal_corner_perms.add(corner_perm)
            self.phase3_goal_edge_perms.add(edge_perm)
            self.phase3_goal_slice_perms.add(slice_perm)

    def _load_or_generate_phase3_exact(self, moves: List[str]) -> None:
        """
        Load or generate the exact G3 half-turn subgroup table.

        The old implementation approximated G3 with tetrads/parity and a
        corner-only phase-3 table. That admitted states which were not actually
        solvable using only half turns. Here we enumerate the full half-turn
        subgroup exactly in (corner_perm, edge_perm, slice_perm) space.
        """
        self.phase3_moves = moves
        self.phase3_move_indices = [KOCIEMBA_PHASE2_MOVES.index(move) for move in moves]
        cache_file = self._cache_path("phase3_exact_g3_v4")

        if os.path.exists(cache_file):
            print("Loading cached exact phase-3 subgroup table 'phase3_exact_g3_v4'...")
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            self.phase3_distances = data["distances"] if isinstance(data, dict) else data
            self._derive_phase3_goal_projections()
            print(
                "  Loaded "
                f"{len(self.phase3_distances)} exact G3 states "
                f"({len(self.phase3_goal_corner_perms)} corner perms, "
                f"{len(self.phase3_goal_edge_perms)} edge perms, "
                f"{len(self.phase3_goal_slice_perms)} slice perms)"
            )
            return

        print("Generating exact phase-3 half-turn subgroup table 'phase3_exact_g3_v4'...")
        move_tables = get_move_tables()
        move_tables.load()

        distances: Dict[int, int] = {0: 0}
        queue = deque([(0, 0, 0)])

        while queue:
            corner_perm, edge_perm, slice_perm = queue.popleft()
            key = self.pack_phase3_state(corner_perm, edge_perm, slice_perm)
            depth = distances[key]

            if len(distances) % 100000 == 0 and len(queue) % 10000 == 0:
                print(
                    f"  Enumerated {len(distances)} G3 states "
                    f"(queue={len(queue)}, depth={depth})"
                )

            for move_idx in self.phase3_move_indices:
                next_corner_perm = int(move_tables.corner_perm_moves[corner_perm, move_idx])
                next_edge_perm = int(move_tables.edge_perm_moves[edge_perm, move_idx])
                next_slice_perm = int(move_tables.udslice_perm_moves[slice_perm, move_idx])
                next_key = self.pack_phase3_state(
                    next_corner_perm,
                    next_edge_perm,
                    next_slice_perm,
                )
                if next_key in distances:
                    continue

                distances[next_key] = depth + 1
                queue.append((next_corner_perm, next_edge_perm, next_slice_perm))

        self.phase3_distances = distances
        self._derive_phase3_goal_projections()

        print(
            "  Enumerated "
            f"{len(self.phase3_distances)} exact G3 states "
            f"({len(self.phase3_goal_corner_perms)} corner perms, "
            f"{len(self.phase3_goal_edge_perms)} edge perms, "
            f"{len(self.phase3_goal_slice_perms)} slice perms)"
        )
        with open(cache_file, 'wb') as f:
            pickle.dump({"distances": self.phase3_distances}, f)
        print(f"  Saved exact phase-3 subgroup table to {cache_file}")

    def _load_or_generate_goal_distance_table(
        self,
        name: str,
        size: int,
        move_table: np.ndarray,
        goal_coords: Set[int],
    ) -> np.ndarray:
        """
        Multi-source BFS distance table from every coordinate to a goal set.

        This is used for exact admissible phase-2 heuristics toward the true
        G3 subgroup instead of the old tetrad approximation.
        """
        cache_file = self._cache_path(name)

        if os.path.exists(cache_file):
            print(f"Loading cached pattern database '{name}'...")
            with open(cache_file, 'rb') as f:
                table = pickle.load(f)
            print(f"  Loaded {size} entries")
            return table

        print(f"Generating pattern database '{name}' (size={size})...")
        table = np.full(size, 255, dtype=np.uint8)
        queue = deque()

        for coord in sorted(goal_coords):
            table[coord] = 0
            queue.append(coord)

        while queue:
            coord = queue.popleft()
            depth = int(table[coord])
            for next_coord in move_table[coord]:
                next_coord = int(next_coord)
                if table[next_coord] != 255:
                    continue
                table[next_coord] = depth + 1
                queue.append(next_coord)

        with open(cache_file, 'wb') as f:
            pickle.dump(table, f)
        known = int(np.count_nonzero(table != 255))
        print(f"  Visited {known} / {size} states ({100 * known / size:.1f}%)")
        print(f"  Saved to {cache_file}")
        return table

    def _load_or_generate_phase2_exact(self) -> None:
        """Load or generate the exact phase-2 heuristics toward the true G3 subgroup."""
        move_tables = get_move_tables()
        move_tables.load()

        self.phase2_corner_to_g3 = self._load_or_generate_goal_distance_table(
            name="phase2_corner_to_g3_v4",
            size=40320,
            move_table=move_tables.corner_perm_moves,
            goal_coords=self.phase3_goal_corner_perms,
        )
        self.phase2_edge_to_g3 = self._load_or_generate_goal_distance_table(
            name="phase2_edge_to_g3_v4",
            size=40320,
            move_table=move_tables.edge_perm_moves,
            goal_coords=self.phase3_goal_edge_perms,
        )
        self.phase2_slice_to_g3 = self._load_or_generate_goal_distance_table(
            name="phase2_slice_to_g3_v4",
            size=24,
            move_table=move_tables.udslice_perm_moves,
            goal_coords=self.phase3_goal_slice_perms,
        )

    def is_phase3_reachable(self, cube: RubikCube) -> bool:
        """Return True if the cube is in the exact half-turn subgroup G3."""
        coords = CubeCoordinates(cube)
        if coords.get_edge_orientation_coord() != 0:
            return False
        if coords.get_corner_orientation_coord() != 0:
            return False
        if coords.get_e_slice_coord() != 0:
            return False
        return self._phase3_key_from_cube(cube) in self.phase3_distances

    def lookup_phase2(self, cube: RubikCube) -> int:
        """Exact admissible phase-2 heuristic based on distances to the true G3 goal set."""
        if (
            self.phase2_corner_to_g3 is None
            or self.phase2_edge_to_g3 is None
            or self.phase2_slice_to_g3 is None
        ):
            raise RuntimeError("Phase 2 exact tables are not loaded")

        coords = CubeCoordinates(cube)
        corner_distance = int(
            self.phase2_corner_to_g3[coords.get_corner_permutation_coord()]
        )
        edge_distance = int(
            self.phase2_edge_to_g3[coords.get_ud_edge_permutation_coord()]
        )
        slice_distance = int(
            self.phase2_slice_to_g3[coords.get_e_edge_permutation_coord()]
        )

        distances = [corner_distance, edge_distance, slice_distance]
        distances = [0 if distance == 255 else distance for distance in distances]
        return max(distances)

    def lookup_phase3_distance(self, cube: RubikCube) -> Optional[int]:
        """Return the exact phase-3 distance for a G3 state, or None if the state is not in G3."""
        return self.phase3_distances.get(self._phase3_key_from_cube(cube))

    def solve_phase3(self, cube: RubikCube) -> Optional[List[str]]:
        """Solve a G3 state exactly by descending the exact half-turn distance table."""
        if not self.phase3_distances:
            raise RuntimeError("Exact phase-3 table is not loaded")

        coords = CubeCoordinates(cube)
        corner_perm = coords.get_corner_permutation_coord()
        edge_perm = coords.get_ud_edge_permutation_coord()
        slice_perm = coords.get_e_edge_permutation_coord()
        key = self.pack_phase3_state(corner_perm, edge_perm, slice_perm)

        distance = self.phase3_distances.get(key)
        if distance is None:
            return None

        if distance == 0:
            return []

        move_tables = get_move_tables()
        move_tables.load()
        solution: List[str] = []

        while distance > 0:
            found = False
            for move, move_idx in zip(self.phase3_moves, self.phase3_move_indices):
                next_corner_perm = int(move_tables.corner_perm_moves[corner_perm, move_idx])
                next_edge_perm = int(move_tables.edge_perm_moves[edge_perm, move_idx])
                next_slice_perm = int(move_tables.udslice_perm_moves[slice_perm, move_idx])
                next_key = self.pack_phase3_state(
                    next_corner_perm,
                    next_edge_perm,
                    next_slice_perm,
                )
                next_distance = self.phase3_distances.get(next_key)
                if next_distance is None or next_distance != distance - 1:
                    continue

                solution.append(move)
                corner_perm = next_corner_perm
                edge_perm = next_edge_perm
                slice_perm = next_slice_perm
                key = next_key
                distance = next_distance
                found = True
                break

            if not found:
                raise RuntimeError("Exact phase-3 table is inconsistent")

        return solution

    def load_all(self, phase_moves: List[List[str]], max_depth: int = 12) -> None:
        """
        Load or generate all pattern databases.

        Args:
            phase_moves: List of move sets for each phase
            max_depth: Maximum depth for generation
        """
        print("Initializing Thistlethwaite pattern databases...")

        # Phase 0: Edge orientation
        print("\n=== Phase 0: Edge Orientation ===")
        db0 = self.initialize_phase_0(phase_moves[0])
        self._generate_phase0_from_move_tables(db0, max_depth=7)

        # Phase 1: Corner orientation + E-slice
        print("\n=== Phase 1: Corner Orientation + E-slice ===")
        db1 = self.initialize_phase_1(phase_moves[1])
        self._generate_phase1_from_move_tables(db1, max_depth=10)

        # Phase 3 exact subgroup first, because phase 2 heuristics depend on it.
        print("\n=== Phase 3: Exact Half-Turn Subgroup ===")
        self._load_or_generate_phase3_exact(phase_moves[3])

        # Phase 2: exact distances to the true G3 goal set
        print("\n=== Phase 2: Exact Distance-To-G3 Heuristics ===")
        self._load_or_generate_phase2_exact()

        print("\n=== All pattern databases loaded ===\n")

    def get_database(self, phase: int) -> PatternDatabase:
        """
        Get pattern database for a specific phase.

        Args:
            phase: Phase number (0-3)

        Returns:
            Pattern database for the phase

        Raises:
            KeyError: If phase database not initialized
        """
        phase_names = ['phase0', 'phase1']
        if phase < 0 or phase >= len(phase_names):
            raise ValueError(f"PatternDatabase lookup is only supported for phases 0 and 1, got {phase}")

        phase_name = phase_names[phase]
        if phase_name not in self.databases:
            raise KeyError(f"Pattern database for {phase_name} not initialized")

        return self.databases[phase_name]
