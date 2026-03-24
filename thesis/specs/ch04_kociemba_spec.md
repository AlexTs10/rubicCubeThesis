# Chapter 04: Kociemba Algorithm - Detailed Specification

**Title (Greek):** Αλγόριθμος Kociemba
**Goal:** Present the two-phase optimal-seeking algorithm with pruning tables
**Target:** ~2,500 words (8-10 pages with figures and code examples)
**Key takeaway:** Kociemba achieves the best balance of speed and solution quality through efficient coordinate systems and precomputed pruning tables

---

## Section 4.1: Algorithm Overview (~400 words)

### 4.1.1 Historical Context (~150 words)

**Points to Cover:**
1. Herbert Kociemba's 1992 algorithm: refinement of Thistlethwaite
2. Two-phase approach: reduced from four phases
3. Near-optimal solutions in practice, with runtime depending on the scramble and backend

**Citations:**
- `\cite{kociemba1992close}` - Original algorithm
- `\cite{kociemba_twophase_details}` - Modern implementation notes

### 4.1.2 Two-Phase Structure (~250 words)

**Points to Cover:**
1. Phase 1: G₀ → G₁ (orient pieces, place UD-slice edges) - 2.2 billion states
2. Phase 2: G₁ → Solved (complete solution within G₁) - tens of billions of theoretical states before pruning
3. Total theoretical max: 12 + 18 = 30 moves (practical: ~22 average)

**Table 4.1: Phase Comparison**
| Phase | State Space | Max Depth | Allowed Moves |
|-------|-------------|-----------|---------------|
| 1 | 2.2 × 10⁹ | 12 | All 18 |
| 2 | 3.9 × 10¹⁰ | 18 | 10 (U, U', U2, D, D', D2, F2, B2, L2, R2) |

**Code References:**
- `src/kociemba/solver.py:31-449` - KociembaSolver class
- `src/kociemba/solver.py:79-187` - Main solve() method
- `src/kociemba/moves.py:31-35` - PHASE1_MOVES, PHASE2_MOVES

---

## Section 4.2: Coordinate Systems (~600 words)

### 4.2.1 Phase 1 Coordinates (~300 words)

**Points to Cover:**
1. **Corner Orientation (CO):** 0-2186 (3⁷ = 2,187 states)
   - Base-3 encoding of 7 corner twists (8th determined by parity)
2. **Edge Orientation (EO):** 0-2047 (2¹¹ = 2,048 states)
   - Binary encoding of 11 edge flips (12th determined by parity)
3. **UD-Slice Position (UDS):** 0-494 (C(12,4) = 495 states)
   - Combination rank: which 4 positions contain slice edges

**Code References:**
- `src/kociemba/coord.py:150-166` - `get_corner_orientation()`
- `src/kociemba/coord.py:186-202` - `get_edge_orientation()`
- `src/kociemba/coord.py:222-249` - `get_udslice()`

### 4.2.2 Phase 2 Coordinates (~300 words)

**Points to Cover:**
1. **Corner Permutation (CP):** 0-40319 (8! = 40,320 states)
   - Lexicographic rank of corner positions
2. **Edge Permutation (EP):** 0-40319 (8! for U/D edges only)
   - Lexicographic rank of U/D edge positions (0-7)
3. **UD-Slice Permutation (UDSP):** 0-23 (4! = 24 states)
   - Permutation of the 4 slice edges within slice positions

**Code References:**
- `src/kociemba/coord.py:282-295` - `get_corner_permutation()`
- `src/kociemba/coord.py:309-326` - `get_edge_permutation()`
- `src/kociemba/coord.py:341-358` - `get_udslice_permutation()`

**Figure:** Coordinate system diagram showing all 6 coordinates

---

## Section 4.3: Move Tables (~500 words)

### 4.3.1 Table Structure (~250 words)

**Points to Cover:**
1. Precomputed transitions: table[coordinate][move] = new_coordinate
2. O(1) coordinate updates during search
3. Generation via brute-force simulation of moves on representative states

