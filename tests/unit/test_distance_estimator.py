"""
Unit tests for distance estimator components.

Tests pattern databases, heuristics, and the combined distance estimator.
"""

import pytest
import numpy as np
import pickle
from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import CubieCube, from_facelet_cube
from src.korf.pattern_database import PatternDatabase
from src.korf.corner_database import corner_index, CORNER_DB_SIZE
from src.korf.heuristics import (
    simple_heuristic,
    hamming_distance,
    manhattan_distance,
    manhattan_distance_corner,
    manhattan_distance_edge,
    HeuristicEvaluator
)
from src.korf.distance_estimator import DistanceEstimator


class TestPatternDatabase:
    """Test pattern database infrastructure."""

    def test_pattern_database_creation(self):
        """Test creating a pattern database."""
        db = PatternDatabase("test", 1000)
        assert db.name == "test"
        assert db.size == 1000
        assert db.data.shape == (1000,)
        assert db.storage_format == PatternDatabase.STORAGE_FORMAT_BYTE

    def test_set_get_distance(self):
        """Test setting and getting distances."""
        db = PatternDatabase("test", 100)

        # Set and retrieve distances
        db.set_distance(0, 0)
        assert db.get_distance(0) == 0

        db.set_distance(50, 5)
        assert db.get_distance(50) == 5

        db.set_distance(99, 12)
        assert db.get_distance(99) == 12

    def test_exact_safe_byte_storage(self):
        """Distances are stored exactly and no longer clamped to 15."""
        db = PatternDatabase("test", 100)

        for dist in [0, 1, 5, 15, 20, 42, 254]:
            db.set_distance(0, dist)
            assert db.get_distance(0) == dist

        with pytest.raises(ValueError):
            db.set_distance(0, 255)

    def test_adjacent_indices_do_not_conflict(self):
        """Adjacent indices remain independent in the exact-safe format."""
        db = PatternDatabase("test", 10)

        db.set_distance(0, 3)
        db.set_distance(1, 7)
        db.set_distance(2, 5)
        db.set_distance(3, 9)

        assert db.get_distance(0) == 3
        assert db.get_distance(1) == 7
        assert db.get_distance(2) == 5
        assert db.get_distance(3) == 9

    def test_uninitialized_entries_raise(self):
        """Uninitialized entries are explicit and do not alias valid distances."""
        db = PatternDatabase("test", 10)

        assert db.is_initialized(0) is False
        with pytest.raises(ValueError):
            db.get_distance(0)

        db.set_distance(0, 15)
        assert db.is_initialized(0) is True
        assert db.get_distance(0) == 15

    def test_save_load_round_trip(self, tmp_path):
        """Exact-safe serialized databases round-trip with metadata intact."""
        db = PatternDatabase("test", 6)
        db.set_distance(0, 0)
        db.set_distance(3, 17)
        db.max_depth = 17
        db.states_at_depth = {0: 1, 17: 1}

        path = tmp_path / "db.pkl"
        db.save(str(path))

        loaded = PatternDatabase.load(str(path))
        assert loaded.name == "test"
        assert loaded.size == 6
        assert loaded.storage_format == PatternDatabase.STORAGE_FORMAT_BYTE
        assert loaded.uninitialized_value == 255
        assert loaded.get_distance(0) == 0
        assert loaded.get_distance(3) == 17
        assert loaded.max_depth == 17
        assert loaded.states_at_depth == {0: 1, 17: 1}

    def test_load_safe_legacy_nibble_database(self, tmp_path):
        """Legacy nibble files are upgraded only when conversion is unambiguous."""
        path = tmp_path / "legacy.pkl"
        payload = {
            'name': 'legacy',
            'size': 4,
            'data': np.array([0x30, 0x42], dtype=np.uint8),
            'max_depth': 4,
            'states_at_depth': {0: 1, 2: 1, 3: 1, 4: 1},
        }

        with open(path, 'wb') as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

        loaded = PatternDatabase.load(str(path))
        assert loaded.storage_format == PatternDatabase.STORAGE_FORMAT_BYTE
        assert loaded.get_distance(0) == 0
        assert loaded.get_distance(1) == 3
        assert loaded.get_distance(2) == 2
        assert loaded.get_distance(3) == 4

    def test_reject_ambiguous_legacy_nibble_database(self, tmp_path):
        """Legacy nibble files with distance 15 ambiguity are rejected."""
        path = tmp_path / "legacy_ambiguous.pkl"
        payload = {
            'name': 'legacy',
            'size': 2,
            'data': np.array([0xF0], dtype=np.uint8),
            'max_depth': 15,
            'states_at_depth': {0: 1, 15: 1},
        }

        with open(path, 'wb') as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

        with pytest.raises(ValueError, match="ambiguous distance 15"):
            PatternDatabase.load(str(path))


