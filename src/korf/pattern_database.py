"""
Pattern Database Infrastructure for Distance Estimation

This module provides the base infrastructure for creating and using pattern databases
for Rubik's Cube distance estimation. Pattern databases store the exact minimum number
of moves needed to solve specific subsets of the cube (e.g., corners only, edges only).

The original repository stored distances in packed nibbles. That representation was
space-efficient, but it conflated the valid distance value 15 with the implicit
"uninitialized" sentinel and also clamped larger distances. The exact solver path
needs exact-safe semantics first, so the default storage format is now one byte per
state with an explicit uninitialized value of 255.

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

    FORMAT_VERSION = 2
    STORAGE_FORMAT_BYTE = "byte"
    LEGACY_STORAGE_FORMAT_NIBBLE = "legacy_nibble"
    BYTE_UNINITIALIZED = np.uint8(0xFF)

    def __init__(self, name: str, size: int):
        """
        Initialize a pattern database.

        Args:
            name: Name of this pattern database (e.g., "corner", "edge1")
            size: Number of states in this pattern database
        """
        self.name = name
        self.size = size

        # Exact-safe default: one byte per entry, with a dedicated uninitialized sentinel.
        self.storage_format = self.STORAGE_FORMAT_BYTE
        self.uninitialized_value = int(self.BYTE_UNINITIALIZED)
        self.data = np.full(size, self.BYTE_UNINITIALIZED, dtype=np.uint8)

        # Track statistics
        self.max_depth = 0
        self.states_at_depth = {}

    def _pack_distance(self, distance: int) -> int:
        """
        Pack a distance value for storage.

        Args:
            distance: Distance value

        Returns:
            Packed value
        """
        if distance < 0:
            raise ValueError(f"Distance must be non-negative, got {distance}")
        if distance >= self.uninitialized_value:
            raise ValueError(
                f"Distance {distance} cannot be stored in {self.storage_format} format "
                f"(reserved sentinel={self.uninitialized_value})"
            )
        return distance

    def _unpack_distance(self, packed: int) -> int:
        """
        Unpack a distance value from storage.

        Args:
            packed: Packed value

        Returns:
            Distance value
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
        self.data[index] = packed_dist

    def get_distance(self, index: int) -> int:
        """
        Get the distance for a given state index.

        Args:
            index: State index in the pattern database

        Returns:
            Minimum distance to solve this state
        """
        if index < 0 or index >= self.size:
            raise ValueError(f"Index {index} out of range [0, {self.size})")

        packed = int(self.data[index])
        if packed == self.uninitialized_value:
            raise ValueError(f"Distance at index {index} is uninitialized")
        return self._unpack_distance(packed)

    def is_initialized(self, index: int) -> bool:
        """
        Check if a state has been initialized (distance set).

        Args:
            index: State index

        Returns:
            True if distance has been set, False if still uninitialized
        """
        if index < 0 or index >= self.size:
            raise ValueError(f"Index {index} out of range [0, {self.size})")
        return int(self.data[index]) != self.uninitialized_value

    def copy_storage_from(self, other: 'PatternDatabase') -> None:
        """
        Copy serialized storage state from another pattern database instance.

        This is used when loading a base `PatternDatabase` from disk and
        reconstructing a concrete subclass wrapper.
        """
        if self.size != other.size:
            raise ValueError(f"Size mismatch: expected {self.size}, got {other.size}")

        self.storage_format = other.storage_format
        self.uninitialized_value = other.uninitialized_value
        self.data = other.data.copy()
        self.max_depth = other.max_depth
        self.states_at_depth = dict(other.states_at_depth)

    def initialized_count(self) -> int:
        """
        Return the number of states with initialized distances.

        Pattern databases built through the repository track a depth histogram,
        which is the cheapest source of truth. Fall back to scanning the array
        only when that metadata is unavailable.
        """
        if self.states_at_depth:
            return int(sum(int(v) for v in self.states_at_depth.values()))
        return int(np.count_nonzero(self.data != self.uninitialized_value))

    def is_complete(self) -> bool:
        """Return True when distances have been generated for every state."""
        return self.initialized_count() == self.size

    def save(self, filepath: str) -> None:
        """
        Save the pattern database to disk.

        Args:
            filepath: Path to save the database
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data_dict = {
            'format_version': self.FORMAT_VERSION,
            'name': self.name,
            'size': self.size,
            'storage_format': self.storage_format,
            'uninitialized_value': self.uninitialized_value,
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

        if data_dict.get('format_version') == cls.FORMAT_VERSION:
            db.storage_format = data_dict['storage_format']
            db.uninitialized_value = int(data_dict['uninitialized_value'])
            db.data = data_dict['data']
            db.max_depth = data_dict['max_depth']
            db.states_at_depth = data_dict['states_at_depth']
            return db

        db._load_legacy_nibble_payload(data_dict)

        return db

    def _load_legacy_nibble_payload(self, data_dict: Dict) -> None:
        """
        Load the original nibble-packed format when it is provably safe to convert.

        Legacy payloads are accepted only when we can show they do not rely on the
        ambiguous nibble value 15 and that every state has been initialized.
        """
        legacy_data = data_dict['data']
        decoded = np.full(self.size, self.BYTE_UNINITIALIZED, dtype=np.uint8)

        for index in range(self.size):
            byte_idx = index // 2
            if index % 2 == 0:
                decoded[index] = legacy_data[byte_idx] & 0x0F
            else:
                decoded[index] = (legacy_data[byte_idx] >> 4) & 0x0F

        initialized_count = sum(int(v) for v in data_dict.get('states_at_depth', {}).values())
        if initialized_count != self.size:
            raise ValueError(
                "Legacy pattern database is incomplete and cannot be upgraded safely. "
                "Regenerate it with the exact-safe storage format."
            )

        if data_dict.get('max_depth', 0) >= 15 or np.any(decoded == 15):
            raise ValueError(
                "Legacy nibble-packed pattern database may contain ambiguous distance 15 values. "
                "Regenerate it with the exact-safe storage format."
            )

        self.storage_format = self.STORAGE_FORMAT_BYTE
        self.uninitialized_value = int(self.BYTE_UNINITIALIZED)
        self.data = decoded
        self.max_depth = data_dict['max_depth']
        self.states_at_depth = data_dict['states_at_depth']

    def get_statistics(self) -> Dict:
        """
        Get statistics about the pattern database.

        Returns:
            Dictionary with statistics
        """
        return {
            'name': self.name,
            'size': self.size,
            'storage_format': self.storage_format,
            'max_depth': self.max_depth,
            'states_at_depth': self.states_at_depth,
            'initialized_states': self.initialized_count(),
            'complete': self.is_complete(),
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