**Table 4.2: Move Table Dimensions**
| Coordinate | Phase | Dimension | Memory |
|------------|-------|-----------|--------|
| Corner Orientation | 1 | [2187][18] | ~39 KB |
| Edge Orientation | 1 | [2048][18] | ~37 KB |
| UD-Slice | 1 | [495][18] | ~9 KB |
| Corner Permutation | 2 | [40320][10] | ~403 KB |
| Edge Permutation | 2 | [40320][10] | ~403 KB |
| UD-Slice Permutation | 2 | [24][10] | ~240 B |

**Code References:**
- `src/kociemba/moves.py:38-266` - MoveTables class
- `src/kociemba/moves.py:110-149` - `_generate_tables()`
- `src/kociemba/moves.py:151-183` - `_generate_coord_table()`

### 4.3.2 Transition Functions (~250 words)

**Points to Cover:**
1. Phase 1: `apply_move_to_coords(co, eo, us, move)` - returns new (CO, EO, UDS)
2. Phase 2: `apply_move_to_phase2_coords(cp, ep, sp, move)` - returns new (CP, EP, UDSP)
3. Index computation: `move_idx = ALL_MOVE_NAMES.index(move)`

**Code References:**
- `src/kociemba/moves.py:185-213` - `apply_move_to_coords()`
- `src/kociemba/moves.py:215-246` - `apply_move_to_phase2_coords()`

---

## Section 4.4: Pruning Tables (~500 words)

### 4.4.1 BFS Construction (~250 words)

**Points to Cover:**
1. Backward BFS from goal state (all coordinates = 0)
2. Records minimum move distance at each coordinate combination
3. Tables provide admissible lower bounds for IDA*

**Code References:**
- `src/kociemba/pruning.py:31-303` - PruningTables class
- `src/kociemba/pruning.py:124-157` - Phase 1 CO-EO table generation
- `src/kociemba/pruning.py:159-192` - Phase 1 EO-Slice table generation
- `src/kociemba/pruning.py:194-247` - Phase 2 single-coordinate tables

### 4.4.2 Table Specifications (~250 words)

**Table 4.3: Pruning Table Dimensions**
| Table | Phase | Size | Purpose |
|-------|-------|------|---------|
| phase1_co_eo | 1 | [2187 × 2048] | Corner × Edge orientation |
| phase1_eo_slice | 1 | [2048 × 495] | Edge orientation × UD-slice |
| phase2_cp | 2 | [40320] | Corner permutation |
| phase2_ep | 2 | [40320] | Edge permutation |
| phase2_sp | 2 | [24] | Slice permutation |

**Memory Estimate:** roughly 6 MB for the raw serialized pruning tables, with higher process memory once loaded into Python objects

**Heuristic Functions:**
- Phase 1: `h = max(phase1_co_eo[co,eo], phase1_eo_slice[eo,uds])`
- Phase 2: `h = max(phase2_cp[cp], phase2_ep[ep], phase2_sp[sp])`

**Code References:**
- `src/kociemba/pruning.py:249-274` - `get_phase1_heuristic()`
- `src/kociemba/pruning.py:276-302` - `get_phase2_heuristic()`

**Citations:**
- `\cite{korf1997finding}` - Pattern database principles
- `\cite{korf2002disjoint}` - Max vs additive heuristics

---

## Section 4.5: IDA* Search (~500 words)

### 4.5.1 Phase 1 Search (~250 words)

**Points to Cover:**
1. Goal: CO = 0, EO = 0, UDS = 0
2. All 18 moves allowed
3. Iterative deepening with pruning table heuristic

**Code References:**
- `src/kociemba/solver.py:189-244` - `_solve_phase1()`
- `src/kociemba/solver.py:246-318` - `_phase1_ida_search()` recursive implementation
- `src/kociemba/solver.py:280-281` - Phase 1 goal test

**Pseudocode:**
```
function solve_phase1(cubie, max_depth, timeout):
    co, eo, us = extract_coordinates(cubie)
    for depth in 0..max_depth:
        result = ida_search(co, eo, us, depth, [], null)
        if result is solution: return result
    return failure
```

### 4.5.2 Phase 2 Search (~250 words)

