"""
A* Search Algorithm for Rubik's Cube

Implements standard A* algorithm with a priority queue for cube-solving
experiments. Optimality is guaranteed only when the supplied heuristic is a
proven admissible lower bound; the lightweight demo heuristics in
`src.korf.heuristics` do not provide that guarantee.
This is compared against IDA* to demonstrate memory vs time tradeoffs.

Key Implementation Details:
- Uses heapq for efficient priority queue (min-heap)
- Maintains best-known g scores and reopens states when a better path is found
- Supports multiple heuristics, with explicit admissibility metadata
- Tracks performance metrics (nodes explored, memory usage)

References:
- BenSDuggan/CubeAI: Multi-heuristic A* implementation
- Korf (1997): Pattern database heuristics
- Russell & Norvig: A* algorithm fundamentals
"""

import heapq
import time
from typing import List, Callable, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from ..cube.rubik_cube import RubikCube

_IDA_TIMEOUT = object()


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
    A* solver for Rubik's Cube.

    This implementation demonstrates why A* is impractical for Rubik's Cube:
    - Memory consumption grows exponentially
    - Open set can reach millions of states
    - Closed set also requires significant memory

    Performance depends on the configured heuristic, scramble corpus, timeout,
    and memory limit. Use committed benchmark artifacts for thesis claims.
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
        memory_limit_mb: int = 2048,
        heuristic_is_admissible: bool = False,
    ):
        """
        Initialize A* solver.

        Args:
            heuristic: Heuristic distance estimate. Set
                heuristic_is_admissible=True only for proven lower bounds.
            max_depth: Maximum search depth (prevents infinite search)
            timeout: Timeout in seconds
            memory_limit_mb: Approximate memory limit in megabytes
            heuristic_is_admissible: Whether returned solutions carry an
                optimality guarantee.
        """
        self.heuristic = heuristic
        self.heuristic_is_admissible = heuristic_is_admissible
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

        start_hash = start_node.cube_state.state.tobytes()

        # best_g/open-set entries make this graph-search A* safe for
        # admissible but inconsistent heuristics. Duplicate heap entries are
        # allowed and discarded when they are stale.
        best_g: Dict[bytes, int] = {start_hash: 0}
        closed_g: Dict[bytes, int] = {}

        # State lookup for path reconstruction / debugging.
        state_lookup: Dict[bytes, SearchNode] = {}

        while open_set:
            # Check timeout
            if time.time() - self.start_time > self.timeout:
                return None

            # Check memory limit (approximate)
            if len(open_set) + len(closed_g) > self.memory_limit_mb * 100:
                # Approximate: 100 states per MB (conservative estimate)
                return None

            # Get node with lowest f-value
            current = heapq.heappop(open_set)
            self.nodes_explored += 1

            # Update metrics
            self.max_open_size = max(self.max_open_size, len(open_set))
            self.max_closed_size = max(self.max_closed_size, len(closed_g))

            # Get state hash
            state_hash = current.cube_state.state.tobytes()

            # Skip stale heap entries that were superseded by a better path.
            if current.g_value != best_g.get(state_hash, float("inf")):
                continue

            # Skip states already closed at an equal or lower path cost.
            if closed_g.get(state_hash, float("inf")) <= current.g_value:
                continue

            # Close the state at the best g found so far.
            closed_g[state_hash] = current.g_value
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

                # Calculate costs
                g_successor = current.g_value + 1
                if closed_g.get(successor_hash, float("inf")) <= g_successor:
                    continue
                if g_successor >= best_g.get(successor_hash, float("inf")):
                    continue

                h_successor = self.heuristic(successor_cube)
                f_successor = g_successor + h_successor
                best_g[successor_hash] = g_successor

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
            'approximate_memory_mb': (self.max_open_size + self.max_closed_size) / 100.0,
            'estimated_memory_mb': (self.max_open_size + self.max_closed_size) / 100.0,
            'memory_metric_kind': 'approximate_state_count',
            'heuristic_is_admissible': self.heuristic_is_admissible,
            'optimality_guarantee': self.heuristic_is_admissible,
            'reopens_improved_states': True,
        }