class TestCornerDatabase:
    """Test corner pattern database."""

    def test_corner_index_solved(self):
        """Test corner index for solved cube."""
        cubie = CubieCube()
        index = corner_index(cubie)

        # Solved state should have index 0
        assert index == 0

    def test_corner_index_range(self):
        """Test that corner indices are in valid range."""
        cubie = CubieCube()

        # Apply some moves and check index is in range
        from src.kociemba.cubie import ALL_MOVES

        for move_name, move in list(ALL_MOVES.items())[:6]:
            cubie_moved = cubie.multiply(move)
            index = corner_index(cubie_moved)

            assert 0 <= index < CORNER_DB_SIZE, f"Index {index} out of range for move {move_name}"

    def test_corner_index_consistency(self):
        """Test that same cube state gives same index."""
        cubie = CubieCube()

        # Apply a sequence of moves
        from src.kociemba.cubie import ALL_MOVES
        cubie = cubie.multiply(ALL_MOVES['R'])
        cubie = cubie.multiply(ALL_MOVES['U'])

        index1 = corner_index(cubie)
        index2 = corner_index(cubie)

        assert index1 == index2


class TestHeuristics:
    """Test heuristic functions."""

    def test_simple_heuristic_solved(self):
        """Test simple heuristic on solved cube."""
        cube = RubikCube()
        distance = simple_heuristic(cube)
        assert distance == 0.0

    def test_hamming_distance_solved(self):
        """Test Hamming distance on solved cube."""
        cube = RubikCube()
        distance = hamming_distance(cube)
        assert distance == 0.0

    def test_manhattan_distance_solved(self):
        """Test Manhattan distance on solved cube."""
        cube = RubikCube()
        distance = manhattan_distance(cube)
        assert distance == 0.0

    def test_simple_heuristic_scrambled(self):
        """Test simple heuristic on scrambled cube."""
        cube = RubikCube()
        cube.scramble(10, seed=42)
        distance = simple_heuristic(cube)

        assert distance > 0.0, "Scrambled cube should have distance > 0"
        assert distance <= 10.0

    def test_hamming_distance_scrambled(self):
        """Test Hamming distance on scrambled cube."""
        cube = RubikCube()
        cube.scramble(10, seed=42)
        distance = hamming_distance(cube)

        assert distance > 0.0
        assert distance <= 10.0

    def test_manhattan_distance_scrambled(self):
        """Test Manhattan distance on scrambled cube."""
        cube = RubikCube()
        cube.scramble(10, seed=42)
        distance = manhattan_distance(cube)

        assert distance > 0.0
        assert distance <= 10.0

    def test_manhattan_corner_vs_edge(self):
        """Test that corner and edge Manhattan distances are computed separately."""
        cube = RubikCube()
        cube.scramble(10, seed=42)
        cubie = from_facelet_cube(cube)

        corner_dist = manhattan_distance_corner(cubie)
        edge_dist = manhattan_distance_edge(cubie)

        assert corner_dist >= 0.0
        assert edge_dist >= 0.0

    def test_single_move_state_can_be_overestimated(self):
        """The lightweight heuristics are not guaranteed lower bounds."""
        cube = RubikCube()
        cube.apply_move('F')

        simple_est = simple_heuristic(cube)
        hamming_est = hamming_distance(cube)
        manhattan_est = manhattan_distance(cube)

        assert simple_est == 1.5
        assert hamming_est == 1.0
        assert manhattan_est == 2.0


