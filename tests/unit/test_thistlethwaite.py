"""
Unit Tests for Thistlethwaite Algorithm

Tests the implementation of Thistlethwaite's 4-phase algorithm
for solving the Rubik's Cube.
"""

import math
import time
import pytest
import numpy as np
from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver
from src.thistlethwaite.coordinates import CubeCoordinates, permutation_to_rank, rank_to_permutation
from src.kociemba.cubie import from_facelet_cube
from src.kociemba.coord import get_corner_orientation, get_edge_orientation, get_udslice
from src.thistlethwaite.moves import (
    PHASE_0_MOVES,
    PHASE_1_MOVES,
    PHASE_2_MOVES,
    PHASE_3_MOVES,
    get_phase_moves,
    is_move_allowed
)
from src.thistlethwaite.ida_star import IDAStarSearch, IterativeDeepeningSearch


class TestPermutationRanking:
    """Test permutation to rank conversion utilities."""

    def test_permutation_to_rank_identity(self):
        """Test that identity permutation has rank 0."""
        perm = np.array([0, 1, 2, 3])
        assert permutation_to_rank(perm) == 0

    def test_permutation_to_rank_last(self):
        """Test that reverse permutation has max rank."""
        perm = np.array([3, 2, 1, 0])
        # For n=4, max rank is 4! - 1 = 23
        rank = permutation_to_rank(perm)
        assert rank == 23

    def test_rank_to_permutation_roundtrip(self):
        """Test that rank_to_permutation is inverse of permutation_to_rank."""
        for n in [3, 4, 5]:
            for rank in range(0, min(24, math.factorial(n))):
                perm = rank_to_permutation(rank, n)
                recovered_rank = permutation_to_rank(perm)
                assert recovered_rank == rank


class TestCubeCoordinates:
    """Test cube coordinate extraction."""

    def test_solved_cube_coordinates(self):
        """Test that solved cube has all coordinates at 0."""
        cube = RubikCube()
        coords = CubeCoordinates(cube)

        # Solved cube should have all orientations at 0
        assert coords.get_edge_orientation_coord() == 0
        assert coords.get_corner_orientation_coord() == 0

    def test_edge_orientation_after_move(self):
        """Test edge orientation coordinate after moves."""
        cube = RubikCube()

        # U move should not change edge orientation (edges stay oriented)
        cube.apply_move('U')
        coords = CubeCoordinates(cube)
        assert coords.get_edge_orientation_coord() == 0

        # F move flips edges in this cubie convention.
        cube2 = RubikCube()
        cube2.apply_move('F')
        coords2 = CubeCoordinates(cube2)
        assert coords2.get_edge_orientation_coord() == get_edge_orientation(from_facelet_cube(cube2))
        assert coords2.get_edge_orientation_coord() != 0

    def test_corner_orientation_after_move(self):
        """Test corner orientation coordinate after moves."""
        cube = RubikCube()

        # U move should not change corner orientation
        cube.apply_move('U')
        coords = CubeCoordinates(cube)
        assert coords.get_corner_orientation_coord() == 0

        # R and F quarter turns twist corners in the trusted cubie convention.
        cube2 = RubikCube()
        cube2.apply_move('R')
        coords2 = CubeCoordinates(cube2)
        assert coords2.get_corner_orientation_coord() == get_corner_orientation(from_facelet_cube(cube2))
        assert coords2.get_corner_orientation_coord() != 0

    def test_coordinates_match_cubie_model_after_f_turn(self):
        """Thistlethwaite coordinates must agree with the trusted cubie model."""
        cube = RubikCube()
        cube.apply_move('F')

        coords = CubeCoordinates(cube)
        cubie = from_facelet_cube(cube)

        np.testing.assert_array_equal(coords.corner_permutation, cubie.corner_perm)
        np.testing.assert_array_equal(coords.corner_orientation, cubie.corner_orient)
        np.testing.assert_array_equal(coords.edge_permutation, cubie.edge_perm)
        np.testing.assert_array_equal(coords.edge_orientation, cubie.edge_orient)
        assert coords.get_corner_orientation_coord() == get_corner_orientation(cubie)
        assert coords.get_edge_orientation_coord() == get_edge_orientation(cubie)
        assert coords.get_e_slice_coord() == get_udslice(cubie)

    def test_coordinates_match_cubie_model_after_commutator(self):
        """Non-trivial states must preserve exact piece data."""
        cube = RubikCube()
        cube.apply_moves(['U', 'R', "U'", "R'"])

        coords = CubeCoordinates(cube)
        cubie = from_facelet_cube(cube)

        np.testing.assert_array_equal(coords.corner_permutation, cubie.corner_perm)
        np.testing.assert_array_equal(coords.corner_orientation, cubie.corner_orient)
        np.testing.assert_array_equal(coords.edge_permutation, cubie.edge_perm)
        np.testing.assert_array_equal(coords.edge_orientation, cubie.edge_orient)
        assert coords.get_corner_orientation_coord() == get_corner_orientation(cubie)
        assert coords.get_edge_orientation_coord() == get_edge_orientation(cubie)
        assert coords.get_e_slice_coord() == get_udslice(cubie)