**Points to Cover:**
1. Goal: CP = 0, EP = 0, SP = 0
2. Only 10 moves allowed (restricted to preserve Phase 1 invariants)
3. Starts from state after Phase 1 solution applied

**Code References:**
- `src/kociemba/solver.py:320-377` - `_solve_phase2()`
- `src/kociemba/solver.py:379-449` - `_phase2_ida_search()`
- `src/kociemba/solver.py:413-414` - Phase 2 goal test

---

## Section 4.6: Redundancy Pruning (~300 words)

### 4.6.1 Move Sequence Pruning (~300 words)

**Points to Cover:**
1. **Same-face pruning:** U followed by U' or U2 is redundant
2. **Opposite-face ordering:**
   - Phase 1: U before D, F before B, L before R
   - Phase 2: U before D, L before R only (F, B, L, R are all double moves)
3. Reduces branching factor significantly

**Code References:**
- `src/kociemba/solver.py:294-302` - Phase 1 redundancy check
- `src/kociemba/solver.py:428-433` - Phase 2 redundancy check

**Figure:** Search tree diagram showing pruned branches

---

## Section 4.7: Cubie Representation (~400 words)

### 4.7.1 CubieCube Class (~200 words)

**Points to Cover:**
1. Corner representation: `corner_perm[8]` (positions) + `corner_orient[8]` (twists 0-2)
2. Edge representation: `edge_perm[12]` (positions) + `edge_orient[12]` (flips 0-1)
3. Move composition via `multiply()` method

**Code References:**
- `src/kociemba/cubie.py:30-114` - CubieCube class
- `src/kociemba/cubie.py:63-91` - `multiply()` method

### 4.7.2 Facelet Conversion (~200 words)

**Points to Cover:**
1. `from_facelet_cube()`: Convert 54-facelet state to cubie representation
2. `to_facelet_cube()`: Convert back for display/verification
3. Error handling for invalid configurations

**Code References:**
- `src/kociemba/cubie.py:231-352` - `from_facelet_cube()`
- `src/kociemba/cubie.py:355-422` - `to_facelet_cube()`

---

## Section 4.8: Summary and Evaluation (~200 words)

**Key Findings:**
1. Kociemba achieves 100% success rate in the current thesis corpus
2. Runtime varies by scramble depth and backend, but remains practical
3. Solutions remain close to optimal in practice
4. Best practical algorithm for real-time applications

**Performance Characteristics:**
- Time: depends on scramble depth and solver backend
- Solution length: 5-22 moves typical in the thesis corpus
- Memory: modest to moderate, depending on whether you count raw tables or loaded runtime objects

**Transition to Chapter 5:**
"While Kociemba produces near-optimal solutions efficiently, Korf's IDA* algorithm with pattern databases guarantees truly optimal solutions, trading computation time for solution quality."

---

## Writing Checklist

### Figures
- [ ] Figure 4.1: Two-phase algorithm flow diagram
- [ ] Figure 4.2: Coordinate system visualization (6 coordinates)
- [ ] Figure 4.3: Move table lookup diagram
- [ ] Figure 4.4: Pruning table BFS construction
- [ ] Figure 4.5: IDA* search tree with pruning
- [ ] Figure 4.6: CubieCube representation diagram

### Tables
- [ ] Table 4.1: Phase Comparison
- [ ] Table 4.2: Move Table Dimensions
- [ ] Table 4.3: Pruning Table Dimensions

### Citations
- [ ] `\cite{kociemba1992close}` - Original algorithm
- [ ] `\cite{kociemba_twophase_details}` - Modern implementation
- [ ] `\cite{korf1997finding}` - Pattern databases
- [ ] `\cite{korf2002disjoint}` - Heuristic combination
- [ ] `\cite{korf1985depth}` - IDA* algorithm

### Cross-References
- [ ] Chapter 2 (Background) for cubie representation basics
- [ ] Chapter 3 (Thistlethwaite) for four-phase comparison
- [ ] Chapter 5 (Korf) for optimal solving contrast
- [ ] Chapter 6 (Heuristics) for pruning table theory
- [ ] Chapter 7 (Evaluation) for benchmark results
