# Chapter 03: Thistlethwaite Algorithm - Detailed Specification

**Title (Greek):** Αλγόριθμος Thistlethwaite
**Goal:** Present the four-phase nested subgroup algorithm for Rubik's Cube solving
**Target:** ~2,500 words (8-10 pages with figures and code examples)
**Key takeaway:** Thistlethwaite demonstrates how group theory constraints enable systematic cube solving through progressive move restrictions

---

## Section 3.1: Algorithm Overview (~400 words)

### 3.1.1 Historical Context (~150 words)

**Points to Cover:**
1. Morwen Thistlethwaite's 1981 breakthrough: first algorithm to guarantee sub-50 move solutions
2. Group-theoretic approach: nested subgroups G₀ ⊃ G₁ ⊃ G₂ ⊃ G₃ ⊃ G₄
3. Historical significance: precursor to Kociemba's two-phase algorithm

**Citations:**
- `\cite{thistlethwaite1981}` - Original algorithm paper
- `\cite{joyner2008adventures}` - Group theory perspective

### 3.1.2 Algorithm Structure (~250 words)

**Points to Cover:**
1. Four-phase reduction approach: each phase restricts allowed moves
2. Invariant preservation: once achieved, properties are maintained
3. Move progression: 18 → 14 → 8 → 6 moves across phases

**Table 3.1: Phase Overview**
| Phase | Subgroup Transition | Moves | State Space | Goal |
|-------|---------------------|-------|-------------|------|
| 0 | G₀ → G₁ | 18 | 2,048 | Orient all edges |
| 1 | G₁ → G₂ | 14 | 1,082,565 | Orient corners + E-slice |
| 2 | G₂ → G₃ | 8 | 70 | Tetrad + parity |
| 3 | G₃ → G₄ | 6 | 40,320 | Fully solve |

**Code References:**
- `src/thistlethwaite/solver.py:22-350` - ThistlethwaiteSolver class
- `src/thistlethwaite/solver.py:67-195` - Main solve() method
- `src/thistlethwaite/moves.py:13-59` - Phase move definitions

---

## Section 3.2: Phase 0 - Edge Orientation (~400 words)

### 3.2.1 Mathematical Foundation (~200 words)

**Points to Cover:**
1. Edge orientation: each edge has 2 possible states (0 = correct, 1 = flipped)
2. Coordinate space: 2¹¹ = 2,048 (12th edge determined by parity)
3. Goal: all edges correctly oriented relative to face colors

**Figure:** Edge orientation diagram showing flip states

**Code References:**
- `src/thistlethwaite/coordinates.py:257-271` - `get_edge_orientation_coord()`
- `src/thistlethwaite/coordinates.py:273-275` - `count_misoriented_edges()`

### 3.2.2 Implementation Details (~200 words)

**Points to Cover:**
1. All 18 moves allowed in Phase 0
2. F, F', B, B', L, L', R, R' quarter-turns affect edge orientation
3. Pattern database: 2,048 entries, max depth 7 moves

**Code References:**
- `src/thistlethwaite/moves.py:13-20` - PHASE_0_MOVES
- `src/thistlethwaite/tables.py:160-183` - Phase 0 database initialization
- `src/thistlethwaite/solver.py:284-289` - Phase 0 goal check

**Citations:**
- `\cite{bandelow1982inside}` - Edge mechanics

---

## Section 3.3: Phase 1 - Corner Orientation and E-Slice (~500 words)

### 3.3.1 Corner Orientation (~200 words)

**Points to Cover:**
1. Corner twist: 3 states per corner (0, 1, 2 representing 0°, 120°, 240° rotation)
2. Coordinate: 3⁷ = 2,187 states (8th corner determined by sum mod 3)
3. F, F', B, B' quarter-turns change corner orientation

**Code References:**
- `src/thistlethwaite/coordinates.py:278-291` - `get_corner_orientation_coord()`

### 3.3.2 E-Slice Positioning (~200 words)

