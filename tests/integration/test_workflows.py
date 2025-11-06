"""
Integration tests for complete workflows.

These tests verify that different components work together correctly.
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

from src.cube import (
    RubikCube,
    inverse_sequence, parse_move_sequence, simplify_moves,
    visualize_2d, visualize_3d
)
import matplotlib.pyplot as plt


class TestScrambleAndSolve:
    """Test scrambling and solving workflows."""

    def test_scramble_and_reverse(self):
        """Test that scramble can be reversed."""
        cube = RubikCube()
        scramble_moves = cube.scramble(moves=20, seed=42)

        # Apply inverse
        inverse_moves = inverse_sequence(scramble_moves)
        cube.apply_moves(inverse_moves)

        assert cube.is_solved()

    def test_multiple_scrambles_reversible(self):
        """Test multiple scrambles can be reversed."""
        for seed in range(10):
            cube = RubikCube()
            moves = cube.scramble(moves=15, seed=seed)

            inverse = inverse_sequence(moves)
            cube.apply_moves(inverse)

            assert cube.is_solved(), f"Failed for seed {seed}"


class TestMoveSequenceWorkflows:
    """Test complete move sequence workflows."""

    def test_parse_apply_format_cycle(self):
        """Test parsing, applying, and formatting moves."""
        original_sequence = "R U R' U' F' U' F U"

        # Parse
        moves = parse_move_sequence(original_sequence)

        # Apply to cube
        cube = RubikCube()
        cube.apply_moves(moves)

        # Should not be solved
        assert not cube.is_solved()

        # Apply inverse
        inverse = inverse_sequence(moves)
        cube.apply_moves(inverse)

        # Should be solved
        assert cube.is_solved()

    def test_simplify_and_apply(self):
        """Test that simplified moves give same result."""
        # Complex sequence that can be simplified
        original = ['R', 'R', 'R', 'U', 'U']
        simplified = simplify_moves(original)

        cube1 = RubikCube()
        cube1.apply_moves(original)

        cube2 = RubikCube()
        cube2.apply_moves(simplified)

        assert cube1 == cube2


class TestAlgorithmCombinations:
    """Test combinations of known algorithms."""

    def test_combine_multiple_algorithms(self):
        """Test applying multiple algorithms in sequence."""
        cube = RubikCube()

        algorithms = [
            "R U R' U'",           # Sexy move
            "R' F R F'",           # Sledgehammer
            "F R U R' U' F'",      # F sexy F'
        ]

        for algo in algorithms:
            cube.apply_move_sequence(algo)

        # Apply all inverses in reverse order
        for algo in reversed(algorithms):
            inverse = inverse_sequence(parse_move_sequence(algo))
            cube.apply_moves(inverse)

        assert cube.is_solved()


class TestVisualizationIntegration:
    """Test visualization components integration."""

    def test_visualize_2d_basic(self):
        """Test that 2D visualization runs without errors."""
        cube = RubikCube()

        try:
            fig = visualize_2d(cube, show=False)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"2D visualization failed: {e}")

    def test_visualize_2d_scrambled(self):
        """Test 2D visualization of scrambled cube."""
        cube = RubikCube()
        cube.scramble(moves=10, seed=42)

        try:
            fig = visualize_2d(cube, show=False)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"2D visualization of scrambled cube failed: {e}")

    def test_visualize_3d_basic(self):
        """Test that 3D visualization runs without errors."""
        cube = RubikCube()

        try:
            fig = visualize_3d(cube, show=False)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"3D visualization failed: {e}")

    def test_visualize_3d_scrambled(self):
        """Test 3D visualization of scrambled cube."""
        cube = RubikCube()
        cube.scramble(moves=10, seed=42)

        try:
            fig = visualize_3d(cube, show=False)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"3D visualization of scrambled cube failed: {e}")


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""

    def test_full_workflow(self):
        """Test a complete workflow from creation to visualization."""
        # Create cube
        cube = RubikCube()
        assert cube.is_solved()

        # Apply some moves
        cube.apply_move_sequence("R U R' U' R' F R F'")
        assert not cube.is_solved()

        # Visualize (should not raise errors)
        fig1 = visualize_2d(cube, show=False)
        plt.close(fig1)

        fig2 = visualize_3d(cube, show=False)
        plt.close(fig2)

        # Apply inverse to solve
        moves = parse_move_sequence("R U R' U' R' F R F'")
        inverse = inverse_sequence(moves)
        cube.apply_moves(inverse)

        assert cube.is_solved()

    def test_reproducible_results(self):
        """Test that same seed gives reproducible results."""
        results = []

        for _ in range(3):
            cube = RubikCube()
            cube.scramble(moves=20, seed=12345)
            results.append(cube.state.copy())

        # All results should be identical
        for i in range(1, len(results)):
            assert np.array_equal(results[0], results[i])


class TestPerformanceBasics:
    """Basic performance tests."""

    def test_many_moves_performance(self):
        """Test that applying many moves is reasonably fast."""
        import time

        cube = RubikCube()
        start = time.time()

        # Apply 1000 moves
        for _ in range(1000):
            cube.apply_move('R')

        elapsed = time.time() - start

        # Should complete in reasonable time (less than 1 second)
        assert elapsed < 1.0, f"1000 moves took {elapsed} seconds"

    def test_large_scramble_performance(self):
        """Test that large scrambles are reasonably fast."""
        import time

        cube = RubikCube()
        start = time.time()

        cube.scramble(moves=1000, seed=42)

        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 2.0, f"1000-move scramble took {elapsed} seconds"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
