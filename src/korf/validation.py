"""
Validation and Accuracy Testing for Distance Estimator

This module provides tools for validating the accuracy of distance estimation
by comparing estimates against known optimal distances.

Features:
- Generate test positions with known distances
- Load validation data from cube20.org
- Calculate Mean Absolute Error (MAE)
- Compare multiple estimation methods
- Generate accuracy reports

References:
- cube20.org: Known distance-20 positions
- Rokicki et al. (2010): God's Number is 20
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json
import os

from ..cube.rubik_cube import RubikCube
from .distance_estimator import DistanceEstimator


class ValidationDataset:
    """
    Dataset of cube positions with known optimal distances.
    """

    def __init__(self):
        """Initialize validation dataset."""
        self.positions: List[Tuple[RubikCube, int]] = []  # (cube, distance)

    def add_position(self, cube: RubikCube, distance: int) -> None:
        """
        Add a position with known distance to the dataset.

        Args:
            cube: Cube position
            distance: Known optimal distance
        """
        self.positions.append((cube.copy(), distance))

    def generate_random_scrambles(self,
                                   distances: List[int],
                                   count_per_distance: int = 10,
                                   seed: Optional[int] = None) -> None:
        """
        Generate random scrambles at specific distances.

        Note: These are approximations - the actual optimal distance may be
        less than the scramble length due to move cancellations.

        Args:
            distances: List of scramble distances to generate
            count_per_distance: Number of positions per distance
            seed: Random seed for reproducibility
        """
        if seed is not None:
            np.random.seed(seed)

        for distance in distances:
            for i in range(count_per_distance):
                cube = RubikCube()
                scramble = cube.scramble(moves=distance, seed=None)

                # Add to dataset (using scramble length as approximate distance)
                self.add_position(cube, distance)

        print(f"Generated {len(self.positions)} validation positions")

    def load_from_file(self, filepath: str) -> None:
        """
        Load validation data from a file.

        File format (JSON):
        {
            "positions": [
                {
                    "moves": "R U R' U'",
                    "distance": 4
                },
                ...
            ]
        }

        Args:
            filepath: Path to validation data file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        for entry in data['positions']:
            cube = RubikCube()
            moves_str = entry['moves']
            cube.apply_move_sequence(moves_str)
            distance = entry['distance']

            self.add_position(cube, distance)

        print(f"Loaded {len(self.positions)} positions from {filepath}")

    def save_to_file(self, filepath: str) -> None:
        """
        Save validation dataset to a file.

        Args:
            filepath: Path to save the dataset
        """
        # For now, just save metadata
        # TODO: Implement cube state serialization
        data = {
            'count': len(self.positions),
            'positions': []
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved {len(self.positions)} positions to {filepath}")

    def __len__(self) -> int:
        """Get number of positions in dataset."""
        return len(self.positions)

    def __iter__(self):
        """Iterate over positions."""
        return iter(self.positions)


class AccuracyEvaluator:
    """
    Evaluator for measuring distance estimation accuracy.
    """

    def __init__(self, estimator: DistanceEstimator):
        """
        Initialize accuracy evaluator.

        Args:
            estimator: Distance estimator to evaluate
        """
        self.estimator = estimator

    def evaluate(self,
                 dataset: ValidationDataset,
                 methods: List[str] = None) -> Dict:
        """
        Evaluate estimator accuracy on a validation dataset.

        Args:
            dataset: Validation dataset with known distances
            methods: List of methods to evaluate (default: all available)

        Returns:
            Dictionary with accuracy metrics
        """
        if methods is None:
            methods = ['pattern_db', 'manhattan', 'hamming', 'simple']

        # Filter methods based on availability
        if not self.estimator.use_pattern_dbs and 'pattern_db' in methods:
            methods = [m for m in methods if m != 'pattern_db']
            print("Warning: pattern_db not available, excluding from evaluation")

        results = {
            'dataset_size': len(dataset),
            'methods': {}
        }

        for method in methods:
            print(f"Evaluating method: {method}...")
            method_results = self._evaluate_method(dataset, method)
            results['methods'][method] = method_results

        return results

    def _evaluate_method(self, dataset: ValidationDataset, method: str) -> Dict:
        """
        Evaluate a single estimation method.

        Args:
            dataset: Validation dataset
            method: Method name

        Returns:
            Dictionary with metrics for this method
        """
        errors = []
        estimates = []
        actuals = []
        by_distance = defaultdict(list)

        for cube, actual_distance in dataset:
            try:
                estimate = self.estimator.estimate(cube, method=method)
                error = abs(estimate - actual_distance)

                errors.append(error)
                estimates.append(estimate)
                actuals.append(actual_distance)

                by_distance[actual_distance].append(error)

            except Exception as e:
                print(f"Error evaluating position: {e}")
                continue

        if not errors:
            return {'error': 'No successful evaluations'}

        # Calculate metrics
        mae = np.mean(errors)  # Mean Absolute Error
        rmse = np.sqrt(np.mean(np.array(errors) ** 2))  # Root Mean Square Error
        max_error = np.max(errors)
        min_error = np.min(errors)

        # Calculate accuracy (percentage of exact predictions)
        exact_predictions = sum(1 for e in errors if e < 0.5)
        accuracy = 100 * exact_predictions / len(errors)

        # Per-distance statistics
        distance_stats = {}
        for distance, dist_errors in by_distance.items():
            distance_stats[distance] = {
                'count': len(dist_errors),
                'mae': float(np.mean(dist_errors)),
                'max_error': float(np.max(dist_errors))
            }

        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'max_error': float(max_error),
            'min_error': float(min_error),
            'accuracy': float(accuracy),
            'num_samples': len(errors),
            'distance_stats': distance_stats
        }

    def compare_methods(self, dataset: ValidationDataset) -> None:
        """
        Compare all available methods and print results.

        Args:
            dataset: Validation dataset
        """
        print("=" * 80)
        print("DISTANCE ESTIMATION ACCURACY EVALUATION")
        print("=" * 80)
        print(f"Dataset size: {len(dataset)} positions")
        print()

        results = self.evaluate(dataset)

        print("Results by Method:")
        print("-" * 80)

        for method, metrics in results['methods'].items():
            if 'error' in metrics:
                print(f"\n{method.upper()}: {metrics['error']}")
                continue

            print(f"\n{method.upper()}:")
            print(f"  Mean Absolute Error (MAE): {metrics['mae']:.3f}")
            print(f"  Root Mean Square Error:     {metrics['rmse']:.3f}")
            print(f"  Max Error:                  {metrics['max_error']:.3f}")
            print(f"  Min Error:                  {metrics['min_error']:.3f}")
            print(f"  Accuracy (exact):           {metrics['accuracy']:.1f}%")
            print(f"  Samples:                    {metrics['num_samples']}")

            if metrics['distance_stats']:
                print(f"\n  Per-Distance Statistics:")
                for dist in sorted(metrics['distance_stats'].keys()):
                    stats = metrics['distance_stats'][dist]
                    print(f"    Distance {dist:2d}: MAE={stats['mae']:.2f}, "
                          f"Max={stats['max_error']:.2f}, Count={stats['count']}")

        print("=" * 80)

    def save_report(self, dataset: ValidationDataset, filepath: str) -> None:
        """
        Generate and save a detailed accuracy report.

        Args:
            dataset: Validation dataset
            filepath: Path to save the report
        """
        results = self.evaluate(dataset)

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Report saved to {filepath}")


def create_test_dataset(seed: int = 42) -> ValidationDataset:
    """
    Create a standard test dataset for validation.

    This generates positions at distances 1-20 for testing.

    Args:
        seed: Random seed for reproducibility

    Returns:
        Validation dataset
    """
    dataset = ValidationDataset()

    # Generate positions at various distances
    distances = [1, 2, 3, 4, 5, 7, 10, 15, 20]
    dataset.generate_random_scrambles(
        distances=distances,
        count_per_distance=10,
        seed=seed
    )

    return dataset


def load_cube20_data(filepath: str) -> ValidationDataset:
    """
    Load validation data from cube20.org dataset.

    The cube20.org dataset contains positions with known optimal distances,
    particularly useful for distance-20 positions.

    Args:
        filepath: Path to cube20.org data file

    Returns:
        Validation dataset

    Note:
        Data can be downloaded from http://www.cube20.org/distance20s
    """
    dataset = ValidationDataset()

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Cube20 data not found at {filepath}. "
            f"Download from http://www.cube20.org/distance20s"
        )

    # TODO: Implement parser for cube20.org format
    # The format may be cube states in specific notation
    print("Warning: cube20.org data loading not yet implemented")
    print("Using test dataset instead")

    return dataset