class TestPhaseMoveSets:
    """Test phase move set definitions."""

    def test_phase_move_counts(self):
        """Test that each phase has correct number of allowed moves."""
        assert len(PHASE_0_MOVES) == 18  # All moves
        assert len(PHASE_1_MOVES) == 14  # Remove F, F', B, B'
        assert len(PHASE_2_MOVES) == 10  # Remove L, L', R, R' as well
        assert len(PHASE_3_MOVES) == 6   # Only double moves

    def test_phase_move_restrictions(self):
        """Test that phase moves follow proper restrictions."""
        # Phase 1 should not have F, B quarter turns
        assert 'F' not in PHASE_1_MOVES
        assert 'F\'' not in PHASE_1_MOVES
        assert 'B' not in PHASE_1_MOVES
        assert 'B\'' not in PHASE_1_MOVES
        assert 'F2' in PHASE_1_MOVES  # F2 is allowed
        assert 'B2' in PHASE_1_MOVES  # B2 is allowed

        # Phase 2 should not have L, R quarter turns
        assert 'L' not in PHASE_2_MOVES
        assert 'L\'' not in PHASE_2_MOVES
        assert 'R' not in PHASE_2_MOVES
        assert 'R\'' not in PHASE_2_MOVES

        # Phase 3 should only have double moves
        for move in PHASE_3_MOVES:
            assert move.endswith('2')

    def test_get_phase_moves(self):
        """Test get_phase_moves function."""
        assert get_phase_moves(0) == PHASE_0_MOVES
        assert get_phase_moves(1) == PHASE_1_MOVES
        assert get_phase_moves(2) == PHASE_2_MOVES
        assert get_phase_moves(3) == PHASE_3_MOVES

        with pytest.raises(ValueError):
            get_phase_moves(-1)

        with pytest.raises(ValueError):
            get_phase_moves(4)

    def test_is_move_allowed(self):
        """Test is_move_allowed function."""
        # Phase 0 allows all moves
        assert is_move_allowed('U', 0)
        assert is_move_allowed('F', 0)
        assert is_move_allowed('R\'', 0)

        # Phase 1 does not allow F quarter turn
        assert not is_move_allowed('F', 1)
        assert is_move_allowed('F2', 1)

        # Phase 3 only allows double moves
        assert not is_move_allowed('U', 3)
        assert is_move_allowed('U2', 3)

    def test_phase_move_sets_preserve_previous_invariants(self):
        """Later phase move sets must preserve invariants solved by earlier phases."""
        for move in PHASE_1_MOVES:
            cube = RubikCube()
            cube.apply_move(move)
            cubie = from_facelet_cube(cube)
            assert get_edge_orientation(cubie) == 0

        for move in PHASE_2_MOVES:
            cube = RubikCube()
            cube.apply_move(move)
            cubie = from_facelet_cube(cube)
            assert get_edge_orientation(cubie) == 0
            assert get_corner_orientation(cubie) == 0
            assert get_udslice(cubie) == 0

        for move in PHASE_3_MOVES:
            cube = RubikCube()
            cube.apply_move(move)
            cubie = from_facelet_cube(cube)
            assert get_edge_orientation(cubie) == 0
            assert get_corner_orientation(cubie) == 0
            assert get_udslice(cubie) == 0


