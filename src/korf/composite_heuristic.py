"""
Composite Heuristic for Rubik's Cube - Exploratory Path

This module implements a composite heuristic that combines multiple inexpensive
estimates. It is useful for practical search experiments, but the composite
path is not treated as a formal admissible lower bound in this repository.

Exploratory strategy:
The composite heuristic uses dynamic weighting based on cube state characteristics:
1. Early scramble detection (high entropy) → emphasize pattern databases
2. Near-solved states (low entropy) → emphasize Manhattan distance
3. Mid-range states → balanced combination

This adaptive approach is kept for practical experiments; the committed thesis
benchmark does not treat it as a proven improvement without a separate ablation.

Research Justification:
- Korf (1997) showed pattern databases are strongest for deep scrambles
- Manhattan distance is computationally cheaper for shallow states
- Combining them adaptively is a plausible experimental strategy for the
  practical IDA* fallback path

Pattern-database mode is optional: when cached Korf tables are available,
they are used directly; otherwise the heuristic falls back to the cheaper
approximate estimate instead of attempting to regenerate enormous tables.

Author: Alex Toska
Date: November 2025
"""

from pathlib import Path
from typing import Dict
from ..cube.rubik_cube import RubikCube
from ..kociemba.cubie import CubieCube, from_facelet_cube
from .pattern_database import PatternDatabase
from .corner_database import CornerPatternDatabase
from .edge_database import EDGE_GROUP_1, EDGE_GROUP_2, EdgePatternDatabase
from .heuristics import (
    manhattan_distance,
    hamming_distance,
    manhattan_distance_corner,
    manhattan_distance_edge
)


class StateAnalyzer:
    """
    Analyzes cube state characteristics to inform heuristic selection.
    """

    @staticmethod
    def calculate_entropy(cube: RubikCube) -> float:
        """
        Calculate the entropy (disorder) of the cube state.

        Higher entropy indicates more scrambled state.
        Uses color distribution across faces as a measure.

        Args:
            cube: Rubik's cube state

        Returns:
            Entropy value (0.0 = solved, 1.0 = maximally scrambled)
        """
        if cube.is_solved():
            return 0.0

        total_misplaced = 0
        max_misplaced = 48  # 6 faces × 8 non-center stickers

        for face_idx in range(6):
            face_state = cube.state[face_idx]
            center_color = face_state[4]

            # Count misplaced stickers
            for i in range(9):
                if i != 4 and face_state[i] != center_color:
                    total_misplaced += 1

        return min(total_misplaced / max_misplaced, 1.0)

    @staticmethod
    def calculate_separation(cubie: CubieCube) -> float:
        """
        Calculate average positional separation of pieces.

        Measures how far pieces are from their home positions.

        Args:
            cubie: Cubie cube representation

        Returns:
            Average separation distance (0.0 to 1.0)
        """
        # Count positions that are not home
        corner_separation = sum(1 for i in range(8) if cubie.corner_perm[i] != i)
        edge_separation = sum(1 for i in range(12) if cubie.edge_perm[i] != i)

        total_separation = corner_separation + edge_separation
        max_separation = 20  # 8 corners + 12 edges

        return total_separation / max_separation

    @staticmethod
    def has_oriented_layer(cube: RubikCube) -> bool:
        """
        Check if any face has all edges correctly oriented.

        This indicates a partially solved state where simpler
        heuristics may be more effective.

        Args:
            cube: Rubik's cube state

        Returns:
            True if any face has all edges matching center color
        """
        for face_idx in range(6):
            face_state = cube.state[face_idx]
            center_color = face_state[4]

            # Check edge pieces (positions 1, 3, 5, 7)
            edge_positions = [1, 3, 5, 7]
            if all(face_state[pos] == center_color for pos in edge_positions):
                return True

        return False


