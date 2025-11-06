"""
IDA* Search Algorithm for Thistlethwaite Solver

Implements Iterative Deepening A* search with pruning tables
for efficient searching through the cube state space.
"""

from typing import List, Callable, Optional, Dict, Any
import time
from ..cube.rubik_cube import RubikCube


class IDAStarSearch:
    """
    IDA* search algorithm for finding optimal solutions within a phase.

    IDA* combines the space efficiency of iterative deepening with the
    efficiency of A* search using an admissible heuristic (pruning table).
    """

    def __init__(
        self,
        goal_check: Callable[[RubikCube], bool],
        heuristic: Callable[[RubikCube], int],
        allowed_moves: List[str],
        max_depth: int = 20,
        timeout: float = 60.0
    ):
        """
        Initialize IDA* search.

        Args:
            goal_check: Function that returns True if cube is at goal state
            heuristic: Admissible heuristic function (never overestimates distance to goal)
            allowed_moves: List of allowed move strings for this phase
            max_depth: Maximum search depth
            timeout: Timeout in seconds
        """
        self.goal_check = goal_check
        self.heuristic = heuristic
        self.allowed_moves = allowed_moves
        self.max_depth = max_depth
        self.timeout = timeout

        # Statistics
        self.nodes_explored = 0
        self.start_time = 0.0

    def search(self, cube: RubikCube) -> Optional[List[str]]:
        """
        Perform IDA* search to find a solution.

        Args:
            cube: Starting cube state

        Returns:
            List of moves to reach goal, or None if no solution found
        """
        self.start_time = time.time()
        self.nodes_explored = 0

        # Check if already at goal
        if self.goal_check(cube):
            return []

        # Get initial bound from heuristic
        bound = self.heuristic(cube)

        path: List[str] = []

        while bound <= self.max_depth:
            # Check timeout
            if time.time() - self.start_time > self.timeout:
                return None

            # Search with current bound
            result = self._search_recursive(cube, path, 0, bound)

            if isinstance(result, list):
                # Found solution
                return result
            elif result == float('inf'):
                # No solution exists
                return None
            else:
                # Increase bound and try again
                bound = result

        return None

    def _search_recursive(
        self,
        cube: RubikCube,
        path: List[str],
        g: int,
        bound: int
    ) -> Any:
        """
        Recursive IDA* search.

        Args:
            cube: Current cube state
            path: Current move path
            g: Cost to reach current state (path length)
            bound: Current cost bound

        Returns:
            - List of moves if solution found
            - New bound if f > bound
            - inf if no solution
        """
        self.nodes_explored += 1

        # Check timeout periodically
        if self.nodes_explored % 10000 == 0:
            if time.time() - self.start_time > self.timeout:
                return float('inf')

        # Calculate f = g + h
        h = self.heuristic(cube)
        f = g + h

        if f > bound:
            return f

        # Goal check
        if self.goal_check(cube):
            return path.copy()

        # Try all allowed moves
        min_bound = float('inf')

        for move in self.allowed_moves:
            # Prune: don't undo the previous move
            if path and self._is_redundant_move(path[-1], move):
                continue

            # Apply move
            next_cube = cube.copy()
            next_cube.apply_move(move)

            # Recursive search
            path.append(move)
            result = self._search_recursive(next_cube, path, g + 1, bound)
            path.pop()

            if isinstance(result, list):
                return result
            elif result < min_bound:
                min_bound = result

        return min_bound

    def _is_redundant_move(self, prev_move: str, current_move: str) -> bool:
        """
        Check if current move is redundant given the previous move.

        Redundant cases:
        1. Same face as previous move (e.g., U followed by U)
        2. Opposite faces in wrong order (e.g., U followed by D should be D followed by U)

        Args:
            prev_move: Previous move
            current_move: Current move to check

        Returns:
            True if redundant
        """
        prev_face = prev_move[0]
        curr_face = current_move[0]

        # Same face is redundant
        if prev_face == curr_face:
            return True

        # Opposite faces: enforce canonical order to avoid duplicates
        # Canonical order: U before D, F before B, L before R
        opposite_pairs = [('U', 'D'), ('F', 'B'), ('L', 'R')]

        for face1, face2 in opposite_pairs:
            if prev_face == face2 and curr_face == face1:
                return True

        return False


class IterativeDeepeningSearch:
    """
    Simple iterative deepening search (without heuristic).

    Useful for phases where the state space is small enough
    that a heuristic isn't necessary.
    """

    def __init__(
        self,
        goal_check: Callable[[RubikCube], bool],
        allowed_moves: List[str],
        max_depth: int = 20,
        timeout: float = 60.0
    ):
        """
        Initialize iterative deepening search.

        Args:
            goal_check: Function that returns True if cube is at goal state
            allowed_moves: List of allowed move strings
            max_depth: Maximum search depth
            timeout: Timeout in seconds
        """
        self.goal_check = goal_check
        self.allowed_moves = allowed_moves
        self.max_depth = max_depth
        self.timeout = timeout
        self.nodes_explored = 0
        self.start_time = 0.0

    def search(self, cube: RubikCube) -> Optional[List[str]]:
        """
        Perform iterative deepening search.

        Args:
            cube: Starting cube state

        Returns:
            List of moves to reach goal, or None if no solution found
        """
        self.start_time = time.time()
        self.nodes_explored = 0

        # Check if already at goal
        if self.goal_check(cube):
            return []

        # Try increasing depths
        for depth in range(1, self.max_depth + 1):
            result = self._depth_limited_search(cube, [], depth)
            if result is not None:
                return result

            # Check timeout
            if time.time() - self.start_time > self.timeout:
                return None

        return None

    def _depth_limited_search(
        self,
        cube: RubikCube,
        path: List[str],
        depth: int
    ) -> Optional[List[str]]:
        """
        Depth-limited search.

        Args:
            cube: Current cube state
            path: Current move path
            depth: Remaining depth

        Returns:
            List of moves if solution found, None otherwise
        """
        self.nodes_explored += 1

        # Check timeout periodically
        if self.nodes_explored % 10000 == 0:
            if time.time() - self.start_time > self.timeout:
                return None

        # Goal check
        if self.goal_check(cube):
            return path.copy()

        # Depth limit reached
        if depth == 0:
            return None

        # Try all moves
        for move in self.allowed_moves:
            # Prune redundant moves
            if path and self._is_redundant_move(path[-1], move):
                continue

            # Apply move
            next_cube = cube.copy()
            next_cube.apply_move(move)

            # Recursive search
            path.append(move)
            result = self._depth_limited_search(next_cube, path, depth - 1)
            path.pop()

            if result is not None:
                return result

        return None

    def _is_redundant_move(self, prev_move: str, current_move: str) -> bool:
        """Check if current move is redundant (same as IDAStarSearch)."""
        prev_face = prev_move[0]
        curr_face = current_move[0]

        if prev_face == curr_face:
            return True

        opposite_pairs = [('U', 'D'), ('F', 'B'), ('L', 'R')]
        for face1, face2 in opposite_pairs:
            if prev_face == face2 and curr_face == face1:
                return True

        return False