**Points to Cover:**
1. E-slice: the middle layer containing 4 edges (FR, FL, BL, BR)
2. Goal: place these 4 edges in E-slice positions (not necessarily permuted correctly)
3. Coordinate: C(12,4) = 495 states (which 4 of 12 positions contain E-slice edges)

**Code References:**
- `src/thistlethwaite/coordinates.py:297-317` - `get_e_slice_coord()`
- `src/thistlethwaite/coordinates.py:319-327` - `count_e_slice_misplacements()`

### 3.3.3 Combined Coordinate (~100 words)

**Points to Cover:**
1. Combined state space: 2,187 × 495 ≈ 1.08 million states
2. Pattern database encodes both invariants: `coord = co * 495 + es`
3. Moves restricted: F, F', B, B' removed (only F2, B2 allowed)

**Code References:**
- `src/thistlethwaite/moves.py:26-33` - PHASE_1_MOVES (14 moves)
- `src/thistlethwaite/tables.py:185-215` - Phase 1 database (1,082,565 entries)
- `src/thistlethwaite/solver.py:291-300` - Phase 1 goal check

---

## Section 3.4: Phase 2 - Tetrad and Parity (~500 words)

### 3.4.1 Corner Tetrad Constraint (~200 words)

**Points to Cover:**
1. Tetrad: partition of 8 corners into two groups of 4
   - Tetrad 1: UFL, UFR, DFL, DFR (indices 0, 1, 4, 5)
   - Tetrad 2: UBL, UBR, DBL, DBR (indices 3, 2, 7, 6)
2. Goal: corners within same tetrad must occupy tetrad positions
3. Coordinate: C(8,4) = 70 states

**Code References:**
- `src/thistlethwaite/coordinates.py:330-356` - `get_corner_tetrad_coord()`

### 3.4.2 UD-Edge Slicing (~150 words)

**Points to Cover:**
1. UD-edges (positions 0-7) must remain in UD-layer positions
2. Ensures edges don't cross into E-slice after Phase 1
3. Combined with tetrad constraint for Phase 2 goal

**Code References:**
- `src/thistlethwaite/coordinates.py:370-381` - `get_edge_slice_coord()`

### 3.4.3 Parity Constraint (~150 words)

**Points to Cover:**
1. Corner permutation parity must equal edge permutation parity
2. This constraint enables Phase 3's restricted move set
3. Quarter-turns change parity; double-turns preserve it

**Code References:**
- `src/thistlethwaite/coordinates.py:393-397` - `has_even_parity()`
- `src/thistlethwaite/coordinates.py:80-98` - `permutation_parity()`
- `src/thistlethwaite/moves.py:39-46` - PHASE_2_MOVES (8 moves: only L2, R2 instead of L, L', R, R')

---

## Section 3.5: Phase 3 - Final Solve (~400 words)

### 3.5.1 Restricted Move Set (~200 words)

**Points to Cover:**
1. Only 6 double moves allowed: U2, D2, F2, B2, L2, R2
2. These preserve all previous phase invariants
3. Quarter-turns would break orientation and parity constraints

**Code References:**
- `src/thistlethwaite/moves.py:52-59` - PHASE_3_MOVES

### 3.5.2 Permutation Coordinate (~200 words)

**Points to Cover:**
1. Corner permutation: 8! = 40,320 states
2. Edge permutation: 12! ≈ 479 million (too large for full PDB)
3. Implementation uses corner-only PDB for tractability

**Code References:**
- `src/thistlethwaite/coordinates.py:408-415` - `get_corner_permutation_coord()`
- `src/thistlethwaite/tables.py:244-269` - Phase 3 database (40,320 entries)
- `src/thistlethwaite/solver.py:311-315` - Phase 3 goal: `cube.is_solved()`

---

## Section 3.6: Pattern Database Construction (~400 words)

### 3.6.1 BFS Generation (~200 words)

