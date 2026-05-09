"""Tests for Thistlethwaite pattern-table cache validation."""

import pickle

import numpy as np
import pytest

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.tables import PatternDatabase, ThistlethwaitePatternDatabases


def _coord(_cube: RubikCube) -> int:
    return 0


def test_pattern_database_rejects_wrong_shape_cache(tmp_path):
    db = PatternDatabase(
        name="tiny",
        size=4,
        get_coord=_coord,
        moves=["U"],
        cache_dir=str(tmp_path),
    )
    with open(db.cache_file, "wb") as fh:
        pickle.dump(np.zeros(3, dtype=np.uint8), fh)

    with pytest.raises(ValueError, match="expected"):
        db.load_or_generate(max_depth=0)


def test_pattern_database_schema_cache_round_trip(tmp_path):
    db = PatternDatabase(
        name="tiny",
        size=4,
        get_coord=_coord,
        moves=["U"],
        cache_dir=str(tmp_path),
    )
    db.table[0] = 0
    db.table[1] = 1
    db.save()

    loaded = PatternDatabase(
        name="tiny",
        size=4,
        get_coord=_coord,
        moves=["U"],
        cache_dir=str(tmp_path),
    )
    loaded.load_or_generate(max_depth=0)

    assert loaded.table.tolist() == [0, 1, 255, 255]


def test_phase3_exact_cache_rejects_invalid_payload(tmp_path):
    """Exact phase-3 caches must contain a validated solved-state distance map."""
    pdb = ThistlethwaitePatternDatabases(cache_dir=str(tmp_path))
    cache_file = tmp_path / "phase3_exact_g3_v4.pkl"
    with open(cache_file, "wb") as fh:
        pickle.dump({"distances": {1: 0}}, fh)

    with pytest.raises(ValueError, match="solved-state distance 0"):
        pdb._load_or_generate_phase3_exact(["U2"])


def test_goal_distance_cache_rejects_nonzero_goal(tmp_path):
    """Goal-distance tables must preserve distance 0 for every projected goal coordinate."""
    pdb = ThistlethwaitePatternDatabases(cache_dir=str(tmp_path))
    cache_file = tmp_path / "tiny_goal.pkl"
    with open(cache_file, "wb") as fh:
        pickle.dump(np.array([1, 255, 255, 255], dtype=np.uint8), fh)

    with pytest.raises(ValueError, match="goal coordinate 0"):
        pdb._load_or_generate_goal_distance_table(
            name="tiny_goal",
            size=4,
            move_table=np.array([[0], [1], [2], [3]], dtype=np.int32),
            goal_coords={0},
        )
