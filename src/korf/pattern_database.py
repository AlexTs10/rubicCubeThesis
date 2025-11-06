"""
Pattern Database Infrastructure for Distance Estimation

This module provides the base infrastructure for creating and using pattern databases
for Rubik's Cube distance estimation. Pattern databases store the exact minimum number
of moves needed to solve specific subsets of the cube (e.g., corners only, edges only).

Key Concepts:
- Pattern Database: Exhaustive BFS from solved state for a subset of pieces
- Compression: Store distances in nibbles (4 bits) to save memory
- Indexing: Use lexicographic ranking for perfect hashing
- Admissibility: Estimates never overestimate actual distance

References:
- Korf, R. (1997). Finding Optimal Solutions to Rubik's Cube Using Pattern Databases
- Culberson & Schaeffer (1998). Pattern Databases
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque
import pickle
import os


class PatternDatabase:
    """
    Base class for pattern databases.

    A pattern database stores the exact minimum distance to solve a specific
    subset of the cube (e.g., all corners, or a subset of edges).
    """

    def __init__(self, name: str, size: int):
        """
        Initialize a pattern database.

        Args:
            name: Name of this pattern database (e.g., "corner", "edge1")
            size: Number of states in this pattern database
        """
        self.name = name
        self.size = size

        # Store distances in nibbles (4 bits each)
        # This allows distances 0-15, which is sufficient for Rubik's Cube
        # We pack two distances per byte for 2x compression
        self.data = np.full((size + 1) // 2, 0xFF, dtype=np.uint8)

        # Track statistics
        self.max_depth = 0
        self.states_at_depth = {}

    def _pack_distance(self, distance: int) -> int:
        """
        Pack a distance value into a nibble (4 bits).

        Args:
            distance: Distance value (0-15)

        Returns:
            Packed value (0-15)
        """
        return min(distance, 15)

    def _unpack_distance(self, packed: int) -> int:
        """
        Unpack a distance value from a nibble.

        Args:
            packed: Packed value (0-15)

        Returns:
            Distance value (0-15, where 15 may mean "15 or more")
        """
        return packed

    def set_distance(self, index: int, distance: int) -> None:
        """
        Set the distance for a given state index.

        Args:
            index: State index in the pattern database
            distance: Minimum distance to solve this state
        """
        if index < 0 or index >= self.size:
            raise ValueError(f"Index {index} out of range [0, {self.size})")

        packed_dist = self._pack_distance(distance)
        byte_idx = index // 2

        if index % 2 == 0:
            # Store in lower nibble
            self.data[byte_idx] = (self.data[byte_idx] & 0xF0) | packed_dist
        else:
            # Store in upper nibble
            self.data[byte_idx] = (self.data[byte_idx] & 0x0F) | (packed_dist << 4)

    def get_distance(self, index: int) -> int:
        """
        Get the distance for a given state index.

        Args:
            index: State index in the pattern database

        Returns:
            Minimum distance to solve this state (0-15)
        """
        if index < 0 or index >= self.size:
            raise ValueError(f"Index {index} out of range [0, {self.size})")

        byte_idx = index // 2

        if index % 2 == 0:
            # Lower nibble
            packed = self.data[byte_idx] & 0x0F
        else:
            # Upper nibble
            packed = (self.data[byte_idx] >> 4) & 0x0F

        return self._unpack_distance(packed)

    def is_initialized(self, index: int) -> bool:
        """
        Check if a state has been initialized (distance set).

        Args:
            index: State index

        Returns:
            True if distance has been set, False if still uninitialized (0xFF)
        """
        return self.get_distance(index) != 15

    def save(self, filepath: str) -> None:
        """
        Save the pattern database to disk.

        Args:
            filepath: Path to save the database
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data_dict = {
            'name': self.name,
            'size': self.size,
            'data': self.data,
            'max_depth': self.max_depth,
            'states_at_depth': self.states_at_depth
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, filepath: str) -> 'PatternDatabase':
        """
        Load a pattern database from disk.

        Args:
            filepath: Path to the saved database

        Returns:
            Loaded pattern database
        """
        with open(filepath, 'rb') as f:
            data_dict = pickle.load(f)

        db = cls(data_dict['name'], data_dict['size'])
        db.data = data_dict['data']
        db.max_depth = data_dict['max_depth']
        db.states_at_depth = data_dict['states_at_depth']

        return db

    def get_statistics(self) -> Dict:
        """
        Get statistics about the pattern database.

        Returns:
            Dictionary with statistics
        """
        return {
            'name': self.name,
            'size': self.size,
            'max_depth': self.max_depth,
            'states_at_depth': self.states_at_depth,
            'memory_bytes': self.data.nbytes
        }

    def __str__(self) -> str:
        """String representation of the pattern database."""
        stats = self.get_statistics()
        lines = [
            f"Pattern Database: {stats['name']}",
            f"  States: {stats['size']:,}",
            f"  Max depth: {stats['max_depth']}",
            f"  Memory: {stats['memory_bytes'] / (1024*1024):.2f} MB"
        ]

        if stats['states_at_depth']:
            lines.append("  Distribution:")
            for depth in sorted(stats['states_at_depth'].keys()):
                count = stats['states_at_depth'][depth]
                pct = 100 * count / stats['size']
                lines.append(f"    Depth {depth}: {count:,} states ({pct:.2f}%)")

        return "\n".join(lines)


def bfs_generate_pattern_database(
    db: PatternDatabase,
    index_func,
    move_func,
    solved_index: int = 0,
    moves: Optional[List[str]] = None
) -> None:
    """
    Generate a pattern database using breadth-first search.

    This function performs BFS from the solved state, applying all possible moves
    and storing the minimum distance for each state.

    Args:
        db: Pattern database to populate
        index_func: Function that takes a state and returns its index
        move_func: Function that takes (state, move) and returns new state
        solved_index: Index of the solved state (default: 0)
        moves: List of moves to use (if None, uses all 18 basic moves)
    """
    if moves is None:
        moves = [
            'U', 'U\'', 'U2', 'D', 'D\'', 'D2',
            'F', 'F\'', 'F2', 'B', 'B\'', 'B2',
            'L', 'L\'', 'L2', 'R', 'R\'', 'R2'
        ]

    # Initialize: solved state has distance 0
    db.set_distance(solved_index, 0)
    db.states_at_depth[0] = 1

    # BFS queue: (state, depth)
    queue = deque([(solved_index, 0)])
    visited = {solved_index}

    states_processed = 0

    while queue:
        state_idx, depth = queue.popleft()

        states_processed += 1
        if states_processed % 100000 == 0:
            print(f"  Processed {states_processed:,} states, depth {depth}, queue size {len(queue):,}")

        # Try all moves
        for move in moves:
            try:
                # Apply move to get new state
                new_state_idx = move_func(state_idx, move)

                # Skip if already visited
                if new_state_idx in visited:
                    continue

                # Mark as visited and set distance
                visited.add(new_state_idx)
                new_depth = depth + 1
                db.set_distance(new_state_idx, new_depth)

                # Track statistics
                if new_depth > db.max_depth:
                    db.max_depth = new_depth
                db.states_at_depth[new_depth] = db.states_at_depth.get(new_depth, 0) + 1

                # Add to queue
                queue.append((new_state_idx, new_depth))

            except Exception as e:
                # Skip invalid states
                continue

    print(f"  Generation complete: {states_processed:,} states, max depth {db.max_depth}")