class CompositeHeuristic:
    """
    Novel composite heuristic combining multiple estimation strategies.

    Research Contribution:
    This heuristic adapts its weighting based on cube state analysis,
    providing better estimates across varying scramble depths.

    Approach:
    1. Analyze state characteristics (entropy, separation, partial solutions)
    2. Select primary and secondary heuristics based on state
    3. Combine using maximum for a conservative practical estimate
    4. Apply learning-based adjustment factors
    """

    def __init__(
        self,
        use_pattern_db: bool = False,
        pattern_db_cache_dir: str = "data/pattern_databases/korf"
    ):
        """
        Initialize composite heuristic.

        Args:
            use_pattern_db: Whether to use pattern databases (expensive)
            pattern_db_cache_dir: Directory containing optional Korf cache files
        """
        self.use_pattern_db = use_pattern_db
        self.analyzer = StateAnalyzer()

        # Pattern databases are loaded from cache files if available.
        self.pattern_db_cache_dir = Path(pattern_db_cache_dir)
        self.corner_db = None
        self.edge1_db = None
        self.edge2_db = None
        self._pattern_db_initialized = False
        self.pattern_db_loaded = False
        self.pattern_db_status = "disabled" if not use_pattern_db else "not loaded"

        # Performance tracking
        self.calls = 0
        self.avg_entropy = 0.0

    def __call__(self, cube: RubikCube) -> float:
        """
        Evaluate the composite heuristic.

        Args:
            cube: Rubik's cube state

        Returns:
            Estimated distance to solved state
        """
        self.calls += 1

        if cube.is_solved():
            return 0.0

        # Convert to cubie representation
        cubie = from_facelet_cube(cube)

        # Analyze state
        entropy = self.analyzer.calculate_entropy(cube)
        separation = self.analyzer.calculate_separation(cubie)
        has_layer = self.analyzer.has_oriented_layer(cube)

        # Update rolling average
        self.avg_entropy = (self.avg_entropy * (self.calls - 1) + entropy) / self.calls

        # Strategy 1: Near-solved states (low entropy)
        if entropy < 0.3 or has_layer:
            return self._near_solved_strategy(cube, cubie)

        # Strategy 2: Highly scrambled states (high entropy)
        elif entropy > 0.7:
            return self._deep_scramble_strategy(cube, cubie)

        # Strategy 3: Mid-range states
        else:
            return self._balanced_strategy(cube, cubie, entropy)

    def _near_solved_strategy(self, cube: RubikCube, cubie: CubieCube) -> float:
        """
        Strategy for near-solved states.

        Emphasizes Manhattan distance which is fast and accurate
        for states close to solution.

        Args:
            cube: Rubik's cube state
            cubie: Cubie representation

        Returns:
            Heuristic estimate
        """
        # Use Manhattan distance components
        corner_dist = manhattan_distance_corner(cubie)
        edge_dist = manhattan_distance_edge(cubie)

        # Return the larger normalized component.
        return max(corner_dist, edge_dist)

    def _deep_scramble_strategy(self, cube: RubikCube, cubie: CubieCube) -> float:
        """
        Strategy for deeply scrambled states.

        Uses pattern databases if available, otherwise enhanced Manhattan.

        Args:
            cube: Rubik's cube state
            cubie: Cubie representation

        Returns:
            Heuristic estimate
        """
        if self.use_pattern_db:
            # Pattern database lookup (if available)
            return self._pattern_db_heuristic(cubie)
        else:
            # Enhanced Manhattan with orientation penalties
            return self._enhanced_manhattan(cubie)

    def _balanced_strategy(
        self,
        cube: RubikCube,
        cubie: CubieCube,
        entropy: float
    ) -> float:
        """
        Balanced strategy for mid-range states.

        Combines multiple heuristics using the maximum.

        Args:
            cube: Rubik's cube state
            cubie: Cubie representation
            entropy: Current state entropy

        Returns:
            Heuristic estimate
        """
        # Compute multiple heuristics
        hamming = hamming_distance(cube)
        manhattan = manhattan_distance(cube)

        # Enhanced Manhattan
        enhanced = self._enhanced_manhattan(cubie)

        # Return the strongest of the available approximate signals.
        return max(hamming, manhattan, enhanced)

    def _enhanced_manhattan(self, cubie: CubieCube) -> float:
        """
        Enhanced Manhattan distance with orientation weighting.

        Research Innovation:
        Adds small penalties for orientation mismatches that standard
        Manhattan misses.

        Args:
            cubie: Cubie representation

        Returns:
            Enhanced Manhattan estimate
        """
        # Base Manhattan distance
        corner_dist = 0
        edge_dist = 0

        # Corner analysis with orientation
        for i in range(8):
            if cubie.corner_perm[i] != i:
                corner_dist += 1

            # Small orientation penalty for practical search guidance.
            if cubie.corner_orient[i] != 0:
                corner_dist += 0.5  # Half move penalty

        # Edge analysis with orientation
        for i in range(12):
            if cubie.edge_perm[i] != i:
                edge_dist += 1

            if cubie.edge_orient[i] != 0:
                edge_dist += 0.5

        # Divide by pieces affected per move
        corner_estimate = corner_dist / 4.0
        edge_estimate = edge_dist / 4.0

        return max(corner_estimate, edge_estimate)

    def _pattern_db_heuristic(self, cubie: CubieCube) -> float:
        """
        Pattern database heuristic (if databases are loaded).

        Args:
            cubie: Cubie representation

        Returns:
            Pattern database estimate
        """
        if not self._load_pattern_databases():
            return self._enhanced_manhattan(cubie)

        distances = []
        try:
            if self.corner_db is not None:
                distances.append(self.corner_db.get_corner_distance(cubie))
            if self.edge1_db is not None:
                distances.append(self.edge1_db.get_edge_distance(cubie))
            if self.edge2_db is not None:
                distances.append(self.edge2_db.get_edge_distance(cubie))
        except Exception:
            # Fall back on cache corruption or lookup errors.
            return self._enhanced_manhattan(cubie)

        if not distances:
            self.pattern_db_status = "unavailable (no databases loaded)"
            return self._enhanced_manhattan(cubie)

        # Return the strongest loaded database distance.
        return max(distances)

    def _load_pattern_databases(self) -> bool:
        """
        Load pattern databases from cache if available.

        The repository does not ship the expensive Korf caches by default.
        When they are absent, the heuristic degrades to the cheaper strategy
        instead of trying to regenerate multi-gigabyte tables.
        """
        if self._pattern_db_initialized:
            return self.pattern_db_loaded

        self._pattern_db_initialized = True

        cache_files = {
            "corner": self.pattern_db_cache_dir / "corner_db.pkl",
            "edge1": self.pattern_db_cache_dir / "edge1_db.pkl",
            "edge2": self.pattern_db_cache_dir / "edge2_db.pkl",
        }

        missing = [name for name, path in cache_files.items() if not path.exists()]
        if missing:
            self.pattern_db_status = (
                f"unavailable (missing cache files: {', '.join(missing)})"
            )
            return False

        try:
            self.corner_db = self._load_corner_database(cache_files["corner"])
            self.edge1_db = self._load_edge_database(cache_files["edge1"], EDGE_GROUP_1, "edge1")
            self.edge2_db = self._load_edge_database(cache_files["edge2"], EDGE_GROUP_2, "edge2")
        except Exception as exc:
            self.corner_db = None
            self.edge1_db = None
            self.edge2_db = None
            self.pattern_db_status = f"unavailable ({exc})"
            return False

        self.pattern_db_loaded = True
        self.pattern_db_status = f"loaded from {self.pattern_db_cache_dir}"
        return True

    @staticmethod
    def _load_corner_database(cache_path: Path) -> CornerPatternDatabase:
        """Load a serialized corner pattern database into the concrete wrapper."""
        loaded = PatternDatabase.load(str(cache_path))
        corner_db = CornerPatternDatabase()
        corner_db.copy_storage_from(loaded)
        return corner_db

    @staticmethod
    def _load_edge_database(
        cache_path: Path,
        edge_subset,
        name: str
    ) -> EdgePatternDatabase:
        """Load a serialized edge pattern database into the concrete wrapper."""
        loaded = PatternDatabase.load(str(cache_path))
        edge_db = EdgePatternDatabase(edge_subset, name)
        edge_db.copy_storage_from(loaded)
        if not edge_db.is_complete():
            raise ValueError(
                f"Edge database at {cache_path} is incomplete "
                f"({edge_db.initialized_count():,}/{edge_db.size:,} states)"
            )
        return edge_db

    def get_statistics(self) -> Dict[str, object]:
        """
        Get statistics about heuristic usage.

        Returns:
            Dictionary with usage statistics
        """
        return {
            'total_calls': self.calls,
            'average_entropy': self.avg_entropy,
            'using_pattern_db': self.use_pattern_db,
            'pattern_db_loaded': self.pattern_db_loaded,
            'pattern_db_status': self.pattern_db_status,
            'pattern_db_cache_dir': str(self.pattern_db_cache_dir),
        }


