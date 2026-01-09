# Chapter 05: Korf IDA* Algorithm - Detailed Specification

**Title (Greek):** Αλγόριθμος Korf IDA*
**Goal:** Present optimal Rubik's Cube solving using IDA* with pattern databases
**Target:** ~2,500 words (8-10 pages with figures and code examples)
**Key takeaway:** Korf's algorithm guarantees optimal solutions but has exponential time complexity, making it practical only for shallow scrambles

---

## Section 5.1: Algorithm Overview (~400 words)

### 5.1.1 Historical Context (~150 words)

**Points to Cover:**
1. Richard Korf's 1997 breakthrough: first optimal solver for random Rubik's Cube states
2. Pattern database innovation: precomputed heuristics for admissible search
3. Significance: proved random cubes solvable in median 18 moves

**Citations:**
- `\cite{korf1997finding}` - Original paper
- `\cite{korf2002disjoint}` - Disjoint pattern databases

### 5.1.2 IDA* Foundation (~250 words)

**Points to Cover:**
1. Iterative Deepening A*: combines A*'s heuristic guidance with DFS memory efficiency
2. Memory complexity: O(d) vs A*'s O(b^d)
3. Trade-off: re-expands nodes but avoids memory explosion
4. Admissibility requirement: h(n) ≤ h*(n) guarantees optimality

**Code References:**
- `src/korf/a_star.py:271-443` - IDAStarSolver class
- `src/korf/a_star.py:312-352` - Main solve() method
- `src/korf/a_star.py:354-416` - Recursive _search() implementation

**Citations:**
- `\cite{korf1985depth}` - IDA* original paper
- `\cite{korf2001timecomplexity}` - Time complexity analysis

---

## Section 5.2: Pattern Databases (~600 words)

### 5.2.1 Corner Pattern Database (~250 words)

**Points to Cover:**
1. State space: 8! × 3⁷ = 40,320 × 2,187 = 88,179,840 states
2. Index computation: `index = corner_perm_rank × 3^7 + corner_orientation`
3. Maximum distance: 11-12 moves
4. Memory: ~44 MB (with nibble compression)

**Code References:**
- `src/korf/corner_database.py:34-35` - Size calculation
- `src/korf/corner_database.py:38-59` - `corner_index()` function
- `src/korf/corner_database.py:108-162` - CornerPatternDatabase class

### 5.2.2 Edge Pattern Databases (~250 words)

**Points to Cover:**
1. Split design rationale: full 12-edge DB would require ~500GB
2. Two 6-edge databases: 6! × 2⁵ = 720 × 32 = 23,040 states each
3. Edge groups: Group 1 (0-5: UR, UF, UL, UB, DR, DF), Group 2 (6-11: DL, DB, FR, FL, BL, BR)
4. Combined memory: ~488 MB

**Code References:**
- `src/korf/edge_database.py:271-273` - EDGE_GROUP_1, EDGE_GROUP_2
- `src/korf/edge_database.py:128-150` - `edge_index()` method
- `src/korf/edge_database.py:276-331` - `create_edge_database()`

### 5.2.3 BFS Generation (~100 words)

**Points to Cover:**
1. Backward BFS from solved state
2. Record minimum distance at each coordinate
3. Progress reporting and persistence

**Code References:**
- `src/korf/pattern_database.py:211-282` - `bfs_generate_pattern_database()`

**Figure:** BFS layer diagram showing distance distribution

---

## Section 5.3: Nibble Compression (~300 words)

### 5.3.1 Storage Optimization (~300 words)

**Points to Cover:**
1. Two distances per byte (4 bits each)
2. Range 0-15 sufficient for Rubik's Cube distances (max ~20)
3. 50% memory reduction compared to byte storage
4. Bitwise operations for packing/unpacking

**Code References:**
- `src/korf/pattern_database.py:45-48` - Data structure initialization
- `src/korf/pattern_database.py:78-97` - `set_distance()` nibble packing
- `src/korf/pattern_database.py:99-121` - `get_distance()` nibble unpacking

**Table 5.1: Database Size Comparison**
| Database | States | Uncompressed | Compressed |
|----------|--------|--------------|------------|
| Corner | 88.2M | ~88 MB | ~44 MB |
| Edge 1 | 23K | ~23 KB | ~11.5 KB |
| Edge 2 | 23K | ~23 KB | ~11.5 KB |

---

## Section 5.4: Heuristic Functions (~500 words)

### 5.4.1 Basic Heuristics (~200 words)

**Points to Cover:**
1. **Simple heuristic:** misplaced_stickers / 8
2. **Hamming distance:** misplaced_pieces / 8
3. **Manhattan distance:** max(corner_dist, edge_dist) / 4
4. All admissible but vary in tightness

**Code References:**
- `src/korf/heuristics.py:28-59` - `simple_heuristic()`
- `src/korf/heuristics.py:62-94` - `hamming_distance()`
- `src/korf/heuristics.py:97-192` - Manhattan distance functions

### 5.4.2 Pattern Database Heuristics (~150 words)

**Points to Cover:**
1. Direct lookup of precomputed distances
2. Combination: `h = max(h_corner, h_edge1, h_edge2)`
3. Admissibility proof: each component ≤ h*, so max ≤ h*

**Code References:**
- `src/korf/distance_estimator.py:162-190` - `estimate_from_pattern_dbs()`

### 5.4.3 Composite Heuristic (Research Contribution) (~150 words)

**Points to Cover:**
1. Adaptive strategy based on state entropy
2. Near-solved states: use fast Manhattan
3. Deep scrambles: use pattern databases
4. Mid-range: balanced maximum combination

