# Phase 5: Distance Estimator Implementation

## Overview

This implementation provides a comprehensive distance estimation system for Rubik's Cube states, combining pattern databases with multiple heuristic approaches. The system estimates the minimum number of moves required to solve a cube from any given state.

## Implemented Features

### 1. Pattern Databases

Pattern databases store exact minimum distances for subsets of the cube:

- **Corner Database**: Tracks all 8 corners (position + orientation)
  - State space: 8! × 3^7 = 88,179,840 states
  - Memory: ~44 MB (using nibble compression)
  - Maximum depth: ~11-12 moves

- **Edge Databases** (Two 6-edge groups):
  - Edge Group 1: UR, UF, UL, UB, DR, DF
  - Edge Group 2: DL, DB, FR, FL, BL, BR
  - State space per group: ~645,120 states
  - Memory: ~0.3 MB each

**Why split edges?** A full 12-edge database would require ~500GB of memory, making it impractical. Following Korf's approach, we split edges into two independent groups.

### 2. Multiple Heuristics

The system implements three classic heuristics:

- **Manhattan Distance**: Sum of individual piece distances, divided by 4 for admissibility
  - Most accurate heuristic without pattern databases
  - Considers geometric distance on the cube

- **Hamming Distance**: Count of misplaced pieces, divided by 8
  - Simple and fast
  - Counts pieces in wrong positions/orientations

- **Simple Heuristic**: Face-based color matching, divided by 8
  - Basic approach
  - Higher scores for more similar faces

### 3. Combined Distance Estimation

The final estimate uses: **max(corner_db, edge1_db, edge2_db)**

This strategy:
- Maintains admissibility (never overestimates)
- Provides the tightest lower bound
- Is proven effective in Korf's original work

## Code Structure

```
src/korf/
├── pattern_database.py      # Base pattern database infrastructure
├── corner_database.py        # Corner pattern database
├── edge_database.py          # Edge pattern databases (2 groups)
├── heuristics.py             # Manhattan, Hamming, simple heuristics
├── distance_estimator.py     # Main estimator combining all methods
├── validation.py             # Accuracy testing and validation
└── __init__.py               # Module exports
```

## Usage Examples

### Basic Usage (Heuristics Only)

```python
from src.cube.rubik_cube import RubikCube
from src.korf import create_estimator

# Create estimator without pattern databases
estimator = create_estimator(load_databases=False)

# Scramble a cube
cube = RubikCube()
cube.scramble(20)

# Estimate distance
distance = estimator.estimate(cube, method='manhattan')
print(f"Estimated distance: {distance}")
```

### Using Pattern Databases

```python
from src.korf import create_estimator

# Load or generate pattern databases
# Note: Generation takes significant time!
estimator = create_estimator(
    load_databases=True,
    generate_if_missing=True  # Will generate if not found
)

# Estimate using pattern databases
cube = RubikCube()
cube.scramble(15)

distance = estimator.estimate(cube, method='pattern_db')
print(f"Pattern DB estimate: {distance}")
```

### Comparing All Methods

```python
# Get detailed comparison
details = estimator.estimate_detailed(cube)

print(f"Pattern DB: {details['pattern_db']}")
print(f"Manhattan:  {details['heuristics']['manhattan']}")
print(f"Hamming:    {details['heuristics']['hamming']}")
print(f"Simple:     {details['heuristics']['simple']}")
```

### Accuracy Evaluation

```python
from src.korf.validation import create_test_dataset, AccuracyEvaluator

# Create test dataset
dataset = create_test_dataset(seed=42)

# Evaluate accuracy
evaluator = AccuracyEvaluator(estimator)
results = evaluator.evaluate(dataset)

# Print results
evaluator.compare_methods(dataset)
```

## Performance Metrics

### Accuracy (on test dataset)

**Manhattan Distance Heuristic:**
- Mean Absolute Error: ~4.6 moves
- RMSE: ~7.0 moves
- Exact predictions: 22.2%
- Best at short distances (1-5 moves)

**Pattern Databases** (when available):
- Expected MAE: ~2-3 moves (based on literature)
- Significantly better than heuristics alone
- Tightest admissible lower bound

### Memory Usage

- Corner DB: 44 MB
- Edge1 DB: 0.3 MB
- Edge2 DB: 0.3 MB
- **Total: ~45 MB**

### Generation Time

Pattern database generation (approximate):
- Corner DB: 10-20 minutes (88M states)
- Edge DBs: 1-2 minutes each (645K states)
- **Total: ~15-25 minutes**

## Key Implementation Details

### 1. Lexicographic Indexing

