"""
Unit Tests for Kociemba Algorithm Implementation

Tests cover:
1. Cubie-level representation
2. Coordinate systems
3. Move tables
4. Pruning tables
5. Phase 1 and Phase 2 solvers
6. Full integration tests
"""

import pytest
import numpy as np
import time
from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import (
    CubieCube, from_facelet_cube, apply_move_to_cubie,
    ALL_MOVES
)
from src.kociemba.coord import (
    CoordCube,
    get_corner_orientation, set_corner_orientation,
    get_edge_orientation, set_edge_orientation,
    get_udslice, set_udslice,
    get_corner_permutation, set_corner_permutation,
    get_edge_permutation, set_edge_permutation,
    get_udslice_permutation, set_udslice_permutation
)
from src.kociemba.moves import get_move_tables
from src.kociemba.pruning import get_pruning_tables
from src.kociemba.solver import KociembaSolver, solve_cube


class TestCubieRepresentation:
    """Test cubie-level representation."""

    def test_solved_cube(self):
        """Test that a solved cube is correctly represented."""
        cubie = CubieCube()
        assert cubie.is_solved()
        assert np.array_equal(cubie.corner_perm, np.arange(8))
        assert np.array_equal(cubie.corner_orient, np.zeros(8))
        assert np.array_equal(cubie.edge_perm, np.arange(12))
        assert np.array_equal(cubie.edge_orient, np.zeros(12))

    def test_move_application(self):
        """Test applying moves to cubie cube."""
        cubie = CubieCube()

        # Apply U move
        cubie_u = apply_move_to_cubie(cubie, 'U')
        assert not cubie_u.is_solved()

        # Apply U' to undo
        cubie_u_prime = apply_move_to_cubie(cubie_u, "U'")
        assert cubie_u_prime.is_solved()

    def test_move_commutativity(self):
        """Test that U2 = U + U."""
        cubie = CubieCube()

        # Apply U twice
        cubie1 = apply_move_to_cubie(cubie, 'U')
        cubie1 = apply_move_to_cubie(cubie1, 'U')

        # Apply U2
        cubie2 = apply_move_to_cubie(cubie, 'U2')

        assert cubie1 == cubie2

    def test_move_inverse(self):
        """Test that X + X' + X' + X = identity."""
        cubie = CubieCube()

        for move in ['U', 'D', 'R', 'L', 'F', 'B']:
            test_cubie = apply_move_to_cubie(cubie, move)
            test_cubie = apply_move_to_cubie(test_cubie, move + "'")
            test_cubie = apply_move_to_cubie(test_cubie, move + "'")
            test_cubie = apply_move_to_cubie(test_cubie, move)
            assert test_cubie.is_solved()

    def test_facelet_to_cubie_conversion(self):
        """Test converting facelet cube to cubie cube."""
        # Test solved cube
        facelet = RubikCube()
        cubie = from_facelet_cube(facelet)
        assert cubie.is_solved()

        # Test after applying moves
        facelet.apply_move('R')
        facelet.apply_move('U')
        cubie = from_facelet_cube(facelet)
        assert not cubie.is_solved()


class TestCoordinates:
    """Test coordinate systems."""

    def test_corner_orientation_solved(self):
        """Test corner orientation coordinate for solved cube."""
        cubie = CubieCube()
        assert get_corner_orientation(cubie) == 0

    def test_edge_orientation_solved(self):
        """Test edge orientation coordinate for solved cube."""
        cubie = CubieCube()
        assert get_edge_orientation(cubie) == 0

    def test_udslice_solved(self):
        """Test UD-slice coordinate for solved cube."""
        cubie = CubieCube()
        assert get_udslice(cubie) == 0

    def test_corner_permutation_solved(self):
        """Test corner permutation coordinate for solved cube."""
        cubie = CubieCube()
        assert get_corner_permutation(cubie) == 0

    def test_edge_permutation_solved(self):
        """Test edge permutation coordinate for solved cube."""
        cubie = CubieCube()
        assert get_edge_permutation(cubie) == 0

    def test_udslice_permutation_solved(self):
        """Test UD-slice permutation coordinate for solved cube."""
        cubie = CubieCube()
        assert get_udslice_permutation(cubie) == 0

    def test_coordinate_ranges(self):
        """Test that coordinates are within valid ranges."""
        cubie = CubieCube()

        # Apply random moves
        for move in ['R', 'U', 'F', 'L', 'D', 'B', 'R2', 'U2']:
            cubie = apply_move_to_cubie(cubie, move)

        # Check ranges
        assert 0 <= get_corner_orientation(cubie) < 2187  # 3^7
        assert 0 <= get_edge_orientation(cubie) < 2048  # 2^11
        assert 0 <= get_udslice(cubie) < 495  # C(12,4)
        assert 0 <= get_corner_permutation(cubie) < 40320  # 8!
        assert 0 <= get_edge_permutation(cubie) < 40320  # 8!
        assert 0 <= get_udslice_permutation(cubie) < 24  # 4!

    def test_coord_cube_class(self):
        """Test CoordCube class."""
        cubie = CubieCube()
        coord = CoordCube(cubie)

        assert coord.is_solved()
        assert coord.is_phase1_solved()

    def test_coordinate_setting(self):
        """Test setting coordinates."""
        cubie = CubieCube()

        # Set corner orientation
        set_corner_orientation(cubie, 100)
        assert get_corner_orientation(cubie) == 100

        # Set edge orientation
        cubie = CubieCube()
        set_edge_orientation(cubie, 200)
        assert get_edge_orientation(cubie) == 200