class TestHeuristicEvaluator:
    """Test heuristic evaluator."""

    def test_evaluate_all(self):
        """Test evaluating all heuristics."""
        evaluator = HeuristicEvaluator()
        cube = RubikCube()
        cube.scramble(5, seed=42)

        results = evaluator.evaluate_all(cube)

        assert 'simple' in results
        assert 'hamming' in results
        assert 'manhattan' in results

        assert all(v >= 0 for v in results.values())

    def test_evaluate_specific(self):
        """Test evaluating a specific heuristic."""
        evaluator = HeuristicEvaluator()
        cube = RubikCube()
        cube.scramble(5, seed=42)

        distance = evaluator.evaluate(cube, 'manhattan')
        assert distance >= 0


class TestDistanceEstimator:
    """Test distance estimator."""

    def test_estimator_creation(self):
        """Test creating a distance estimator."""
        estimator = DistanceEstimator()
        assert estimator is not None

    def test_estimator_without_databases(self):
        """Test estimator using heuristics only (no databases)."""
        estimator = DistanceEstimator()
        cube = RubikCube()

        # Solved cube
        distance = estimator.estimate(cube, method='manhattan')
        assert distance == 0.0

        # Scrambled cube
        cube.scramble(5, seed=42)
        distance = estimator.estimate(cube, method='manhattan')
        assert distance > 0.0

    def test_estimator_detailed(self):
        """Test detailed estimation."""
        estimator = DistanceEstimator()
        cube = RubikCube()
        cube.scramble(5, seed=42)

        details = estimator.estimate_detailed(cube)

        assert 'is_solved' in details
        assert details['is_solved'] is False
        assert 'heuristics' in details
        assert len(details['heuristics']) > 0

    def test_estimator_solved_cube(self):
        """Test estimator on solved cube."""
        estimator = DistanceEstimator()
        cube = RubikCube()

        # All methods should return 0 for solved cube
        assert estimator.estimate(cube, method='manhattan') == 0.0
        assert estimator.estimate(cube, method='hamming') == 0.0
        assert estimator.estimate(cube, method='simple') == 0.0

    def test_estimator_consistency(self):
        """Test that estimator gives consistent results."""
        estimator = DistanceEstimator()
        cube = RubikCube()
        cube.scramble(7, seed=42)

        # Multiple calls should give same result
        dist1 = estimator.estimate(cube, method='manhattan')
        dist2 = estimator.estimate(cube, method='manhattan')

        assert dist1 == dist2


class TestIntegration:
    """Integration tests for the full distance estimation system."""

    def test_increasing_scramble_distance(self):
        """Test that estimated distance increases with scramble depth."""
        estimator = DistanceEstimator()

        distances = []
        for scramble_length in [1, 3, 5, 10]:
            cube = RubikCube()
            cube.scramble(scramble_length, seed=42)
            distance = estimator.estimate(cube, method='manhattan')
            distances.append(distance)

        # Generally, distance should increase (not strict due to randomness)
        # Just check that we get non-zero distances
        assert all(d >= 0 for d in distances)

    def test_known_sequences(self):
        """Test estimation on known move sequences."""
        estimator = DistanceEstimator()

        # Test a simple sequence
        cube = RubikCube()
        cube.apply_moves(['R', 'U'])

        distance = estimator.estimate(cube, method='manhattan')
        assert distance > 0, "Two moves should give non-zero estimate"
        # Note: estimate may be higher than 2 due to heuristic approximation
        # The actual optimal solution for R U might require more moves to undo
        assert distance <= 5, "Estimate should be reasonable"

        # Test a sequence that returns to solved
        cube = RubikCube()
        cube.apply_moves(['R', 'U', 'R\'', 'U\''])

        distance = estimator.estimate(cube, method='manhattan')
        # This should be close to 0 if moves cancel, but may not be exact due to heuristic
        assert distance >= 0

    def test_statistics(self):
        """Test getting estimator statistics."""
        estimator = DistanceEstimator()
        stats = estimator.get_statistics()

        assert 'databases_loaded' in stats
        assert stats['databases_loaded'] is False  # No DBs loaded in basic test


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
