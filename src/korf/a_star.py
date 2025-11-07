"""
A* Search Algorithm for Rubik's Cube

Implements standard A* algorithm with priority queue for optimal cube solving.
This is compared against IDA* to demonstrate memory vs time tradeoffs.

Key Implementation Details:
- Uses heapq for efficient priority queue (min-heap)
- Maintains open and closed sets for state management
- Supports multiple admissible heuristics
- Tracks performance metrics (nodes explored, memory usage)

References:
- BenSDuggan/CubeAI: Multi-heuristic A* implementation
- Korf (1997): Pattern database heuristics
- Russell & Norvig: A* algorithm fundamentals
"""

import heapq
import time
from typing import List, Callable, Optional, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from ..cube.rubik_cube import RubikCube


@dataclass(order=True)
class SearchNode:
    """
    Node in the A* search tree.

    Attributes:
        f_value: Total estimated cost (g + h)
        g_value: Cost from start to current node
        h_value: Heuristic estimate from current to goal
        cube_state: Current cube configuration
        move_sequence: Moves from start to current state
        parent_hash: Hash of parent state (for path reconstruction)
    """
    f_value: float
    g_value: int = field(compare=False)
    h_value: float = field(compare=False)
    cube_state: RubikCube = field(compare=False)
    move_sequence: List[str] = field(default_factory=list, compare=False)
    parent_hash: Optional[int] = field(default=None, compare=False)

    def __hash__(self):
        """Hash based on cube state for closed set membership."""
        return hash(self.cube_state.state.tobytes())