We use permutation-to-rank conversion for perfect hashing:

```python
def corner_index(cubie: CubieCube) -> int:
    perm = get_corner_permutation(cubie)  # 0 to 40,319
    orient = get_corner_orientation(cubie)  # 0 to 2,186
    return perm * 2187 + orient  # Combined index
```

### 2. Nibble Compression

Distances are stored in 4 bits (nibbles) instead of bytes:
- Supports distances 0-15
- 2x memory savings
- Sufficient for Rubik's Cube (God's number = 20)

### 3. BFS Generation

Pattern databases are generated using breadth-first search from the solved state:

```python
def bfs_generate_pattern_database(db, index_func, move_func, solved_index):
    queue = [(solved_index, 0)]
    db.set_distance(solved_index, 0)

    while queue:
        state_idx, depth = queue.popleft()
        for move in ALL_MOVES:
            new_idx = move_func(state_idx, move)
            if not visited(new_idx):
                db.set_distance(new_idx, depth + 1)
                queue.append((new_idx, depth + 1))
```

## Theoretical Background

### Admissibility

A heuristic h(n) is admissible if: **h(n) ≤ h*(n)** (never overestimates)

Our implementations ensure admissibility by:
- Dividing sum heuristics by pieces affected per move (4 or 8)
- Using max() for combining pattern databases
- Pattern databases are inherently admissible (exact distances for subsets)

### Why max() for Combining Databases?

Given independent pattern databases for disjoint piece sets:
- h(n) = max(h₁(n), h₂(n), h₃(n)) is admissible
- h(n) ≤ h*(n) because solving any subset ≤ solving the whole cube
- max() gives the tightest bound among the databases

### Comparison to Alternatives

**vs. Additive Pattern Databases:**
- Additive PDBs can be more accurate but require disjoint move sets
- Not applicable to Rubik's Cube (all moves affect all pieces)

**vs. AI Search Heuristics:**
- Pattern databases provide exact distances for subsets
- Far superior to geometric heuristics like Manhattan distance
- Essential for optimal solving (IDA* with PDBs)

## Testing

Run the comprehensive test suite:

```bash
# Unit tests
pytest tests/unit/test_distance_estimator.py -v

# Run demo
python demos/distance_estimator_demo.py

# Generate and test with pattern databases (slow!)
python demos/distance_estimator_demo.py --generate-dbs
```

Test coverage:
- ✓ Pattern database infrastructure (nibble packing, indexing)
- ✓ Corner database indexing
- ✓ Edge database indexing
- ✓ All heuristic functions
- ✓ Distance estimator integration
- ✓ Admissibility verification
- ✓ Consistency checks

## Validation Results

### Test Dataset Performance

Generated dataset with scrambles at distances 1, 2, 3, 4, 5, 7, 10, 15, 20:

**Manhattan Distance:**
```
Distance  1: MAE=0.70  (70% of actual)
Distance  5: MAE=1.30  (26% of actual)
Distance 10: MAE=6.05  (60% of actual)
Distance 20: MAE=16.12 (80% of actual)
```

Pattern databases expected to significantly reduce these errors.

## References

1. **Korf, R. E. (1997)**. "Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"
   - Original pattern database approach
   - Corner + edge database split strategy

2. **Culberson, J. & Schaeffer, J. (1998)**. "Pattern Databases"
   - Theoretical foundations
   - Compression techniques

3. **Stack Overflow Discussions**:
   - Pattern database creation: https://stackoverflow.com/q/58860280
   - Heuristic admissibility: https://stackoverflow.com/q/60130124
   - General heuristics: https://stackoverflow.com/q/36490073

4. **cube20.org**: Positions with known optimal distances
   - God's Number = 20 (Rokicki et al., 2010)
   - Distance-20 position dataset

5. **BenSDuggan/CubeAI**: Reference implementation
   - Multiple heuristic approaches
   - Manhattan distance for 3D cubes

## Future Enhancements

Potential improvements for future work:

1. **Disjoint Pattern Databases**
   - More sophisticated grouping strategies
   - Higher accuracy with same memory

2. **Symmetry Reduction**
   - Exploit cube symmetries (48-fold)
   - Reduce database size by ~48x

3. **Differential Heuristics**
   - Refine estimates during search
   - Better pruning in IDA*

4. **GPU Acceleration**
   - Parallel BFS generation
   - Faster database creation

5. **Compressed Pattern Databases**
   - Further compression beyond nibbles
   - Trade computation for memory

## License

Part of the Rubik's Cube Master's Thesis project.
University of Patras, 2024.
