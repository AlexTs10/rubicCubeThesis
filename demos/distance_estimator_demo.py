"""
Distance Estimator Demo

This script demonstrates the distance estimation capabilities including:
1. Heuristic-based estimation (Manhattan, Hamming, simple)
2. Pattern database estimation (if databases are available)
3. Accuracy comparison on test positions
4. Visualization of estimation quality

Usage:
    python demos/distance_estimator_demo.py [--generate-dbs]

Options:
    --generate-dbs    Generate pattern databases (takes significant time)
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cube.rubik_cube import RubikCube
from src.korf import create_estimator, HeuristicEvaluator
from src.korf.validation import create_test_dataset, AccuracyEvaluator


def demo_basic_estimation():
    """Demonstrate basic distance estimation."""
    print("=" * 80)
    print("DEMO 1: Basic Distance Estimation")
    print("=" * 80)

    # Create estimator (without pattern databases for now)
    estimator = create_estimator(load_databases=False)

    # Test on solved cube
    print("\n1. Solved Cube:")
    cube = RubikCube()
    details = estimator.estimate_detailed(cube)
    print(f"   Manhattan: {details['heuristics']['manhattan']:.2f}")
    print(f"   Hamming:   {details['heuristics']['hamming']:.2f}")
    print(f"   Simple:    {details['heuristics']['simple']:.2f}")

    # Test on scrambled cubes at different depths
    print("\n2. Scrambled Cubes:")
    for scramble_length in [5, 10, 15, 20]:
        cube = RubikCube()
        cube.scramble(scramble_length, seed=42 + scramble_length)

        details = estimator.estimate_detailed(cube)
        print(f"\n   Scramble {scramble_length} moves:")
        print(f"     Manhattan: {details['heuristics']['manhattan']:.2f}")
        print(f"     Hamming:   {details['heuristics']['hamming']:.2f}")
        print(f"     Simple:    {details['heuristics']['simple']:.2f}")


def demo_heuristic_comparison():
    """Compare different heuristics."""
    print("\n" + "=" * 80)
    print("DEMO 2: Heuristic Comparison on Known Sequences")
    print("=" * 80)

    evaluator = HeuristicEvaluator()

    # Test sequences with known lengths
    sequences = [
        (['R', 'U', 'R\'', 'U\''], "RU commutator (4 moves)"),
        (['R', 'U'] * 3, "R U repeated 3 times (6 moves)"),
        (['F', 'R', 'U', 'R\'', 'U\'', 'F\''], "F sexy F' (6 moves)"),
    ]

    for moves, description in sequences:
        cube = RubikCube()
        cube.apply_moves(moves)

        print(f"\n{description}:")
        print(f"  Actual moves: {len(moves)}")

        results = evaluator.evaluate_all(cube)
        for name, estimate in sorted(results.items()):
            error = abs(estimate - len(moves))
            print(f"  {name:10s}: {estimate:.2f} (error: {error:.2f})")


def demo_accuracy_evaluation():
    """Evaluate accuracy on test dataset."""
    print("\n" + "=" * 80)
    print("DEMO 3: Accuracy Evaluation on Test Dataset")
    print("=" * 80)

    # Create test dataset
    print("\nCreating test dataset...")
    dataset = create_test_dataset(seed=42)
    print(f"Dataset size: {len(dataset)} positions")

    # Create estimator
    estimator = create_estimator(load_databases=False)

    # Evaluate accuracy
    print("\nEvaluating accuracy...")
    evaluator = AccuracyEvaluator(estimator)
    evaluator.compare_methods(dataset)


def demo_pattern_databases():
    """Demonstrate pattern database usage (if available)."""
    print("\n" + "=" * 80)
    print("DEMO 4: Pattern Database Estimation")
    print("=" * 80)

    try:
        # Try to load existing databases
        print("\nAttempting to load pattern databases...")
        estimator = create_estimator(load_databases=True, generate_if_missing=False)

        if not estimator.use_pattern_dbs:
            print("Pattern databases not available.")
            print("To generate them, run with --generate-dbs flag.")
            print("Warning: Generation takes significant time and memory!")
            return

        print("Pattern databases loaded successfully!")

        # Test on various cubes
        print("\nTesting pattern database estimates:")
        for scramble_length in [5, 10, 15]:
            cube = RubikCube()
            cube.scramble(scramble_length, seed=42 + scramble_length)

            estimator.compare_methods(cube, actual_distance=None)
            print()

    except Exception as e:
        print(f"Pattern databases not available: {e}")
        print("To generate them, run with --generate-dbs flag.")


def demo_statistics():
    """Show statistics about the estimator."""
    print("\n" + "=" * 80)
    print("DEMO 5: Distance Estimator Statistics")
    print("=" * 80)

    # Create estimator without databases
    estimator = create_estimator(load_databases=False)

    stats = estimator.get_statistics()
    print(f"\nDatabases loaded: {stats['databases_loaded']}")

    if stats['databases_loaded']:
        if stats['corner_db']:
            print("\nCorner Database:")
            for key, value in stats['corner_db'].items():
                print(f"  {key}: {value}")

        if stats['edge1_db']:
            print("\nEdge1 Database:")
            for key, value in stats['edge1_db'].items():
                print(f"  {key}: {value}")

        if stats['edge2_db']:
            print("\nEdge2 Database:")
            for key, value in stats['edge2_db'].items():
                print(f"  {key}: {value}")


def generate_pattern_databases():
    """Generate pattern databases (warning: takes time!)."""
    print("\n" + "=" * 80)
    print("GENERATING PATTERN DATABASES")
    print("=" * 80)
    print("\nWARNING: This will take significant time and memory!")
    print("Corner DB: ~88M states, ~44MB")
    print("Edge DBs: ~645K states each, ~0.3MB each")
    print()

    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return

    # Create estimator and generate databases
    estimator = create_estimator(load_databases=True, generate_if_missing=True)

    print("\nPattern databases generated and saved!")
    print("You can now use them for more accurate distance estimation.")


def main():
    """Run all demos."""
    parser = argparse.ArgumentParser(description='Distance Estimator Demo')
    parser.add_argument('--generate-dbs', action='store_true',
                        help='Generate pattern databases (takes significant time)')

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("RUBIK'S CUBE DISTANCE ESTIMATOR DEMONSTRATION")
    print("=" * 80)

    # Run demos
    demo_basic_estimation()
    demo_heuristic_comparison()
    demo_accuracy_evaluation()
    demo_statistics()

    # Generate or use pattern databases
    if args.generate_dbs:
        generate_pattern_databases()
    else:
        demo_pattern_databases()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nFor more information, see:")
    print("  - src/korf/distance_estimator.py")
    print("  - src/korf/heuristics.py")
    print("  - tests/unit/test_distance_estimator.py")
    print()


if __name__ == '__main__':
    main()