**Code References:**
- `src/korf/composite_heuristic.py:123-351` - CompositeHeuristic class
- `src/korf/composite_heuristic.py:158-194` - Adaptive `__call__()` method
- `src/korf/composite_heuristic.py:39-120` - StateAnalyzer class

**Figure:** Heuristic comparison chart

---

## Section 5.5: IDA* Implementation (~500 words)

### 5.5.1 Main Algorithm (~250 words)

**Points to Cover:**
1. Initialize bound = h(start)
2. Iteratively increase bound when search fails
3. Return optimal solution when goal found

**Pseudocode:**
```
function ida_star(start):
    bound = h(start)
    while bound <= max_depth:
        result = search(start, 0, bound)
        if result is solution: return result
        if result is infinity: return failure
        bound = result  // new minimum bound
    return failure
```

**Code References:**
- `src/korf/a_star.py:312-352` - IDAStarSolver.solve()

### 5.5.2 Recursive Search (~250 words)

**Points to Cover:**
1. f = g + h(current)
2. If f > bound: return f (for next iteration's bound)
3. If goal: return solution path
4. Try all moves with pruning, track minimum

**Code References:**
- `src/korf/a_star.py:354-416` - `_search()` recursive method

---

## Section 5.6: Pruning Strategies (~300 words)

### 5.6.1 Redundant Move Pruning (~200 words)

**Points to Cover:**
1. Same-face sequences: U U' = identity
2. Canonical ordering: U before D, F before B, L before R
3. Branching reduction: ~30% fewer nodes

**Code References:**
- `src/korf/a_star.py:418-431` - `_is_redundant_move()`

### 5.6.2 Heuristic Pruning (~100 words)

**Points to Cover:**
1. If g + h > bound: prune branch
2. Tighter heuristics = more pruning
3. Pattern databases provide strongest pruning

---

## Section 5.7: A* Comparison (~300 words)

### 5.7.1 A* Implementation (~150 words)

**Points to Cover:**
1. Priority queue ordered by f = g + h
2. Open/closed sets for duplicate detection
3. Memory bound checking

**Code References:**
- `src/korf/a_star.py:51-269` - AStarSolver class

### 5.7.2 IDA* vs A* Trade-offs (~150 words)

**Table 5.2: Algorithm Comparison**
| Aspect | A* | IDA* |
|--------|-----|------|
| Memory | O(b^d) | O(d) |
| Optimality | Yes | Yes |
| Duplicate detection | Yes | No |
| Node re-expansion | No | Yes |
| Practical for Rubik's | No | Yes |

**Code References:**
- `src/korf/solver_comparison.py` - SolverComparison framework

---

## Section 5.8: Performance Analysis (~300 words)

### 5.8.1 Complexity Analysis (~150 words)

**Points to Cover:**
1. Time: O(b^d) where b ≈ 13.5 effective branching factor
2. Memory: O(d) for path storage
3. Exponential growth explains timeout at depth > 10

**Citations:**
- `\cite{korf2001timecomplexity}` - Formal analysis
- `\cite{demaine2018npcomplete}` - NP-completeness

### 5.8.2 Practical Limitations (~150 words)

**Points to Cover:**
1. Depth 5: ~96% success, 6.5s average
2. Depth 10: ~40-52% success, 102s average
3. Depth 15+: <5% success (timeout)
4. PyPy vs CPython: ~40× speedup with PyPy

**Code References:**
- `src/korf/optimal_solver.py:8-16` - Performance notes

---

## Section 5.9: Summary and Evaluation (~200 words)

**Key Findings:**
1. Korf guarantees optimal solutions when successful
2. Practical only for scramble depths ≤ 8-10
3. Pattern databases provide strongest heuristics
4. Valuable for verification and theoretical analysis

**Trade-offs:**
- Optimality guarantee vs computation time
- Memory efficiency vs node re-expansion
- Heuristic quality vs generation time

**Transition to Chapter 6:**
"The effectiveness of Korf's algorithm depends critically on heuristic quality. Chapter 6 explores heuristic design and the composite heuristic approach in detail."

---

## Writing Checklist

### Figures
- [ ] Figure 5.1: IDA* iterative bound expansion
- [ ] Figure 5.2: Pattern database BFS generation
- [ ] Figure 5.3: Nibble compression diagram
- [ ] Figure 5.4: Heuristic comparison chart
- [ ] Figure 5.5: A* vs IDA* memory profiles
- [ ] Figure 5.6: Branching factor vs depth

### Tables
- [ ] Table 5.1: Database Size Comparison
- [ ] Table 5.2: A* vs IDA* Algorithm Comparison
- [ ] Table 5.3: Heuristic Accuracy Comparison

### Citations
- [ ] `\cite{korf1997finding}` - Original algorithm
- [ ] `\cite{korf1985depth}` - IDA*
- [ ] `\cite{korf2001timecomplexity}` - Complexity
- [ ] `\cite{korf2002disjoint}` - Disjoint PDBs
- [ ] `\cite{demaine2018npcomplete}` - NP-completeness
- [ ] `\cite{culberson1998pattern}` - Pattern database survey

### Cross-References
- [ ] Chapter 2 (Background) for A*/IDA* foundations
- [ ] Chapter 4 (Kociemba) for practical comparison
- [ ] Chapter 6 (Heuristics) for detailed heuristic analysis
- [ ] Chapter 7 (Evaluation) for benchmark results
- [ ] Chapter 9 (Conclusions) for composite heuristic contribution