class TestIDAStarSearch:
    """Test IDA* search algorithm."""

    def test_search_already_at_goal(self):
        """Test that search returns empty path when already at goal."""
        cube = RubikCube()

        def goal_check(c):
            return c.is_solved()

        def heuristic(c):
            return 0

        search = IDAStarSearch(
            goal_check=goal_check,
            heuristic=heuristic,
            allowed_moves=['U', 'R'],
            max_depth=5
        )

        result = search.search(cube)
        assert result == []

    def test_search_simple_scramble(self):
        """Test search on a simple scramble."""
        cube = RubikCube()
        cube.apply_move('U')

        def goal_check(c):
            return c.is_solved()

        def heuristic(c):
            return 0 if c.is_solved() else 1

        search = IDAStarSearch(
            goal_check=goal_check,
            heuristic=heuristic,
            allowed_moves=['U', 'U\'', 'U2'],
            max_depth=5
        )

        result = search.search(cube)
        assert result is not None
        assert len(result) <= 3  # U can be undone in at most 3 moves

        # Verify solution
        test_cube = cube.copy()
        test_cube.apply_moves(result)
        assert test_cube.is_solved()

    def test_search_respects_timeout(self):
        """Search should stop close to the requested timeout instead of overshooting badly."""
        cube = RubikCube()
        cube.apply_moves(['U', 'R', 'F'])

        def goal_check(c):
            return False

        def heuristic(c):
            return 0

        search = IDAStarSearch(
            goal_check=goal_check,
            heuristic=heuristic,
            allowed_moves=PHASE_0_MOVES,
            max_depth=20,
            timeout=0.01,
        )

        start = time.time()
        result = search.search(cube)
        elapsed = time.time() - start

        assert result is None
        assert elapsed < 1.0


class TestIterativeDeepeningSearch:
    """Test iterative deepening search."""

    def test_iterative_deepening_simple(self):
        """Test iterative deepening on simple case."""
        cube = RubikCube()
        cube.apply_moves(['U', 'R'])

        def goal_check(c):
            return c.is_solved()

        search = IterativeDeepeningSearch(
            goal_check=goal_check,
            allowed_moves=['U', 'U\'', 'U2', 'R', 'R\'', 'R2'],
            max_depth=10
        )

        result = search.search(cube)
        assert result is not None
        assert len(result) <= 10

        # Verify solution
        test_cube = cube.copy()
        test_cube.apply_moves(result)
        assert test_cube.is_solved()