class AStarSolver:
    """
    A* solver for Rubik's Cube using admissible heuristics.

    This implementation demonstrates why A* is impractical for Rubik's Cube:
    - Memory consumption grows exponentially
    - Open set can reach millions of states
    - Closed set also requires significant memory

    Typical performance: Solves 40-50 cubes before running out of memory
    (compared to IDA* which can solve 5000+)
    """

    # All 18 possible moves (6 faces × 3 types)
    ALL_MOVES = [
        'U', 'U\'', 'U2',
        'D', 'D\'', 'D2',
        'F', 'F\'', 'F2',
        'B', 'B\'', 'B2',
        'L', 'L\'', 'L2',
        'R', 'R\'', 'R2',
    ]

    def __init__(
        self,
        heuristic: Callable[[RubikCube], float],
        max_depth: int = 20,
        timeout: float = 300.0,
        memory_limit_mb: int = 2048
    ):
        """
        Initialize A* solver.

        Args:
            heuristic: Admissible heuristic function (never overestimates)
            max_depth: Maximum search depth (prevents infinite search)
            timeout: Timeout in seconds
            memory_limit_mb: Approximate memory limit in megabytes
        """
        self.heuristic = heuristic
        self.max_depth = max_depth
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb

        # Performance metrics
        self.nodes_explored = 0
        self.nodes_generated = 0
        self.max_open_size = 0
        self.max_closed_size = 0
        self.start_time = 0.0

    def solve(self, cube: RubikCube) -> Optional[List[str]]:
        """
        Solve the cube using A* search.

        Args:
            cube: Starting cube state (scrambled)

        Returns:
            List of moves to solve the cube, or None if no solution found
        """
        self.start_time = time.time()
        self.nodes_explored = 0
        self.nodes_generated = 0
        self.max_open_size = 0
        self.max_closed_size = 0

        # Check if already solved
        if cube.is_solved():
            return []

        # Initialize open set (priority queue) with start state
        h_start = self.heuristic(cube)
        start_node = SearchNode(
            f_value=h_start,
            g_value=0,
            h_value=h_start,
            cube_state=cube.copy(),
            move_sequence=[],
            parent_hash=None
        )

        open_set: List[SearchNode] = [start_node]
        heapq.heapify(open_set)

        # Closed set: states already explored
        closed_set: Set[bytes] = set()

        # State lookup for path reconstruction
        state_lookup: Dict[bytes, SearchNode] = {}

        while open_set:
            # Check timeout
            if time.time() - self.start_time > self.timeout:
                return None

            # Check memory limit (approximate)
            if len(open_set) + len(closed_set) > self.memory_limit_mb * 100:
                # Approximate: 100 states per MB (conservative estimate)
                return None

            # Get node with lowest f-value
            current = heapq.heappop(open_set)
            self.nodes_explored += 1

            # Update metrics
            self.max_open_size = max(self.max_open_size, len(open_set))
            self.max_closed_size = max(self.max_closed_size, len(closed_set))

            # Get state hash
            state_hash = current.cube_state.state.tobytes()

            # Skip if already explored
            if state_hash in closed_set:
                continue

            # Add to closed set
            closed_set.add(state_hash)
            state_lookup[state_hash] = current

            # Goal test
            if current.cube_state.is_solved():
                return current.move_sequence

            # Depth limit check
            if current.g_value >= self.max_depth:
                continue

            # Generate successors
            for move in self.ALL_MOVES:
                # Prune redundant moves
                if current.move_sequence and self._is_redundant_move(
                    current.move_sequence[-1], move
                ):
                    continue

                # Apply move
                successor_cube = current.cube_state.copy()
                successor_cube.apply_move(move)
                successor_hash = successor_cube.state.tobytes()

                # Skip if already explored
                if successor_hash in closed_set:
                    continue

                # Calculate costs
                g_successor = current.g_value + 1
                h_successor = self.heuristic(successor_cube)
                f_successor = g_successor + h_successor

                # Create successor node
                successor_node = SearchNode(
                    f_value=f_successor,
                    g_value=g_successor,
                    h_value=h_successor,
                    cube_state=successor_cube,
                    move_sequence=current.move_sequence + [move],
                    parent_hash=state_hash
                )

                # Add to open set
                heapq.heappush(open_set, successor_node)
                self.nodes_generated += 1

        # No solution found
        return None

    def _is_redundant_move(self, prev_move: str, current_move: str) -> bool:
        """
        Check if current move is redundant given the previous move.

        Redundant cases:
        1. Same face (e.g., U followed by U')
        2. Opposite faces in non-canonical order (e.g., U-D should be D-U)

        Args:
            prev_move: Previous move
            current_move: Current move to check

        Returns:
            True if redundant
        """
        prev_face = prev_move[0]
        curr_face = current_move[0]

        # Same face is redundant (will be combined)
        if prev_face == curr_face:
            return True

        # Opposite faces: enforce canonical order
        # Canonical: U before D, F before B, L before R
        opposite_pairs = [('U', 'D'), ('F', 'B'), ('L', 'R')]

        for face1, face2 in opposite_pairs:
            if prev_face == face2 and curr_face == face1:
                return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics from the last solve attempt.

        Returns:
            Dictionary with performance metrics
        """
        elapsed_time = time.time() - self.start_time if self.start_time > 0 else 0

        return {
            'nodes_explored': self.nodes_explored,
            'nodes_generated': self.nodes_generated,
            'max_open_size': self.max_open_size,
            'max_closed_size': self.max_closed_size,
            'total_states_stored': self.max_open_size + self.max_closed_size,
            'time_elapsed': elapsed_time,
            'nodes_per_second': self.nodes_explored / elapsed_time if elapsed_time > 0 else 0,
            'estimated_memory_mb': (self.max_open_size + self.max_closed_size) / 100.0,
        }


class IDAStarSolver:
    """
    IDA* (Iterative Deepening A*) solver for Rubik's Cube.

    Memory-efficient alternative to A* that uses iterative deepening
    with an admissible heuristic. Much more practical for Rubik's Cube.

    Key advantages over A*:
    - Constant memory (only stores current path)
    - Can solve thousands of cubes
    - No open/closed set overhead

    Key disadvantages:
    - Re-expands nodes multiple times
    - Can be slower for short solutions
    """

    ALL_MOVES = AStarSolver.ALL_MOVES

    def __init__(
        self,
        heuristic: Callable[[RubikCube], float],
        max_depth: int = 20,
        timeout: float = 300.0
    ):
        """
        Initialize IDA* solver.

        Args:
            heuristic: Admissible heuristic function
            max_depth: Maximum search depth
            timeout: Timeout in seconds
        """
        self.heuristic = heuristic
        self.max_depth = max_depth
        self.timeout = timeout

        # Performance metrics
        self.nodes_explored = 0
        self.start_time = 0.0

    def solve(self, cube: RubikCube) -> Optional[List[str]]:
        """
        Solve the cube using IDA* search.

        Args:
            cube: Starting cube state

        Returns:
            List of moves to solve, or None if no solution found
        """
        self.start_time = time.time()
        self.nodes_explored = 0

        # Check if already solved
        if cube.is_solved():
            return []

        # Initialize bound with heuristic estimate
        bound = self.heuristic(cube)
        path: List[str] = []

        # Iterative deepening loop
        while bound <= self.max_depth:
            # Check timeout
            if time.time() - self.start_time > self.timeout:
                return None

            # Search with current bound
            result = self._search(cube, path, 0, bound)

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

    def _search(
        self,
        cube: RubikCube,
        path: List[str],
        g: int,
        bound: float
    ) -> Any:
        """
        Recursive IDA* search.

        Args:
            cube: Current cube state
            path: Current move path
            g: Cost from start to current state
            bound: Current f-value bound

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

        # If f exceeds bound, return f for next iteration
        if f > bound:
            return f

        # Goal test
        if cube.is_solved():
            return path.copy()

        # Generate successors
        min_bound = float('inf')

        for move in self.ALL_MOVES:
            # Prune redundant moves
            if path and self._is_redundant_move(path[-1], move):
                continue

            # Apply move
            next_cube = cube.copy()
            next_cube.apply_move(move)

            # Recursive search
            path.append(move)
            result = self._search(next_cube, path, g + 1, bound)
            path.pop()

            if isinstance(result, list):
                return result
            elif result < min_bound:
                min_bound = result

        return min_bound

    def _is_redundant_move(self, prev_move: str, current_move: str) -> bool:
        """Check if current move is redundant (same as A*)."""
        prev_face = prev_move[0]
        curr_face = current_move[0]

        if prev_face == curr_face:
            return True

        opposite_pairs = [('U', 'D'), ('F', 'B'), ('L', 'R')]
        for face1, face2 in opposite_pairs:
            if prev_face == face2 and curr_face == face1:
                return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        elapsed_time = time.time() - self.start_time if self.start_time > 0 else 0

        return {
            'nodes_explored': self.nodes_explored,
            'time_elapsed': elapsed_time,
            'nodes_per_second': self.nodes_explored / elapsed_time if elapsed_time > 0 else 0,
            'estimated_memory_mb': 0.1,  # Minimal memory usage
        }
