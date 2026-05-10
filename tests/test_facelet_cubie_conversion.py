import pytest
import numpy as np

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import CubieCube, from_facelet_cube, to_facelet_cube
from src.kociemba.coord import (
    get_corner_orientation,
    get_edge_orientation,
    get_udslice,
    set_corner_orientation,
    set_edge_orientation,
    set_udslice,
)


def test_roundtrip_facelet_cubie_identity():
    cube = RubikCube()
    cubie = from_facelet_cube(cube)
    rebuilt = to_facelet_cube(cubie)
    np.testing.assert_array_equal(cube.state, rebuilt.state)


def test_roundtrip_random_scramble():
    cube = RubikCube()
    for move in [
        'R', "U'", 'F2', 'L', 'B', 'D2', 'R2', 'F', "L'", 'U2'
    ]:
        cube.apply_move(move)

    cubie = from_facelet_cube(cube)
    rebuilt = to_facelet_cube(cubie)
    np.testing.assert_array_equal(cube.state, rebuilt.state)


def test_coordinate_consistency_after_roundtrip():
    cubie = from_facelet_cube(RubikCube())
    set_corner_orientation(cubie, 137)
    set_edge_orientation(cubie, 923)
    set_udslice(cubie, 271)

    rebuilt_facelet = to_facelet_cube(cubie)
    rebuilt_cubie = from_facelet_cube(rebuilt_facelet)

    assert get_corner_orientation(rebuilt_cubie) == 137
    assert get_edge_orientation(rebuilt_cubie) == 923
    assert get_udslice(rebuilt_cubie) == 271


def test_from_facelet_cube_rejects_single_twisted_corner():
    cubie = CubieCube()
    cubie.corner_orient[0] = 1

    with pytest.raises(ValueError, match="corner orientation sum must be divisible by 3"):
        to_facelet_cube(cubie)


def test_from_facelet_cube_rejects_single_flipped_edge():
    cubie = CubieCube()
    cubie.edge_orient[0] = 1

    with pytest.raises(ValueError, match="edge orientation sum must be even"):
        to_facelet_cube(cubie)


def test_from_facelet_cube_rejects_permutation_parity_mismatch():
    cubie = CubieCube()
    cubie.edge_perm[[0, 1]] = cubie.edge_perm[[1, 0]]

    with pytest.raises(ValueError, match="permutation parity must match"):
        to_facelet_cube(cubie)


def test_to_facelet_cube_rejects_duplicate_corner_permutation():
    cubie = CubieCube()
    cubie.corner_perm[1] = cubie.corner_perm[0]

    with pytest.raises(
        ValueError,
        match="corner permutation must contain each corner exactly once",
    ):
        to_facelet_cube(cubie)
