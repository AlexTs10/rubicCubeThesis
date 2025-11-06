"""
Pattern Database (Pruning Table) Generation

Generates lookup tables that provide lower bounds on the number of moves
needed to reach the goal state from any given position.

These tables are used as admissible heuristics in the IDA* search.
"""

import numpy as np
import os
import pickle
from typing import Dict, List, Callable
from collections import deque
from ..cube.rubik_cube import RubikCube
from .coordinates import CubeCoordinates


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
            name="phase0_edge_orientation",
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
            name="phase1_corner_eo_eslice",
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
            name="phase2_corner_tetrad",
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
            name="phase3_corner_permutation",
            size=40320,  # 8! = 40,320 corner permutations
            get_coord=get_coord,
            moves=moves,
            cache_dir=self.cache_dir
        )

        self.databases['phase3'] = db
        return db

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
        db0.load_or_generate(max_depth=7)  # Phase 0 max depth is 7

        # Phase 1: Corner orientation + E-slice
        print("\n=== Phase 1: Corner Orientation + E-slice ===")
        db1 = self.initialize_phase_1(phase_moves[1])
        db1.load_or_generate(max_depth=10)  # Phase 1 max depth is 10

        # Phase 2: Corner tetrad
        print("\n=== Phase 2: Corner Tetrad ===")
        db2 = self.initialize_phase_2(phase_moves[2])
        db2.load_or_generate(max_depth=13)  # Phase 2 max depth is 13

        # Phase 3: Corner permutation
        print("\n=== Phase 3: Final Solve ===")
        db3 = self.initialize_phase_3(phase_moves[3])
        db3.load_or_generate(max_depth=15)  # Phase 3 max depth is 15

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
        phase_names = ['phase0', 'phase1', 'phase2', 'phase3']
        if phase < 0 or phase >= len(phase_names):
            raise ValueError(f"Invalid phase: {phase}")

        phase_name = phase_names[phase]
        if phase_name not in self.databases:
            raise KeyError(f"Pattern database for {phase_name} not initialized")

        return self.databases[phase_name]
