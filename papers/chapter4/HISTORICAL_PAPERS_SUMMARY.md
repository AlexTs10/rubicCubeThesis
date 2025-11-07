# Historical Rubik's Cube Algorithm Papers - Research Summary

## Overview
This directory contains historical documentation and references for seminal Rubik's Cube solving algorithms developed between 1980 and 2010.

## Papers and Resources Downloaded

### 1. Kociemba's God's Number Proof (2010)
**File**: `Kociemba_Gods_Number_Is_20.pdf`
**Source**: https://kociemba.org/math/papers/rubik20.pdf
**Authors**: Tomas Rokicki, Herbert Kociemba, Morley Davidson, John Dethridge
**Publication**: SIAM Journal on Discrete Mathematics (Volume 27, Issue 2)
**Significance**: This is the definitive proof that God's Number is 20 - the minimum number of moves required to solve any Rubik's Cube configuration.
**Contribution**: Completed the computational proof of optimal solution bounds that took decades of incremental improvements.

### 2. Thistlethwaite Algorithm Documentation
**File**: `Heise_Human_Thistlethwaite_Algorithm.html`
**Source**: https://www.ryanheise.com/cube/human_thistlethwaite_algorithm.html
**Author**: Ryan Heise (human variant of Thistlethwaite's computer algorithm)
**Original Algorithm**: Morwen Thistlethwaite (1980)
**Significance**: Documents the four-group reduction strategy that became foundational to modern cube solving algorithms.

**Algorithm Overview**:
- Phase 1: Orient edges, move U/D pieces to U/D layers, orient corners
- Phase 2: Move edges into correct slices and position corners
- Phase 3: Fine-tune edge and corner positions
- Phase 4: Final positioning

**Maximum Moves**: Original algorithm achieved 52 moves, later improved to 45-50 moves
**Innovation**: Breaking the problem into manageable subgroups using group theory fundamentals

### 3. Wikipedia: Optimal Solutions for Rubik's Cube
**File**: `Wikipedia_Optimal_Solutions_Rubiks_Cube.html`
**Source**: https://en.wikipedia.org/wiki/Optimal_solutions_for_the_Rubik%27s_Cube
**Comprehensive Reference**: Covers notation, lower bounds, and algorithm evolution
**Key Information**: Detailed timeline of upper bound improvements from 1980 to 2010

### 4. Kociemba's Two-Phase Algorithm Documentation
**Source**: https://kociemba.org/twophase.htm and related mathematical pages
**Significance**: Herbert Kociemba's improvement combining phases of Thistlethwaite's algorithm

**Algorithm Innovation (1992)**:
- Reduced Thistlethwaite's four phases to just two phases
- Phase 1: Get edges oriented, U/D pieces to their layers, corners oriented
- Phase 2: Solve the cube within the constrained group
- Claimed maximum of 21 moves (later verified at 20 moves)

**Publication**: "Close to God's algorithm" - Cubism For Fun, Vol. 28, 1992, pp. 10-13

## Historical Timeline of Algorithm Development

### 1980: Thistlethwaite's Algorithm
- **Achievement**: Reduced upper bound to 52 moves
- **Method**: Four-group reduction strategy
- **Significance**: Pioneering use of group theory for optimal solving

### 1990: Kloosterman's Improvement
- **Achievement**: 42 moves maximum
- **Method**: Refined Thistlethwaite's phases
- **Key Innovation**: Combined and optimized phase transitions

### 1992: Kociemba's "Close to God's Algorithm"
- **Achievement**: 21 moves claimed (later proven to be 20)
- **Method**: Two-phase algorithm combining multiple phases
- **Innovation**: Dramatic reduction from four phases to two
- **Publication Venue**: Cubism For Fun (Dutch Cube Club magazine)

### 1992: Dik Winter's Calculation
- **Achievement**: 37 moves maximum
- **Method**: Extensive phase-1 computation of Kociemba's algorithm
- **Impact**: Provided practical bounds for implementation

### 1995-2010: Incremental Improvements
- Mike Reid: 39 → 29 moves (1992-1995)
- Silviu Radu: 28 → 27 moves (2005-2006)
- Daniel Kunkle & Gene Cooperman: 26 moves (2007)
- Rokicki et al.: 25 → 23 → 22 moves (2008)
- **Final Proof**: 20 moves (July 2010)

## Key Concepts Explained

### Group Theory Application
All these algorithms use the mathematical concept of cosets and group theory to progressively constrain the solution space:
- Start with the full group of possible cube states
- Reduce to manageable subgroups after each phase
- Use pruning tables and move tables to guide search

### Move Metrics
- **HTM (Half-Turn Metric)**: A 180° turn counts as 1 move (used for Kociemba's algorithm)
- **QTM (Quarter-Turn Metric)**: A 180° turn counts as 2 moves
- God's Number is 20 in HTM, higher in QTM

### Upper vs Lower Bounds
- **Upper Bound**: Maximum moves needed (proven by finding solving algorithm)
- **Lower Bound**: Minimum possible based on permutation group size
- Meeting these bounds proves the exact optimal distance

## Online Resources Referenced

1. **Kociemba's Homepage**: https://kociemba.org/
   - Cube Explorer software (Windows)
   - Two-phase algorithm documentation
   - Mathematical papers and proofs
   - Download section with implementations

2. **Jaap's Puzzle Site**: https://www.jaapsch.net/puzzles/thistle.htm
   - Thistlethwaite's original algorithm documentation
   - Note: Currently experiencing SSL certificate issues

3. **Cubing History**: https://www.cubinghistory.com/3x3/3x3ComputerAlgorithms
   - Comprehensive timeline of computer algorithms
   - Historical references and citations
   - Algorithm diagrams and evolution

4. **Ryan Heise's Cube Site**: https://www.ryanheise.com/cube/
   - Human-friendly explanation of algorithms
   - Practical solving methods
   - Tutorial materials

5. **Wikipedia**: https://en.wikipedia.org/wiki/Optimal_solutions_for_the_Rubik%27s_Cube
   - Academic reference
   - Notation standards
   - Comprehensive citations

## Availability Notes

### PDFs Found
- Kociemba_Gods_Number_Is_20.pdf - Successfully downloaded

### Web Pages Archived as HTML
- Heise_Human_Thistlethwaite_Algorithm.html - Complete documentation
- Wikipedia_Optimal_Solutions_Rubiks_Cube.html - Comprehensive reference

### Papers Not Yet Located
- Cubism For Fun Vol. 28 (1992) - Original publication of Kociemba's algorithm
  - Status: Confirmed existence but PDF not publicly available online
  - Location: Published by Dutch Cube Club (NKC)
  - Note: May be available through university library systems or direct contact with cubing historians

## Research Recommendations

To find additional historical materials:
1. Contact the Dutch Cube Club (NKC) directly for Cubism For Fun archives
2. Check academic library databases for scan permission
3. Search archive.org for historical web captures of kociemba.org and jaapsch.net
4. Contact original authors (Kociemba, Thistlethwaite, Rokicki) through academic channels

## Compilation Date
November 7, 2025

## Authors and Contributors Referenced
- Morwen Thistlethwaite - Original algorithm (1980)
- Herbert Kociemba - Two-phase algorithm (1992)
- Tomas Rokicki - God's Number proof (2010)
- Morley Davidson - God's Number proof (2010)
- John Dethridge - God's Number proof (2010)
- Ryan Heise - Human-friendly algorithm explanation
- Multiple contributors to Cubing History and Wikipedia
