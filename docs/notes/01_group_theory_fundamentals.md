# Group Theory Fundamentals for Rubik's Cube

## Overview

The Rubik's Cube is a perfect example of group theory in action. Understanding the mathematical structure helps us develop efficient solving algorithms.

## What is a Group?

A **group** (G, *) is a set G with a binary operation * that satisfies:

1. **Closure**: For all a, b ∈ G, a * b ∈ G
2. **Associativity**: For all a, b, c ∈ G, (a * b) * c = a * (b * c)
3. **Identity**: There exists e ∈ G such that a * e = e * a = a for all a ∈ G
4. **Inverse**: For all a ∈ G, there exists a⁻¹ ∈ G such that a * a⁻¹ = a⁻¹ * a = e

## The Rubik's Cube Group

The Rubik's Cube forms a **permutation group** where:

- **Elements**: All possible cube configurations (positions)
- **Operation**: Applying moves (face rotations)
- **Identity**: The solved state
- **Inverses**: Reverse moves (e.g., R and R')

### Properties

1. **Group Order**: The Rubik's Cube group has approximately 4.3 × 10¹⁹ elements
   - Precise: 43,252,003,274,489,856,000 positions

2. **Generators**: Six basic moves {U, D, F, B, L, R} generate the entire group
   - Any position can be reached using combinations of these moves

3. **Subgroups**: The cube has many interesting subgroups used in solving
   - G₀: All legal cube positions (full group)
   - G₁: Edge orientation corrected
   - G₂: Edge orientation + corner orientation corrected
   - G₃: Edge and corner tetrads in correct slices
   - G₄: Solved state

## Key Concepts for Cube Solving

### 1. Permutations

The cube state can be represented as:
- 8 corner cubies with 3 orientations each
- 12 edge cubies with 2 orientations each

**Corner permutations**: 8! = 40,320 ways
**Corner orientations**: 3⁷ = 2,187 ways (last corner determined by others)
**Edge permutations**: 12! = 479,001,600 ways
**Edge orientations**: 2¹¹ = 2,048 ways (last edge determined by others)

Total: (8! × 3⁷ × 12! × 2¹¹) / 2 = 43,252,003,274,489,856,000

The division by 2 is due to the parity constraint.

### 2. Parity Constraints

**Theorem**: Not all combinations of permutations and orientations are legal.

Two important constraints:
1. **Permutation parity**: Corner and edge permutations must have the same parity
2. **Orientation constraints**:
   - Sum of corner orientations ≡ 0 (mod 3)
   - Sum of edge orientations ≡ 0 (mod 2)

These constraints reduce the theoretical (8! × 3⁸ × 12! × 2¹²) positions by a factor of 12.

### 3. Commutators

A **commutator** [A, B] = A B A' B' is a powerful tool for creating algorithms.

**Property**: Commutators affect only a small portion of the cube while leaving most unchanged.

**Example**: [R, U] = R U R' U'
- Affects only a few cubies
- Returns many pieces to original positions
- Used to construct targeted algorithms

### 4. Conjugates

A **conjugate** of move sequence A by setup S is: S A S'

**Usage**:
- Move problematic pieces into a favorable position (S)
- Apply a known algorithm (A)
- Undo the setup (S')

**Example**: To apply R U R' U' to a different corner, use conjugates.

## God's Number

**God's Number** is the maximum number of moves required to solve any cube position using an optimal algorithm.

**Result** (Rokicki et al., 2010): God's number is **20** in the half-turn metric (HTM).
- Any scrambled cube can be solved in ≤ 20 face turns
- Some positions actually require 20 moves (20f*)

**Diameter of Cayley Graph**: The cube group's Cayley graph has diameter 20.

## Cayley Graphs

A **Cayley graph** visualizes a group:
- **Vertices**: Group elements (cube positions)
- **Edges**: Generators (moves like R, U, F, etc.)
- **Paths**: Move sequences

**Properties**:
- The shortest path from identity to any node = optimal solution length
- Distance metric for heuristic functions
- Diameter = God's number

## Cosets and Subgroups

**Coset**: Given subgroup H ⊆ G and element g ∈ G:
- Left coset: gH = {gh | h ∈ H}
- Right coset: Hg = {hg | h ∈ H}

**Application in Solving**:
- Thistlethwaite's algorithm uses nested subgroups G₀ ⊃ G₁ ⊃ G₂ ⊃ G₃ ⊃ G₄
- Each phase reduces the cube state to a smaller coset
- G₄ = {e} (solved state)

## Distance Metrics

Two main metrics for counting moves:

### 1. Half-Turn Metric (HTM)
- Each face turn (90° or 180°) counts as one move
- R, R', R2 all count as 1 move
- God's number: 20 (HTM)

### 2. Quarter-Turn Metric (QTM)
- Each 90° turn counts as one move
- R and R' count as 1 move
- R2 counts as 2 moves
- God's number: 26 (QTM)

## Important Theorems

### Theorem 1: Legal State Characterization
A cube state is legal if and only if:
1. Corner permutation parity = Edge permutation parity
2. Σ(corner orientations) ≡ 0 (mod 3)
3. Σ(edge orientations) ≡ 0 (mod 2)

### Theorem 2: Impossible to Swap Two Pieces
You cannot swap just two corners or just two edges without affecting anything else.
- Minimum: 3-cycle (swap 3 pieces)

### Theorem 3: Quarter Turns Suffice
The six quarter turns {U, D, F, B, L, R} (90° clockwise) are sufficient to generate the entire group. Prime and double moves can be expressed as combinations.

## Applications to Algorithm Design

### 1. Thistlethwaite's Algorithm (1981)
- Uses subgroup sequence: G₀ → G₁ → G₂ → G₃ → G₄
- Each phase restricts moves to maintain previous constraints
- Guarantees ≤ 52 moves (original), improved to ≤ 45 moves

### 2. Kociemba's Algorithm (1992)
- Two-phase approach
- Phase 1: Reduce to subgroup H (edge orientation + E-slice)
- Phase 2: Solve within H using only U, D, F2, B2, L2, R2
- Average ~20 moves, very fast

### 3. Korf's Algorithm (1997)
- IDA* search with pattern database heuristics
- Guaranteed optimal solutions
- Multiple pattern databases for different cubie subsets
- Uses additive heuristics (multiple DBs)

## Pattern Databases

**Concept**: Pre-compute optimal distances for subsets of pieces.

**Example Patterns**:
- Corner pattern: States of all 8 corners (ignoring edges)
- Edge pattern: States of specific edges (ignoring others)

**Heuristic**: h(state) = max(h_corners(state), h_edges(state))
- Admissible: Never overestimates
- Used in A* and IDA* search

## Macro Operations

**Macro**: A sequence of moves achieving a specific goal.

**Properties**:
- Moves only a few pieces
- Preserves most of the cube
- Composed from commutators and conjugates

**Example Macros**:
- 3-cycle of corners: (R U R' U') × 5
- Edge flip: (M' U M' U M' U M' U) × 2

## Key Takeaways

1. The Rubik's Cube is a permutation group with ~4.3 × 10¹⁹ elements
2. Only certain combinations are legal (parity constraints)
3. Any position can be solved in ≤ 20 moves (God's number)
4. Subgroups enable efficient staged solving (Thistlethwaite, Kociemba)
5. Pattern databases provide admissible heuristics for optimal search
6. Commutators and conjugates are fundamental for building algorithms

## References

1. **MIT SP.268 Course Notes**: Group theory and Rubik's Cube
   - https://web.mit.edu/sp.268/www/rubik.pdf

2. **Harvard Notes**: Chen's Group Theory and Rubik's Cube
   - http://people.math.harvard.edu/~jjchen/docs/Group%20Theory%20and%20the%20Rubik's%20Cube.pdf

3. **UC Berkeley**: Hutching's Rubik's Cube notes
   - http://math.berkeley.edu/~hutching/rubik.pdf

4. **Rokicki et al. (2010)**: "Diameter of the Rubik's Cube Group is 20"
   - Proved God's number is 20

5. **Wikipedia**: Rubik's Cube Group Theory
   - https://en.wikipedia.org/wiki/Rubik%27s_Cube_group

## Further Study

- Study Cayley graphs and their properties
- Explore coset enumeration techniques
- Investigate pattern database construction
- Learn about bidirectional search methods
- Research symmetry reduction techniques