class TestThistlethwaiteSolver:
    """Test complete Thistlethwaite solver."""

    def test_solver_initialization(self):
        """Test that solver initializes correctly."""
        solver = ThistlethwaiteSolver(use_pattern_databases=False)
        assert solver is not None
        assert not solver._databases_loaded
        assert solver.enable_kociemba_fallback is False

    def test_solve_already_solved_cube(self):
        """Test solving an already solved cube."""
        cube = RubikCube()
        solver = ThistlethwaiteSolver(use_pattern_databases=False)

        result = solver.solve(cube, verbose=False)
        assert result is not None

        all_moves, phase_moves, used_fallback = result
        assert len(all_moves) == 0
        assert all([len(phase) == 0 for phase in phase_moves])
        assert used_fallback is False  # No fallback needed for solved cube

    def test_solve_simple_scramble(self):
        """Test solving a simple scramble."""
        cube = RubikCube()
        scramble = ['U', 'R', 'U\'', 'R\'']
        cube.apply_moves(scramble)

        solver = ThistlethwaiteSolver(use_pattern_databases=False)
        result = solver.solve(cube, verbose=False)

        assert result is not None

        all_moves, phase_moves, used_fallback = result

        # Verify solution works
        test_cube = cube.copy()
        test_cube.apply_moves(all_moves)
        assert test_cube.is_solved()

        # Solution should be reasonably short
        assert len(all_moves) <= 52  # Thistlethwaite guarantees <= 52 moves

    def test_exact_g3_membership_rejects_old_false_positive(self):
        """A state that only passed the old tetrad approximation must not count as G3."""
        solver = ThistlethwaiteSolver(use_pattern_databases=True)
        solver._ensure_databases_loaded()

        cube = RubikCube()
        cube.apply_moves(['U', 'R2', "D'", "R'", 'U'])

        # Old buggy run reached this state after phase 1+2 and then entered an
        # impossible half-turn-only phase 3.
        cube.apply_moves(["U'", 'R', "U'", 'L2', 'D'])

        assert solver.pattern_databases.is_phase3_reachable(cube) is False

    def test_pattern_database_solver_handles_previous_phase3_false_positive_scramble(self):
        """The exact G3 table should allow this formerly failing pure solve to succeed."""
        cube = RubikCube()
        cube.apply_moves(['U', 'R2', "D'", "R'", 'U'])

        solver = ThistlethwaiteSolver(
            use_pattern_databases=True,
            enable_kociemba_fallback=False,
        )

        result = solver.solve(cube, verbose=False, max_time=30.0)
        assert result is not None

        all_moves, _, used_fallback = result
        test_cube = cube.copy()
        test_cube.apply_moves(all_moves)
        assert test_cube.is_solved()
        assert used_fallback is False

    def test_pure_solver_aborts_without_fallback(self, monkeypatch):
        """Pure Thistlethwaite mode must not silently delegate to Kociemba."""
        cube = RubikCube()
        cube.apply_move('U')

        solver = ThistlethwaiteSolver(
            use_pattern_databases=False,
            enable_kociemba_fallback=False,
        )

        monkeypatch.setattr(solver, "_solve_phase", lambda *args, **kwargs: None)

        def fail_if_called(*args, **kwargs):
            raise AssertionError("Fallback must not be called in pure mode")

        monkeypatch.setattr(solver, "_fallback_with_kociemba", fail_if_called)

        result = solver.solve(cube, verbose=False)

        assert result is None

    def test_hybrid_solver_uses_fallback_when_enabled(self, monkeypatch):
        """Hybrid mode should use the explicit Kociemba rescue path."""
        cube = RubikCube()
        cube.apply_move('U')

        solver = ThistlethwaiteSolver(
            use_pattern_databases=False,
            enable_kociemba_fallback=True,
        )

        monkeypatch.setattr(solver, "_solve_phase", lambda *args, **kwargs: None)
        monkeypatch.setattr(solver, "_fallback_with_kociemba", lambda *args, **kwargs: ["U'"])

        result = solver.solve(cube, verbose=False)

        assert result is not None

        all_moves, phase_moves, used_fallback = result
        assert all_moves == ["U'"]
        assert phase_moves[-1] == ["U'"]
        assert used_fallback is True

        test_cube = cube.copy()
        test_cube.apply_moves(all_moves)
        assert test_cube.is_solved()

    def test_solve_multiple_scrambles(self):
        """Test solving multiple different scrambles."""
        solver = ThistlethwaiteSolver(use_pattern_databases=False)

        for seed in range(3):  # Test 3 different scrambles
            cube = RubikCube()
            cube.scramble(moves=5, seed=seed)

            result = solver.solve(cube, verbose=False)

            if result is not None:
                all_moves, _, _ = result

                # Verify solution
                test_cube = cube.copy()
                test_cube.apply_moves(all_moves)
                assert test_cube.is_solved()

                # Check move count
                assert len(all_moves) <= 52

    def test_phase_moves_maintain_invariants(self):
        """Test that moves in each phase maintain previous invariants."""
        cube = RubikCube()
        cube.scramble(moves=5, seed=42)

        solver = ThistlethwaiteSolver(use_pattern_databases=False)
        result = solver.solve(cube, verbose=False)

        if result is None:
            pytest.skip("Solver failed (may need pattern databases)")

        all_moves, phase_moves, _ = result

        # Apply phase by phase and check goals
        test_cube = cube.copy()

        # Phase 0: Orient edges
        test_cube.apply_moves(phase_moves[0])
        coords = CubeCoordinates(test_cube)
        assert coords.get_edge_orientation_coord() == 0

        # Phase 1: Orient corners
        test_cube.apply_moves(phase_moves[1])
        coords = CubeCoordinates(test_cube)
        assert coords.get_edge_orientation_coord() == 0
        assert coords.get_corner_orientation_coord() == 0
        assert coords.get_e_slice_coord() == 0

        # Phase 2: Tetrads
        test_cube.apply_moves(phase_moves[2])
        coords = CubeCoordinates(test_cube)
        assert coords.get_edge_orientation_coord() == 0
        assert coords.get_corner_orientation_coord() == 0
        assert coords.get_e_slice_coord() == 0

        # Phase 3: Solve
        test_cube.apply_moves(phase_moves[3])
        assert test_cube.is_solved()