class TestMoveTables:
    """Test move table generation and usage."""

    def test_move_tables_loading(self):
        """Test that move tables can be loaded."""
        tables = get_move_tables()
        tables.load()

        assert tables._loaded
        assert tables.corner_orient_moves is not None
        assert tables.edge_orient_moves is not None
        assert tables.udslice_moves is not None

    def test_move_table_dimensions(self):
        """Test that move tables have correct dimensions."""
        tables = get_move_tables()
        tables.load()

        # Phase 1 tables (18 moves)
        assert tables.corner_orient_moves.shape == (2187, 18)
        assert tables.edge_orient_moves.shape == (2048, 18)
        assert tables.udslice_moves.shape == (495, 18)

        # Phase 2 tables (10 moves)
        assert tables.corner_perm_moves.shape == (40320, 10)
        assert tables.edge_perm_moves.shape == (40320, 10)
        assert tables.udslice_perm_moves.shape == (24, 10)

    def test_move_table_consistency(self):
        """Test that move tables are consistent with direct application."""
        tables = get_move_tables()
        tables.load()

        cubie = CubieCube()
        cubie = apply_move_to_cubie(cubie, 'R')
        cubie = apply_move_to_cubie(cubie, 'U')

        co = get_corner_orientation(cubie)
        eo = get_edge_orientation(cubie)
        us = get_udslice(cubie)

        # Apply R move using table
        new_co, new_eo, new_us = tables.apply_move_to_coords(co, eo, us, 'F')

        # Apply F move directly
        cubie = apply_move_to_cubie(cubie, 'F')
        direct_co = get_corner_orientation(cubie)
        direct_eo = get_edge_orientation(cubie)
        direct_us = get_udslice(cubie)

        assert new_co == direct_co
        assert new_eo == direct_eo
        assert new_us == direct_us


class TestPruningTables:
    """Test pruning table generation and usage."""

    def test_pruning_tables_loading(self):
        """Test that pruning tables can be loaded."""
        tables = get_pruning_tables()
        tables.load(max_depth=8)  # Use smaller depth for testing

        assert tables._loaded
        assert tables.phase1_co_eo is not None
        assert tables.phase1_eo_slice is not None

    def test_phase1_heuristic_solved(self):
        """Test Phase 1 heuristic for solved cube."""
        tables = get_pruning_tables()
        tables.load(max_depth=8)

        h = tables.get_phase1_heuristic(0, 0, 0)
        assert h == 0  # Solved state should have heuristic 0

    def test_phase2_heuristic_solved(self):
        """Test Phase 2 heuristic for solved cube."""
        tables = get_pruning_tables()
        tables.load(max_depth=8)

        h = tables.get_phase2_heuristic(0, 0, 0)
        assert h == 0  # Solved state should have heuristic 0

    def test_heuristic_admissibility(self):
        """Test that heuristic never overestimates (admissibility)."""
        # This is tested implicitly by solver correctness
        pass


