"""
Unit Tests for A* and IDA* Solvers

Tests cover:
1. Basic solving functionality
2. Heuristic integration
3. Move pruning logic
4. Performance metrics collection
5. Timeout and memory limit handling
"""

import pytest
import time
from src.cube.rubik_cube import RubikCube
from src.korf.a_star import AStarSolver, IDAStarSolver, SearchNode
from src.korf.heuristics import manhattan_distance, hamming_distance
from src.korf.composite_heuristic import create_heuristic


class TestSearchNode:
    """Test SearchNode data structure."""

    def test_node_creation(self):
        """Test creating a search node."""
        cube = RubikCube()
        node = SearchNode(
            f_value=5.0,
            g_value=2,
            h_value=3.0,
            cube_state=cube,
            move_sequence=['U', 'R'],
            parent_hash=None
        )

        assert node.f_value == 5.0
        assert node.g_value == 2
        assert node.h_value == 3.0
        assert len(node.move_sequence) == 2

    def test_node_ordering(self):
        """Test that nodes are ordered by f_value."""
        cube = RubikCube()

        node1 = SearchNode(5.0, 2, 3.0, cube, [])
        node2 = SearchNode(3.0, 1, 2.0, cube, [])
        node3 = SearchNode(7.0, 3, 4.0, cube, [])

        assert node2 < node1 < node3

    def test_node_hashing(self):
        """Test that nodes can be hashed based on cube state."""
        cube1 = RubikCube()
        cube2 = RubikCube()
        cube3 = RubikCube()
        cube3.apply_move('U')

        node1 = SearchNode(5.0, 2, 3.0, cube1, [])
        node2 = SearchNode(4.0, 1, 3.0, cube2, [])  # Same state, different values
        node3 = SearchNode(5.0, 2, 3.0, cube3, [])

        # Same cube state should hash the same
        assert hash(node1) == hash(node2)
        # Different cube state should hash differently
        assert hash(node1) != hash(node3)


class TestAStarSolver:
    """Test A* solver implementation."""

    def test_solve_already_solved(self):
        """Test solving an already solved cube."""
        cube = RubikCube()
        solver = AStarSolver(heuristic=manhattan_distance, max_depth=10)

        solution = solver.solve(cube)

        assert solution is not None
        assert len(solution) == 0
        assert cube.is_solved()

    def test_solve_single_move(self):
        """Test solving with a single move scramble."""
        cube = RubikCube()
        cube.apply_move('U')

        solver = AStarSolver(heuristic=manhattan_distance, max_depth=5)
        solution = solver.solve(cube)

        assert solution is not None
        assert len(solution) > 0
        assert len(solution) <= 2  # Should be optimal (1-2 moves)

        # Verify solution works
        test_cube = RubikCube()
        test_cube.apply_move('U')
        for move in solution:
            test_cube.apply_move(move)
        assert test_cube.is_solved()

    def test_solve_short_scramble(self):
        """Test solving a short scramble."""
        cube = RubikCube()
        scramble = ['U', 'R', 'F']
        for move in scramble:
            cube.apply_move(move)

        solver = AStarSolver(heuristic=manhattan_distance, max_depth=10, timeout=30.0)
        solution = solver.solve(cube)

        assert solution is not None
        assert len(solution) > 0

        # Verify solution
        test_cube = RubikCube()
        for move in scramble:
            test_cube.apply_move(move)
        for move in solution:
            test_cube.apply_move(move)
        assert test_cube.is_solved()

    def test_different_heuristics(self):
        """Test that different heuristics work correctly."""
        cube = RubikCube()
        cube.apply_move('U')
        cube.apply_move('R')

        # Test with Manhattan
        solver_manhattan = AStarSolver(heuristic=manhattan_distance, max_depth=8)
        solution_manhattan = solver_manhattan.solve(cube)

        # Test with Hamming
        solver_hamming = AStarSolver(heuristic=hamming_distance, max_depth=8)
        solution_hamming = solver_hamming.solve(cube)

        # Both should find solutions
        assert solution_manhattan is not None
        assert solution_hamming is not None

    def test_timeout_handling(self):
        """Test that timeout is respected."""
        cube = RubikCube()
        cube.scramble(moves=10)

        # Very short timeout
        solver = AStarSolver(heuristic=manhattan_distance, max_depth=20, timeout=0.1)

        start_time = time.time()
        solution = solver.solve(cube)
        elapsed_time = time.time() - start_time

        # Should timeout quickly
        assert elapsed_time < 1.0  # At most 1 second

    def test_statistics_collection(self):
        """Test that statistics are collected correctly."""
        cube = RubikCube()
        cube.apply_move('U')

        solver = AStarSolver(heuristic=manhattan_distance, max_depth=5)
        solution = solver.solve(cube)

        stats = solver.get_statistics()

        assert 'nodes_explored' in stats
        assert 'nodes_generated' in stats
        assert 'time_elapsed' in stats
        assert stats['nodes_explored'] > 0
        assert stats['nodes_generated'] >= stats['nodes_explored']

    def test_redundant_move_pruning(self):
        """Test that redundant moves are pruned."""
        cube = RubikCube()
        solver = AStarSolver(heuristic=manhattan_distance, max_depth=5)

        # Test same face
        assert solver._is_redundant_move('U', 'U\'') == True
        assert solver._is_redundant_move('U', 'U2') == True

        # Test opposite faces (non-canonical order)
        assert solver._is_redundant_move('D', 'U') == True
        assert solver._is_redundant_move('B', 'F') == True
        assert solver._is_redundant_move('R', 'L') == True

        # Test non-redundant
        assert solver._is_redundant_move('U', 'R') == False
        assert solver._is_redundant_move('F', 'U') == False