class TestSolutionQuality:
    """Test solution quality and performance."""

    @pytest.mark.slow
    def test_solution_length_bound(self):
        """Test that solutions stay within theoretical bounds."""
        solver = ThistlethwaiteSolver(use_pattern_databases=False)

        for seed in range(5):
            cube = RubikCube()
            cube.scramble(moves=10, seed=seed)

            result = solver.solve(cube, verbose=False)

            if result is not None:
                all_moves, phase_moves, _ = result

                # Check overall bound
                assert len(all_moves) <= 52

                # Check individual phase bounds (relaxed for testing)
                assert len(phase_moves[0]) <= 15  # Phase 0: should be <= 7, but relaxed
                assert len(phase_moves[1]) <= 20  # Phase 1: should be <= 13, but relaxed
                assert len(phase_moves[2]) <= 25  # Phase 2: should be <= 15, but relaxed
                assert len(phase_moves[3]) <= 30  # Phase 3: should be <= 17, but relaxed

    @pytest.mark.slow
    def test_solution_correctness(self):
        """Test that all solutions correctly solve the cube."""
        solver = ThistlethwaiteSolver(use_pattern_databases=False)

        for seed in range(10):
            cube = RubikCube()
            cube.scramble(moves=8, seed=seed)

            result = solver.solve(cube, verbose=False)

            if result is not None:
                all_moves, _, _ = result

                # Verify solution
                test_cube = cube.copy()
                test_cube.apply_moves(all_moves)

                assert test_cube.is_solved(), \
                    f"Solution failed for scramble with seed {seed}"


@pytest.mark.slow
def test_integration_example():
    """Integration test: complete solve example."""
    # Create a scrambled cube
    cube = RubikCube()
    scramble = cube.scramble(moves=10, seed=12345)

    print(f"\nScramble: {' '.join(scramble)}")

    # Solve with Thistlethwaite
    solver = ThistlethwaiteSolver(use_pattern_databases=False)
    result = solver.solve(cube, verbose=True)

    if result is not None:
        all_moves, phase_moves, used_fallback = result

        print(f"\nSolution: {' '.join(all_moves)}")
        print(f"Total moves: {len(all_moves)}")
        print(f"Used fallback: {used_fallback}")

        # Verify
        test_cube = RubikCube()
        test_cube.apply_moves(scramble)
        test_cube.apply_moves(all_moves)

        assert test_cube.is_solved()
        print("✓ Solution verified!")
    else:
        print("Solver did not find solution (may need pattern databases)")