class IDAStarSolver:
    """
    IDA* (Iterative Deepening A*) solver for Rubik's Cube.

    Memory-efficient alternative to A* that uses iterative deepening.
    It has the usual IDA* optimality guarantee only when the supplied heuristic
    is a proven admissible lower bound.

    Key advantages over A*:
    - Constant memory (only stores current path)
    - Can solve thousands of cubes
    - No open/closed set overhead

    Key disadvantages:
    - Re-expands nodes multiple times
    - Can be slower for short solutions
    """

    ALL_MOVES = AStarSolver.ALL_MOVES
    TIMEOUT_CHECK_INTERVAL = 256

    def __init__(
        self,
        heuristic: Callable[[RubikCube], float],
        max_depth: int = 20,
        timeout: float = 300.0,
        heuristic_is_admissible: bool = False,
    ):
        """
        Initialize IDA* solver.

        Args:
            heuristic: Heuristic distance estimate. Set
                heuristic_is_admissible=True only for proven lower bounds.
            max_depth: Maximum search depth
            timeout: Timeout in seconds
            heuristic_is_admissible: Whether returned solutions carry an
                optimality guarantee.
        """
        self.heuristic = heuristic
        self.heuristic_is_admissible = heuristic_is_admissible
        self.max_depth = max_depth
        self.timeout = timeout

        # Performance metrics
        self.nodes_explored = 0
        self.start_time = 0.0
        self.timed_out = False
        self.depth_limit_reached = False
        self.solution_found = False

    def solve(self, cube: RubikCube) -> Optional[List[str]]:
        """
        Solve the cube using IDA* search.

        Args:
            cube: Starting cube state

        Returns:
            List of moves to solve, or None if no solution found
        """
        self.start_time = time.monotonic()
        self.nodes_explored = 0
        self.timed_out = False
        self.depth_limit_reached = False
        self.solution_found = False

        # Check if already solved
        if cube.is_solved():
            self.solution_found = True
            return []

        # Initialize bound with heuristic estimate
        bound = self.heuristic(cube)
        path: List[str] = []

        # Iterative deepening loop
        while bound <= self.max_depth:
            # Check timeout
            if self._deadline_exceeded():
                self.timed_out = True
                return None

            # Search with current bound
            result = self._search(cube, path, 0, bound)

            if isinstance(result, list):
                # Found solution
                self.solution_found = True
                return result
            elif result is _IDA_TIMEOUT:
                self.timed_out = True
                return None
            elif result == float('inf'):
                # Exhausted the bounded search tree at this threshold.
                self.depth_limit_reached = True
                return None
            else:
                # Increase bound and try again
                bound = result

        self.depth_limit_reached = True
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
            - inf if the bounded subtree is exhausted
            - _IDA_TIMEOUT if the wall-clock budget is exceeded
        """
        self.nodes_explored += 1

        if (
            self.timeout <= 0
            or self.nodes_explored % self.TIMEOUT_CHECK_INTERVAL == 0
        ) and self._deadline_exceeded():
            return _IDA_TIMEOUT

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
            elif result is _IDA_TIMEOUT:
                return _IDA_TIMEOUT
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

    def _deadline_exceeded(self) -> bool:
        """Return whether the configured wall-clock budget has expired."""
        return time.monotonic() - self.start_time >= self.timeout

    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        elapsed_time = time.monotonic() - self.start_time if self.start_time > 0 else 0

        return {
            'nodes_explored': self.nodes_explored,
            'time_elapsed': elapsed_time,
            'nodes_per_second': self.nodes_explored / elapsed_time if elapsed_time > 0 else 0,
            'approximate_memory_mb': 0.1,
            'estimated_memory_mb': 0.1,  # Minimal memory usage
            'memory_metric_kind': 'constant_stack_estimate',
            'timed_out': self.timed_out,
            'depth_limit_reached': self.depth_limit_reached,
            'solution_found': self.solution_found,
            'heuristic_is_admissible': self.heuristic_is_admissible,
            'optimality_guarantee': self.heuristic_is_admissible,
        }