class TestIDAStarSolver:
    """Test IDA* solver implementation."""

    def test_solve_already_solved(self):
        """Test solving an already solved cube."""
        cube = RubikCube()
        solver = IDAStarSolver(heuristic=manhattan_distance, max_depth=10)

        solution = solver.solve(cube)

        assert solution is not None
        assert len(solution) == 0

    def test_solve_single_move(self):
        """Test solving with a single move scramble."""
        cube = RubikCube()
        cube.apply_move('U')

        solver = IDAStarSolver(heuristic=manhattan_distance, max_depth=5)
        solution = solver.solve(cube)

        assert solution is not None
        assert len(solution) > 0

        # Verify solution
        test_cube = RubikCube()
        test_cube.apply_move('U')
        for move in solution:
            test_cube.apply_move(move)
        assert test_cube.is_solved()

    def test_solve_short_scramble(self):
        """Test solving a short scramble."""
        cube = RubikCube()
        scramble = ['U', 'R', 'F']
        for move in scramble:
            cube.apply_move(move)

        solver = IDAStarSolver(heuristic=manhattan_distance, max_depth=10, timeout=30.0)
        solution = solver.solve(cube)

        assert solution is not None

        # Verify solution
        test_cube = RubikCube()
        for move in scramble:
            test_cube.apply_move(move)
        for move in solution:
            test_cube.apply_move(move)
        assert test_cube.is_solved()

    def test_iterative_deepening(self):
        """Test that IDA* uses iterative deepening."""
        cube = RubikCube()
        cube.apply_move('U')
        cube.apply_move('R')

        solver = IDAStarSolver(heuristic=manhattan_distance, max_depth=10)
        solution = solver.solve(cube)

        stats = solver.get_statistics()

        # IDA* should explore multiple nodes (iterative deepening)
        assert stats['nodes_explored'] > len(solution) if solution else 0

    def test_memory_efficiency(self):
        """Test that IDA* uses minimal memory."""
        cube = RubikCube()
        cube.scramble(moves=5)

        solver = IDAStarSolver(heuristic=manhattan_distance, max_depth=15, timeout=30.0)
        solution = solver.solve(cube)

        stats = solver.get_statistics()

        # IDA* should report minimal memory usage
        assert stats['estimated_memory_mb'] < 1.0  # Less than 1MB

    def test_timeout_handling(self):
        """Test that timeout is respected."""
        cube = RubikCube()
        cube.scramble(moves=10)

        # Very short timeout
        solver = IDAStarSolver(heuristic=manhattan_distance, max_depth=20, timeout=0.1)

        start_time = time.time()
        solution = solver.solve(cube)
        elapsed_time = time.time() - start_time

        # Should timeout quickly
        assert elapsed_time < 1.0


class TestSolverComparison:
    """Test comparison between A* and IDA*."""

    def test_both_solvers_find_same_length_solution(self):
        """Test that both solvers find optimal solutions."""
        cube = RubikCube()
        cube.apply_move('U')
        cube.apply_move('R')

        # A* solution
        a_star = AStarSolver(heuristic=manhattan_distance, max_depth=10)
        solution_a = a_star.solve(cube)

        # Reset cube
        cube = RubikCube()
        cube.apply_move('U')
        cube.apply_move('R')

        # IDA* solution
        ida_star = IDAStarSolver(heuristic=manhattan_distance, max_depth=10)
        solution_ida = ida_star.solve(cube)

        # Both should find solutions
        assert solution_a is not None
        assert solution_ida is not None

        # Solutions should be similar length (both optimal)
        assert abs(len(solution_a) - len(solution_ida)) <= 1

    def test_ida_star_uses_less_memory(self):
        """Test that IDA* uses significantly less memory than A*."""
        cube = RubikCube()
        cube.scramble(moves=5)

        # A* statistics
        a_star = AStarSolver(heuristic=manhattan_distance, max_depth=15)
        a_star.solve(cube)
        stats_a = a_star.get_statistics()

        # Reset cube
        cube = RubikCube()
        cube.scramble(moves=5)

        # IDA* statistics
        ida_star = IDAStarSolver(heuristic=manhattan_distance, max_depth=15)
        ida_star.solve(cube)
        stats_ida = ida_star.get_statistics()

        # IDA* should use much less memory
        assert stats_ida['estimated_memory_mb'] < stats_a.get('estimated_memory_mb', 10.0) / 10

    def test_composite_heuristic_integration(self):
        """Test that composite heuristic works with solvers."""
        cube = RubikCube()
        cube.apply_move('U')
        cube.apply_move('R')

        # Create composite heuristic
        heuristic = create_heuristic('composite')

        # Test with A*
        solver_a = AStarSolver(heuristic=heuristic, max_depth=10)
        solution_a = solver_a.solve(cube)
        assert solution_a is not None

        # Reset cube
        cube = RubikCube()
        cube.apply_move('U')
        cube.apply_move('R')

        # Test with IDA*
        solver_ida = IDAStarSolver(heuristic=heuristic, max_depth=10)
        solution_ida = solver_ida.solve(cube)
        assert solution_ida is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
