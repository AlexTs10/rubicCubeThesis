"""
Unit tests for edge pattern database indexing and loading.
"""

import numpy as np
import pytest

from src.kociemba.coord import factorial
from src.kociemba.cubie import CubieCube
from src.korf.composite_heuristic import CompositeHeuristic
from src.korf.distance_estimator import DistanceEstimator
from src.korf.edge_database import EdgePatternDatabase
from src.korf.pattern_database import PatternDatabase


def _tracked_edge_projection(cubie: CubieCube, edge_subset: list[int]) -> tuple[list[int], list[int], list[int]]:
    """Return the tracked edge positions, piece ids, and orientations."""
    tracked_positions = []
    tracked_pieces = []
    tracked_orient = []
    tracked_piece_ids = set(edge_subset)

    for position, piece in enumerate(cubie.edge_perm):
        if int(piece) not in tracked_piece_ids:
            continue
        tracked_positions.append(position)
        tracked_pieces.append(int(piece))
        tracked_orient.append(int(cubie.edge_orient[position]))

    return tracked_positions, tracked_pieces, tracked_orient


class TestEdgePatternDatabase:
    """Test the corrected tracked-edge coordinate abstraction."""

    def test_edge_index_distinguishes_tracked_positions(self):
        """Tracked edges in different positions must not alias."""
        edge_subset = [0, 1]
        db = EdgePatternDatabase(edge_subset, "edge_test")

        solved = CubieCube()

        shifted = CubieCube()
        shifted.edge_perm = np.array([2, 3, 0, 4, 1, 5, 6, 7, 8, 9, 10, 11], dtype=np.int8)

        assert db.edge_index(solved) != db.edge_index(shifted)

    def test_index_to_edge_state_preserves_tracked_projection(self):
        """Index round-tripping preserves tracked positions, pieces, and orientations."""
        edge_subset = [0, 1]
        db = EdgePatternDatabase(edge_subset, "edge_test")

        state = CubieCube()
        state.edge_perm = np.array([2, 3, 0, 4, 1, 5, 6, 7, 8, 9, 10, 11], dtype=np.int8)
        state.edge_orient = np.array([0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0], dtype=np.int8)

        restored = db.index_to_edge_state(db.edge_index(state))

        assert _tracked_edge_projection(restored, edge_subset) == _tracked_edge_projection(state, edge_subset)


class TestEdgePatternDatabaseConsumers:
    """Test consumers that load or guard edge databases."""

    def test_composite_loader_rejects_legacy_subset_edge_cache(self, tmp_path):
        """Legacy caches from the collapsed abstraction must not load."""
        edge_subset = [0, 1]
        legacy_size = factorial(len(edge_subset)) * (2 ** (len(edge_subset) - 1))
        legacy_db = PatternDatabase("edge_test", legacy_size)
        legacy_path = tmp_path / "edge_test.pkl"
        legacy_db.save(str(legacy_path))

        with pytest.raises(ValueError, match="Size mismatch"):
            CompositeHeuristic._load_edge_database(legacy_path, edge_subset, "edge_test")

    def test_distance_estimator_skips_missing_edges_when_generation_disabled(self, tmp_path):
        """Missing edge caches must not trigger generation when disabled."""
        estimator = DistanceEstimator()

        estimator.load_databases(
            load_corner=False,
            load_edges=True,
            edge1_path=str(tmp_path / "missing_edge1.pkl"),
            edge2_path=str(tmp_path / "missing_edge2.pkl"),
            generate_if_missing=False,
        )

        assert estimator.edge1_db is None
        assert estimator.edge2_db is None
        assert estimator.use_pattern_dbs is False
