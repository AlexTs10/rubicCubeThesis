"""Tests for Thistlethwaite pattern-table cache validation."""

import pickle

import numpy as np
import pytest

from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.tables import PatternDatabase


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
