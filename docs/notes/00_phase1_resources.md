# Phase 1: Foundation & Setup - Resource Guide

## Overview

This document tracks Phase 1 resources and learning materials for understanding the mathematical and practical foundations of Rubik's Cube solving algorithms.

**Phase Duration**: Weeks 1-2
**Completion Status**: ✓ COMPLETED

## Phase 1 Tasks

### ✓ Task 1: Set up development environment
- [x] Create project structure
- [x] Set up Python virtual environment
- [x] Install dependencies (requirements.txt)
- [x] Verify setup with test script

**Verification**: Run `python verify_setup.py`

### ✓ Task 2: Study group theory basics
- [x] Read MIT SP.268 Course Notes (pages 1-15)
- [x] Study Harvard Group Theory notes
- [x] Review UC Berkeley handout on commutators
- [x] Create group theory fundamentals document

**Documentation**: See `01_group_theory_fundamentals.md`

### ✓ Task 3: Understand cube representation
- [x] Implement facelet-based cube representation
- [x] Implement state copying and comparison
- [x] Create visualization utilities
- [x] Write comprehensive tests

**Implementation**: See `src/cube/rubik_cube.py` and `src/cube/visualization.py`

### ✓ Task 4: Learn Singmaster notation
- [x] Master basic moves (U, D, F, B, L, R)
- [x] Learn modifiers (', 2)
- [x] Study advanced notation (M, E, S, wide moves)
- [x] Create notation reference guide

**Documentation**: See `02_singmaster_notation.md`

## Key Learning Resources

### Group Theory Fundamentals

#### 📄 MIT SP.268 Course Notes
**URL**: https://web.mit.edu/sp.268/www/rubik.pdf

**Key Topics** (pages 1-15):
- Permutation groups and basic group theory
- The Rubik's Cube as a group
- Order of the cube group: ~4.3 × 10¹⁹
- Cayley graphs and diameter
- Subgroups and cosets

**Important Concepts**:
- Group axioms: closure, associativity, identity, inverse
- Generators: {U, D, F, B, L, R} generate entire group
- God's number: 20 moves (half-turn metric)

#### 📄 Harvard Notes by Janet Chen
**URL**: http://people.math.harvard.edu/~jjchen/docs/Group%20Theory%20and%20the%20Rubik's%20Cube.pdf

**Key Topics**:
- Bounds for solving the cube
- Parity constraints:
  - Corner permutation parity = Edge permutation parity
  - Sum of corner orientations ≡ 0 (mod 3)
  - Sum of edge orientations ≡ 0 (mod 2)
- Legal vs illegal cube states
- Why you can't swap just two pieces

**Critical Formula**:
```
Total positions = (8! × 3⁷ × 12! × 2¹¹) / 2
                = 43,252,003,274,489,856,000
```

#### 📄 UC Berkeley Handout by Michael Hutchings
**URL**: http://math.berkeley.edu/~hutching/rubik.pdf

**Key Topics**:
- Commutators: [A, B] = A B A' B'
- Conjugates: S A S'
- How to construct macros using commutators
- Building targeted algorithms

**Practical Application**:
- Commutators affect only small portions of the cube
- Used to create algorithms that solve specific pieces
- Foundation for advanced solving techniques

### Notation Systems

#### 🌐 Singmaster Notation Guide (Ruwix)
**URL**: https://ruwix.com/the-rubiks-cube/notation/

**Master These Moves**:
- **Basic**: U, D, F, B, L, R (90° clockwise)
- **Prime**: U', D', F', B', L', R' (90° counter-clockwise)
- **Double**: U2, D2, F2, B2, L2, R2 (180°)

**Total**: 18 basic moves (6 faces × 3 modifiers)

**Interactive Features**:
- Visual demonstrations of each move
- Animated cube showing move effects
- Practice sequences

#### 🌐 Speedsolving Wiki - Advanced Notation
**URL**: https://www.speedsolving.com/wiki/index.php/Notation

**Advanced Notation**:
- **Slice moves**: M, E, S (middle layers)
  - M: Middle (between L and R), follows L direction
  - E: Equatorial (between U and D), follows D direction
  - S: Standing (between F and B), follows F direction

- **Wide moves**: Fw, Rw, Uw, etc. (two layers)
  - Rw = R + M'
  - Uw = U + E'
  - Fw = F + S

- **Cube rotations**: x, y, z
  - x: Rotate entire cube like R
  - y: Rotate entire cube like U
  - z: Rotate entire cube like F

**Note**: Our Phase 1 implementation focuses on basic 18 moves. Advanced moves will be added in later phases if needed.

### Background Reading

#### 📖 Wikipedia - Rubik's Cube
**URL**: https://en.wikipedia.org/wiki/Rubik%27s_Cube

**Focus Sections**:
- **Structure**: Physical construction and mechanics
- **Mathematics**:
  - Number of permutations
  - Group theory interpretation
  - Parity constraints
- **History**: Invention and worldwide impact

**Key Facts**:
- Invented by Ernő Rubik in 1974
- Originally called "Magic Cube"
- Best-selling puzzle in history
- World record: ~3 seconds (human), < 0.4 seconds (robot)

#### 📖 Wikipedia - Optimal Solutions
**URL**: https://en.wikipedia.org/wiki/Optimal_solutions_for_Rubik%27s_Cube

**Major Algorithms Covered**:
1. **Thistlethwaite (1981)**: ≤ 52 moves, uses nested subgroups
2. **Kociemba (1992)**: ~20 moves average, two-phase approach
3. **Korf (1997)**: Optimal solutions using IDA* and pattern databases
4. **Optimal solvers**: God's number proof (Rokicki et al., 2010)

**Distance Metrics**:
- **Half-Turn Metric (HTM)**: Each face turn counts as 1
  - God's number: 20
- **Quarter-Turn Metric (QTM)**: Each 90° turn counts as 1
  - God's number: 26

## Implementation Checklist

### Core Cube Representation ✓

- [x] Face enumeration (U, D, F, B, L, R)
- [x] Color enumeration (W, Y, G, B, O, R)
- [x] State representation (6 faces × 9 facelets)
- [x] Solved state initialization
- [x] State copying and comparison
- [x] Hash function for use in sets/dicts

**File**: `src/cube/rubik_cube.py:58`

### Move Implementation ✓

- [x] Basic moves: U, D, F, B, L, R
- [x] Prime moves: U', D', F', B', L', R'
- [x] Double moves: U2, D2, F2, B2, L2, R2
- [x] Move sequence parsing
- [x] Move sequence application

**File**: `src/cube/rubik_cube.py:119-226`

### Move Utilities ✓

- [x] Inverse move calculation
- [x] Inverse sequence calculation
- [x] Move sequence simplification
- [x] Move sequence parsing
- [x] Move sequence formatting

**File**: `src/cube/moves.py`

### Visualization ✓

- [x] Text-based cube display
- [x] Colored terminal output (ANSI)
- [x] 2D unfolded net visualization
- [x] Compact state representation
- [x] Face-by-face display
- [x] Side-by-side comparison
- [x] HTML visualization (for Jupyter)

**File**: `src/cube/visualization.py`

### Testing ✓

- [x] Cube initialization tests
- [x] Basic move tests
- [x] Move sequence tests
- [x] Inverse operation tests
- [x] Scrambling tests
- [x] Edge case handling

**File**: `tests/unit/test_rubik_cube.py`

**Run tests**: `pytest tests/unit/test_rubik_cube.py -v`

### Demos ✓

- [x] Basic usage demonstration
- [x] Move sequence examples
- [x] Scrambling examples
- [x] Visualization examples

**File**: `demos/basic_usage.py`

**Run demo**: `python demos/basic_usage.py`

## Key Concepts Mastered

### 1. Group Theory
- [x] Understand the cube as a permutation group
- [x] Know the group order: ~4.3 × 10¹⁹
- [x] Understand generators and group generation
- [x] Grasp parity constraints
- [x] Understand subgroups and cosets

### 2. Notation
- [x] Master Singmaster notation (18 basic moves)
- [x] Understand move inverses
- [x] Parse and format move sequences
- [x] Know advanced notation (for future phases)

### 3. Representation
- [x] Facelet-based representation
- [x] State encoding as numpy array
- [x] Efficient state copying
- [x] State hashing for search

### 4. Visualization
- [x] Multiple display modes
- [x] Colored terminal output
- [x] Unfolded net display
- [x] Ready for Jupyter notebooks

## Next Phase Preview

**Phase 2: Thistlethwaite's Algorithm (Weeks 3-4)**

**Prerequisites from Phase 1**:
- ✓ Cube representation
- ✓ Move implementation
- ✓ Group theory understanding
- ✓ Subgroup concepts

**What's Coming**:
1. Define subgroups G₀ ⊃ G₁ ⊃ G₂ ⊃ G₃ ⊃ G₄
2. Implement phase transition checks
3. Build lookup tables for each phase
4. Implement breadth-first search for each phase
5. Combine phases into complete solver

**Reading**:
- Thistlethwaite's original paper
- Detailed subgroup definitions
- Move restrictions per phase

## Verification

### Run Setup Verification
```bash
python verify_setup.py
```

**Expected**: All 7 checks should pass
1. ✓ Python Version (>= 3.10)
2. ✓ Required Packages
3. ✓ Project Structure
4. ✓ Core Functionality
5. ✓ Test Suite
6. ✓ Demo Script
7. ✓ Documentation

### Quick Functionality Test
```python
from src.cube.rubik_cube import RubikCube
from src.cube.visualization import show

# Create and display solved cube
cube = RubikCube()
show(cube)

# Apply moves
cube.apply_move_sequence("R U R' U'")
show(cube)

# Scramble
cube = RubikCube()
moves = cube.scramble(moves=20, seed=42)
print(f"Scramble: {' '.join(moves)}")
show(cube)
```

## Additional Resources

### Books
- **"Notes on Rubik's Magic Cube"** by David Singmaster (1981)
  - Original notation system
  - Basic solving methods

- **"Metamagical Themas"** by Douglas Hofstadter (1985)
  - Chapter on Rubik's Cube
  - Mathematical and philosophical aspects

### Papers
- **Rokicki et al. (2010)**: "Diameter of the Rubik's Cube Group is 20"
  - Proof that God's number is 20
  - Computational methods

- **Korf (1997)**: "Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"
  - IDA* algorithm
  - Pattern database heuristics

### Online Communities
- **Speedsolving.com**: Forums for cubers and algorithm developers
- **Reddit r/Cubers**: Active community for all skill levels
- **YouTube**: Tutorials for visualization and understanding

## Phase 1 Completion Checklist

- [x] Development environment set up and verified
- [x] All dependencies installed
- [x] Project structure created
- [x] Core cube implementation complete
- [x] All 18 basic moves working
- [x] Comprehensive test suite passing
- [x] Visualization module complete
- [x] Demo script working
- [x] Group theory fundamentals studied and documented
- [x] Singmaster notation mastered and documented
- [x] Setup verification script created
- [x] Ready to proceed to Phase 2

**Status**: ✓ Phase 1 COMPLETE - Ready for Thistlethwaite implementation!
