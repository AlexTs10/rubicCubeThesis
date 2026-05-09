"""Tests for reproducible validation dataset generation and persistence."""

import pytest

from src.korf.validation import ValidationDataset, load_cube20_data


def _state_keys(dataset):
    return [cube.state_key() for cube, _distance in dataset]


def test_generate_random_scrambles_is_seed_reproducible():
    first = ValidationDataset()
    second = ValidationDataset()

    first.generate_random_scrambles([3, 4], count_per_distance=2, seed=123)
    second.generate_random_scrambles([3, 4], count_per_distance=2, seed=123)

    assert _state_keys(first) == _state_keys(second)
    assert [distance for _cube, distance in first] == [3, 3, 4, 4]


def test_validation_dataset_save_load_round_trip(tmp_path):
    dataset = ValidationDataset()
    dataset.generate_random_scrambles([2], count_per_distance=2, seed=456)

    path = tmp_path / "validation.json"
    dataset.save_to_file(str(path))

    loaded = ValidationDataset()
    loaded.load_from_file(str(path))

    assert len(loaded) == len(dataset)
    assert _state_keys(loaded) == _state_keys(dataset)
    assert [distance for _cube, distance in loaded] == [2, 2]


def test_cube20_loader_fails_loudly_for_unsupported_format(tmp_path):
    cube20_file = tmp_path / "distance20.txt"
    cube20_file.write_text("placeholder unsupported cube20 payload\n")

    with pytest.raises(NotImplementedError):
        load_cube20_data(str(cube20_file))
