"""Tests for reproducible validation dataset generation and persistence."""

from src.korf import validation as validation_module
from src.korf.validation import ValidationDataset


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


def test_cube20_loader_is_not_public_api():
    assert not hasattr(validation_module, "load_cube20_data")
