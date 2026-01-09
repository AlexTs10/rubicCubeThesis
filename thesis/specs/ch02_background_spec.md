# Chapter 02: Theoretical Background - Detailed Specification

**Title (Greek):** Θεωρητικό Υπόβαθρο
**Goal:** Establish mathematical and computational foundations for Rubik's Cube solving algorithms
**Target:** ~2,500 words (8-10 pages with figures and code examples)
**Key takeaway:** Understanding cube representation, group theory constraints, and search algorithm fundamentals is essential for implementing efficient solvers

---

## Section 2.1: Cube Representation (~600 words)

### 2.1.1 Facelet-Based Representation (~250 words)

**Points to Cover:**
1. 6 faces: U (Up/White), D (Down/Yellow), F (Front/Green), B (Back/Blue), L (Left/Orange), R (Right/Red)
2. Each face has 9 facelets indexed 0-8 with standard indexing pattern
3. State representation as 6×9 array of color indices
4. Singmaster Notation: U, D, F, B, L, R (and U', U2, etc.)

**Code References:**
- `src/cube/rubik_cube.py:lines 28-55` - Face and Color enumerations
- `src/cube/rubik_cube.py:lines 97-118` - Face rotation implementation
- `src/cube/rubik_cube.py:lines 185-227` - Singmaster move parsing

**Citations:**
- `\cite{singmaster1981notes}` - Standard notation definition
- `\cite{bandelow1982inside}` - Cube mechanics and terminology

### 2.1.2 Cubie-Level Representation (~200 words)

**Points to Cover:**
1. 8 corner pieces (cubies): URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB
2. 12 edge pieces: UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR
3. Position (0-7 or 0-11) + Orientation (corners: 0-2, edges: 0-1)

**Code References:**
- `src/kociemba/cubie.py:CubieCube` class (lines 30-61)
- `src/kociemba/cubie.py:lines 120-212` - Move definitions

**Citations:**
- `\cite{joyner2008adventures}` - Group theory perspective
- `\cite{kociemba1992close}` - Cubie model for two-phase solving

### 2.1.3 Conversion Between Representations (~150 words)

**Code References:**
- `src/kociemba/cubie.py:from_facelet_cube()` (lines 231-352)
- `src/kociemba/cubie.py:to_facelet_cube()` (lines 355-422)

---

## Section 2.2: Group Theory Foundations (~700 words)

### 2.2.1 Permutation Groups (~250 words)

**Points to Cover:**
1. Rubik's Cube configuration space forms a mathematical group G
2. 18 generators: U, D, F, B, L, R and their inverses/doubles
3. Group size: |G| = 43,252,003,274,489,856,000 ≈ 4.3 × 10^19 states
4. Parity constraint: corner permutation parity must equal edge permutation parity

**Code References:**
- `src/thistlethwaite/coordinates.py:permutation_parity()` (lines 80-98)
- `src/kociemba/cubie.py:multiply()` (lines 63-91)

**Citations:**
- `\cite{joyner2008adventures}` - Comprehensive group theory treatment
- `\cite{chen2005grouptheory}` - Mathematical structure

### 2.2.2 Subgroups and Cosets (~250 words)

**Points to Cover:**
1. Thistlethwaite's Group Chain: G₀ ⊂ G₁ ⊂ G₂ ⊂ G₃ ⊂ G₄ ⊂ G
2. Each phase restricts allowed moves while maintaining invariants
3. Lagrange's Theorem: |H| × |G/H| = |G|

**Citations:**
- `\cite{daniels2008grouptheory}` - Formal treatment
- `\cite{thistlethwaite1981}` - Original paper

### 2.2.3 God's Number and Computational Bounds (~200 words)

**Points to Cover:**
1. God's Number = 20: maximum moves needed to solve any configuration
2. NP-completeness of optimal solving (Demaine et al. 2018)
3. Historical progression: 1981 (45 moves) → 2010 (20 moves)

**Citations:**
- `\cite{rokicki2010gods}` - God's Number is 20
- `\cite{rokicki2014diameter}` - Formal proof
- `\cite{demaine2018npcomplete}` - NP-completeness

---

## Section 2.3: Search Algorithms (~700 words)

### 2.3.1 A* Algorithm Fundamentals (~250 words)

**Points to Cover:**
1. Best-first search using f(n) = g(n) + h(n)
2. Admissibility: h(n) ≤ h*(n) (heuristic never overestimates)
3. Why A* fails for Rubik's Cube: memory explosion

**Code References:**
- `src/korf/a_star.py:AStarSolver` (lines 51-216)

**Citations:**
- `\cite{hart1968formal}` - Foundational A* paper
- `\cite{russell2020artificial}` - Modern textbook treatment

### 2.3.2 IDA* and Memory-Bounded Search (~250 words)

**Points to Cover:**
1. Combines iterative deepening with A* heuristic
2. Memory efficiency: O(d) vs A*'s O(b^d)
3. Trade-off: re-expands nodes multiple times

**Code References:**
- `src/korf/a_star.py:IDAStarSolver` (lines 271-442)

**Citations:**
- `\cite{korf1985depth}` - Original IDA* paper
- `\cite{korf2001timecomplexity}` - Time complexity analysis

### 2.3.3 Pattern Databases and Heuristics (~200 words)

**Points to Cover:**
1. Pre-computed table of optimal distances for cube subsets
2. Built using BFS backward from solved state
3. Disjoint pattern databases for additive heuristics

**Code References:**
- `src/korf/pattern_database.py:PatternDatabase` (lines 26-77)

**Citations:**
- `\cite{korf1997finding}` - Original pattern database paper
- `\cite{culberson1998pattern}` - Pattern database survey
- `\cite{korf2002disjoint}` - Disjoint pattern databases

---

## Section 2.4: Integration and Key Takeaways (~500 words)

### 2.4.1 Representation-Algorithm Mapping (~200 words)

**Table 2.1: Representation Characteristics**
| Aspect | Facelet | Cubie |
|--------|---------|-------|
| State dimensions | 48 facelets | 8+12 pieces |
| Computation speed | Slower | Faster |
| Group theory fit | Indirect | Direct |

### 2.4.2 Mathematical Constraints in Practice (~200 words)

- Parity constraint implementation
- Subgroup exploitation in Thistlethwaite
- God's Number as stopping criterion

### 2.4.3 Preview of Algorithm Chapters (~100 words)

- Chapter 3: Thistlethwaite (4-phase)
- Chapter 4: Kociemba (2-phase)
- Chapter 5: Korf IDA* (optimal)

---

## Writing Checklist

### Figures
- [ ] Facelet indexing diagram (0-8 numbering per face)
- [ ] Singmaster move notation visual
- [ ] Cubie numbering diagram
- [ ] Subgroup chain diagram (Hasse diagram style)
- [ ] A* search tree with f/g/h values
- [ ] IDA* threshold progression diagram
- [ ] Pattern database construction (BFS layers)

### Tables
- [ ] Table 2.1: Representation Characteristics
- [ ] Table 2.2: Subgroup Sizes and Reduction Factors
- [ ] Table 2.3: Algorithm Time/Space Complexity

### Citations
- [ ] `\cite{singmaster1981notes}` - Notation
- [ ] `\cite{joyner2008adventures}` - Group theory
- [ ] `\cite{rokicki2010gods}` - God's Number
- [ ] `\cite{demaine2018npcomplete}` - NP-completeness
- [ ] `\cite{hart1968formal}` - A* algorithm
- [ ] `\cite{korf1985depth}` - IDA* algorithm
- [ ] `\cite{korf1997finding}` - Pattern databases

### Cross-References
- [ ] Chapter 3 (Thistlethwaite)
- [ ] Chapter 4 (Kociemba)
- [ ] Chapter 5 (Korf)
- [ ] Chapter 6 (Heuristics)