**Points to Cover:**
1. Backward BFS from solved state (coordinate 0)
2. Expand with phase-allowed moves, record depth at each new coordinate
3. Progress tracking at 100K node intervals

**Code References:**
- `src/thistlethwaite/tables.py:57-103` - BFS generation
- `src/thistlethwaite/tables.py:19-142` - PatternDatabase class

### 3.6.2 Database Specifications (~200 words)

**Table 3.2: Pattern Database Sizes**
| Phase | Coordinate | Size | Max Depth | Memory |
|-------|------------|------|-----------|--------|
| 0 | Edge orientation | 2,048 | 7 | ~2 KB |
| 1 | Corner orient × E-slice | 1,082,565 | 10 | ~1 MB |
| 2 | Corner tetrad | 70 | 13 | ~70 B |
| 3 | Corner permutation | 40,320 | 15 | ~40 KB |

**Code References:**
- `src/thistlethwaite/tables.py:145-324` - ThistlethwaitePatternDatabases class
- `src/thistlethwaite/tables.py:271-301` - `load_all()` method

**Citations:**
- `\cite{korf1997finding}` - Pattern database methodology
- `\cite{culberson1998pattern}` - Pattern database survey

---

## Section 3.7: IDA* Search per Phase (~400 words)

### 3.7.1 Search Algorithm (~200 words)

**Points to Cover:**
1. IDA* iterative deepening with pattern database heuristic
2. Phase-specific goal checks and move sets
3. Timeout handling per phase (10s, 30s, 60s, 120s)

**Code References:**
- `src/thistlethwaite/ida_star.py:13-184` - IDAStarSearch class
- `src/thistlethwaite/ida_star.py:49-89` - Main search loop
- `src/thistlethwaite/ida_star.py:91-152` - Recursive search

### 3.7.2 Redundant Move Pruning (~200 words)

**Points to Cover:**
1. Same-face sequences (e.g., U followed by U') are redundant
2. Opposite-face ordering (U before D) enforces canonical paths
3. Reduces branching factor significantly

**Code References:**
- `src/thistlethwaite/ida_star.py:154-184` - `_is_redundant_move()`

**Citations:**
- `\cite{korf1985depth}` - IDA* algorithm

---

## Section 3.8: Summary and Evaluation (~200 words)

**Key Findings:**
1. Thistlethwaite guarantees solutions but typically 30+ moves
2. Four-phase structure is deterministic and reliable
3. Educational value in demonstrating group theory concepts
4. Slower than modern algorithms (Kociemba, Korf)

**Transition to Chapter 4:**
"The Kociemba algorithm reduces Thistlethwaite's four phases to two, achieving significantly faster solving times while maintaining near-optimal solution lengths."

---

## Writing Checklist

### Figures
- [ ] Figure 3.1: Subgroup chain diagram (Hasse diagram G₀ → G₁ → G₂ → G₃ → G₄)
- [ ] Figure 3.2: Edge orientation states (0 vs 1)
- [ ] Figure 3.3: Corner orientation states (0, 1, 2)
- [ ] Figure 3.4: E-slice position diagram
- [ ] Figure 3.5: Tetrad partition visualization
- [ ] Figure 3.6: Phase move restriction progression

### Tables
- [ ] Table 3.1: Phase Overview
- [ ] Table 3.2: Pattern Database Sizes

### Citations
- [ ] `\cite{thistlethwaite1981}` - Original algorithm
- [ ] `\cite{joyner2008adventures}` - Group theory
- [ ] `\cite{bandelow1982inside}` - Cube mechanics
- [ ] `\cite{korf1985depth}` - IDA*
- [ ] `\cite{korf1997finding}` - Pattern databases
- [ ] `\cite{culberson1998pattern}` - PDB survey

### Cross-References
- [ ] Chapter 2 (Background) for group theory foundations
- [ ] Chapter 4 (Kociemba) for two-phase comparison
- [ ] Chapter 6 (Heuristics) for pattern database details
- [ ] Chapter 7 (Evaluation) for benchmark results