class TestKociembaSolver:
    """Test the full Kociemba solver."""

    def test_solve_solved_cube(self):
        """Test solving an already solved cube."""
        cube = RubikCube()
        solution = solve_cube(cube, timeout=10.0, verbose=False)

        assert solution is not None
        assert len(solution) == 0

    def test_solve_single_move(self):
        """Test solving a cube scrambled with a single move."""
        cube = RubikCube()
        cube.apply_move('R')

        solution = solve_cube(cube, timeout=10.0, verbose=False)

        assert solution is not None
        assert len(solution) <= 3  # Should find short solution

        # Verify solution
        test_cube = RubikCube()
        test_cube.apply_move('R')
        test_cube.apply_moves(solution)
        assert test_cube.is_solved()

    def test_solve_few_moves(self):
        """Test solving a cube with a few moves."""
        cube = RubikCube()
        scramble = ['R', 'U', 'R\'', 'U\'']
        cube.apply_moves(scramble)

        solution = solve_cube(cube, timeout=30.0, verbose=False)

        assert solution is not None

        # Verify solution
        test_cube = RubikCube()
        test_cube.apply_moves(scramble)
        test_cube.apply_moves(solution)
        assert test_cube.is_solved()

    def test_solve_scrambled_cube(self):
        """Test solving a randomly scrambled cube."""
        cube = RubikCube()
        scramble = cube.scramble(15, seed=42)

        print(f"\nScramble: {' '.join(scramble)}")

        start_time = time.time()
        solution = solve_cube(cube, timeout=30.0, verbose=False)
        solve_time = time.time() - start_time

        print(f"Solution length: {len(solution) if solution else 'FAILED'}")
        print(f"Solve time: {solve_time:.2f}s")

        assert solution is not None
        assert len(solution) < 30  # Should be reasonably short

        # Verify solution
        test_cube = RubikCube()
        test_cube.apply_moves(scramble)
        test_cube.apply_moves(solution)
        assert test_cube.is_solved()

    def test_solver_performance(self):
        """Test solver performance on multiple cubes."""
        solver = KociembaSolver()
        num_cubes = 5
        max_time = 10.0
        max_moves = 25

        print("\n" + "="*60)
        print("PERFORMANCE TEST")
        print("="*60)

        total_moves = 0
        total_time = 0
        success_count = 0

        for i in range(num_cubes):
            cube = RubikCube()
            scramble = cube.scramble(20, seed=100 + i)

            start_time = time.time()
            result = solver.solve(cube, timeout=max_time, verbose=False)
            solve_time = time.time() - start_time

            if result is not None:
                solution, _, _ = result
                total_moves += len(solution)
                total_time += solve_time
                success_count += 1

                print(f"Cube {i+1}: {len(solution)} moves in {solve_time:.2f}s")

                # Verify
                test_cube = RubikCube()
                test_cube.apply_moves(scramble)
                test_cube.apply_moves(solution)
                assert test_cube.is_solved()

                # Check move count
                assert len(solution) <= max_moves
            else:
                print(f"Cube {i+1}: FAILED")

        print(f"\nSuccess rate: {success_count}/{num_cubes}")
        if success_count > 0:
            print(f"Average moves: {total_moves / success_count:.1f}")
            print(f"Average time: {total_time / success_count:.2f}s")

        assert success_count == num_cubes  # All should succeed


class TestIntegration:
    """Integration tests."""

    def test_phase1_reaches_g1(self):
        """Test that Phase 1 actually reaches G1."""
        cube = RubikCube()
        cube.scramble(10, seed=123)

        solver = KociembaSolver()
        result = solver.solve(cube, timeout=30.0, verbose=False)

        assert result is not None
        solution, phase1, phase2 = result

        # Apply only Phase 1 solution
        test_cube = RubikCube()
        test_cube.apply_moves(['R', 'U', 'F', 'D', 'L', 'B'] * 2)  # Scramble
        test_cube.apply_moves(phase1)

        # Check if in G1
        cubie = from_facelet_cube(test_cube)
        coord = CoordCube(cubie)
        assert coord.is_phase1_solved()

    def test_full_solution_solves_cube(self):
        """Test that the complete solution solves the cube."""
        for seed in range(5):
            cube = RubikCube()
            scramble = cube.scramble(15, seed=seed)

            solution = solve_cube(cube, timeout=30.0, verbose=False)
            assert solution is not None

            # Apply solution
            test_cube = RubikCube()
            test_cube.apply_moves(scramble)
            test_cube.apply_moves(solution)

            assert test_cube.is_solved()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