class WeightedCompositeHeuristic:
    """
    Alternative composite approach using weighted combination.

    This is NOT admissible but can be useful for non-optimal solvers
    or as an upper bound for branch-and-bound algorithms.
    """

    def __init__(self):
        """Initialize weighted composite heuristic."""
        self.analyzer = StateAnalyzer()

    def __call__(self, cube: RubikCube) -> float:
        """
        Evaluate weighted composite (non-admissible).

        Args:
            cube: Rubik's cube state

        Returns:
            Weighted heuristic estimate
        """
        if cube.is_solved():
            return 0.0

        # Compute all heuristics
        hamming = hamming_distance(cube)
        manhattan = manhattan_distance(cube)

        # Analyze state
        entropy = self.analyzer.calculate_entropy(cube)

        # Weight based on entropy
        # Low entropy: favor Manhattan (more accurate near solution)
        # High entropy: favor Hamming (broader overview)
        weight_hamming = entropy
        weight_manhattan = 1.0 - entropy

        # Weighted combination
        estimate = (weight_hamming * hamming + weight_manhattan * manhattan)

        return estimate


# Factory function for easy heuristic creation
def create_heuristic(heuristic_type: str = 'composite', **kwargs) -> callable:
    """
    Factory function to create heuristic functions.

    Args:
        heuristic_type: Type of heuristic to create
            - 'manhattan': Standard Manhattan distance
            - 'hamming': Hamming distance
            - 'composite': Composite practical heuristic (not used for proofs)
            - 'weighted': Weighted composite (non-admissible)
        **kwargs: Additional arguments for heuristic initialization

    Returns:
        Heuristic function
    """
    if heuristic_type == 'manhattan':
        return manhattan_distance
    elif heuristic_type == 'hamming':
        return hamming_distance
    elif heuristic_type == 'composite':
        return CompositeHeuristic(**kwargs)
    elif heuristic_type == 'weighted':
        return WeightedCompositeHeuristic()
    else:
        raise ValueError(f"Unknown heuristic type: {heuristic_type}")
