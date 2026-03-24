"""Unit tests for the specialized corner pattern database generator."""

import pytest

from src.korf.corner_database import CornerPatternDatabase, create_corner_database


def test_corner_database_partial_generation_is_marked_incomplete(tmp_path):
    save_path = tmp_path / "corner_partial.pkl"
    cache_dir = tmp_path / "corner_cache"

    corner_db = create_corner_database(
        load_if_exists=False,
        save_path=str(save_path),
        verbose=False,
        max_depth=1,
        frontier_chunk_size=64,
        move_cache_dir=str(cache_dir),
    )

    assert corner_db.states_at_depth[0] == 1
    assert corner_db.states_at_depth[1] == 18
    assert corner_db.initialized_count() == 19
    assert corner_db.is_complete() is False


def test_loading_incomplete_corner_database_can_be_rejected(tmp_path):
    save_path = tmp_path / "corner_partial.pkl"
    cache_dir = tmp_path / "corner_cache"

    create_corner_database(
        load_if_exists=False,
        save_path=str(save_path),
        verbose=False,
        max_depth=1,
        frontier_chunk_size=64,
        move_cache_dir=str(cache_dir),
    )

    with pytest.raises(ValueError, match="incomplete"):
        create_corner_database(
            load_if_exists=True,
            save_path=str(save_path),
            generate_if_missing=False,
            require_complete=True,
            verbose=False,
        )


def test_loading_incomplete_corner_database_is_allowed_when_requested(tmp_path):
    save_path = tmp_path / "corner_partial.pkl"
    cache_dir = tmp_path / "corner_cache"

    create_corner_database(
        load_if_exists=False,
        save_path=str(save_path),
        verbose=False,
        max_depth=1,
        frontier_chunk_size=64,
        move_cache_dir=str(cache_dir),
    )

    loaded = create_corner_database(
        load_if_exists=True,
        save_path=str(save_path),
        generate_if_missing=False,
        require_complete=False,
        verbose=False,
    )

    assert isinstance(loaded, CornerPatternDatabase)
    assert loaded.is_complete() is False
    assert loaded.initialized_count() == 19
