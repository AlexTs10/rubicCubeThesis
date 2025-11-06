# Singmaster Notation - Complete Reference

## Overview

Singmaster notation is the standard system for recording Rubik's Cube moves. It was introduced by David Singmaster in his 1981 book "Notes on Rubik's Magic Cube."

## Face Letters

The cube has six faces, each designated by a letter:

| Letter | Face       | Standard Color | Position          |
|--------|------------|----------------|-------------------|
| **U**  | Up         | White          | Top face          |
| **D**  | Down       | Yellow         | Bottom face       |
| **F**  | Front      | Green          | Facing you        |
| **B**  | Back       | Blue           | Away from you     |
| **L**  | Left       | Orange         | Left side         |
| **R**  | Right      | Red            | Right side        |

**Standard Orientation**: White (U) on top, Green (F) in front.

## Basic Moves (Quarter Turns)

A face letter by itself means **90° clockwise rotation** when looking at that face.

### Examples:
- **R**: Rotate the Right face 90° clockwise
- **U**: Rotate the Up face 90° clockwise
- **F**: Rotate the Front face 90° clockwise

**Clockwise Direction**: Determined by looking directly at the face being rotated.

## Move Modifiers

### Prime (') - Counter-Clockwise

The apostrophe indicates a **90° counter-clockwise** rotation.

**Examples**:
- **R'**: Right face 90° counter-clockwise (inverse of R)
- **U'**: Up face 90° counter-clockwise
- **F'**: Front face 90° counter-clockwise

### Double (2) - 180° Turn

The number 2 indicates a **180° rotation** (clockwise or counter-clockwise, same result).

**Examples**:
- **R2**: Right face 180°
- **U2**: Up face 180°
- **F2**: Front face 180°

**Note**: Double moves are self-inverse: R2 R2 returns to the original state.

## Complete Move Set

Here are all 18 basic moves:

### Face Moves (Outer Layer Only)

| Move    | Description                           | Inverse  |
|---------|---------------------------------------|----------|
| **U**   | Up face 90° clockwise                | **U'**   |
| **U'**  | Up face 90° counter-clockwise        | **U**    |
| **U2**  | Up face 180°                         | **U2**   |
| **D**   | Down face 90° clockwise              | **D'**   |
| **D'**  | Down face 90° counter-clockwise      | **D**    |
| **D2**  | Down face 180°                       | **D2**   |
| **F**   | Front face 90° clockwise             | **F'**   |
| **F'**  | Front face 90° counter-clockwise     | **F**    |
| **F2**  | Front face 180°                      | **F2**   |
| **B**   | Back face 90° clockwise              | **B'**   |
| **B'**  | Back face 90° counter-clockwise      | **B**    |
| **B2**  | Back face 180°                       | **B2**   |
| **L**   | Left face 90° clockwise              | **L'**   |
| **L'**  | Left face 90° counter-clockwise      | **L**    |
| **L2**  | Left face 180°                       | **L2**   |
| **R**   | Right face 90° clockwise             | **R'**   |
| **R'**  | Right face 90° counter-clockwise     | **R**    |
| **R2**  | Right face 180°                      | **R2**   |

## Advanced Notation

### Wide Moves (Lowercase w)

Wide moves rotate **two layers** instead of one.

**Notation**: Add lowercase 'w' after the face letter.

**Examples**:
- **Rw**: Rotate right face + middle layer (equivalent to R M')
- **Uw**: Rotate up face + E slice layer
- **Fw**: Rotate front face + S slice layer

**Alternative Notation** (used in WCA):
- **Rw** can also be written as **r**
- **Uw** can also be written as **u**
- **Fw** can also be written as **f**

### Slice Moves (Middle Layers)

Slice moves affect only the **middle layer**, not the outer faces.

| Move  | Description                              | Direction        |
|-------|------------------------------------------|------------------|
| **M** | Middle layer (between L and R)          | Same as L        |
| **E** | Equatorial layer (between U and D)      | Same as D        |
| **S** | Standing layer (between F and B)        | Same as F        |

**Examples**:
- **M**: Middle slice, follows L direction
- **M'**: Middle slice counter-clockwise (follows L')
- **E**: Equatorial slice, follows D direction
- **S**: Standing slice, follows F direction

**Memory Aid**:
- **M** for Middle (vertical, like L)
- **E** for Equator (horizontal)
- **S** for Standing (perpendicular to front)

### Cube Rotations

Rotate the **entire cube** without changing the puzzle state relatively.

| Move  | Description                              |
|-------|------------------------------------------|
| **x** | Rotate entire cube on R axis (like R)   |
| **x'**| Rotate entire cube on R axis (like R')  |
| **y** | Rotate entire cube on U axis (like U)   |
| **y'**| Rotate entire cube on U axis (like U')  |
| **z** | Rotate entire cube on F axis (like F)   |
| **z'**| Rotate entire cube on F axis (like F')  |

**Use Case**: Reorienting the cube during algorithms to make execution easier.

**Example**:
- **y U R U' R'** is equivalent to reorienting and performing moves from a different perspective.

## Common Algorithm Patterns

### Trigger Moves

**Sexy Move**: R U R' U'
- One of the most common triggers in speedsolving
- Used in many algorithms

**Sledgehammer**: R' F R F'
- Another fundamental trigger
- Useful for corner manipulation

### Commutators

**Format**: [A, B] = A B A' B'

**Example**: [R, U] = R U R' U'
- Affects only a few pieces
- Core building block for algorithms

### Conjugates

**Format**: X A X'
- Setup move (X), algorithm (A), undo setup (X')

**Example**: F (R U R' U') F'
- Setup with F, sexy move, undo with F'

## Algorithm Notation Examples

### Example 1: T-Permutation
```
R U R' U' R' F R2 U' R' U' R U R' F'
```
- Swaps two adjacent corners and two adjacent edges

### Example 2: Sune
```
R U R' U R U2 R'
```
- Orients corners in last layer

### Example 3: J-Permutation
```
R U R' F' R U R' U' R' F R2 U' R'
```
- Swaps two corners and two edges

## Reading Algorithms

### Tips for Beginners:

1. **Pace yourself**: Don't rush through moves
2. **Learn triggers**: Recognize common patterns like R U R' U'
3. **Use muscle memory**: Practice until moves become automatic
4. **Check orientation**: Ensure the cube is held correctly (white/yellow on U/D)

### Parsing a Sequence:

Given: `R U R' U' F' U' F U R U' R'`

**Break it down**:
1. R U R' U' (sexy move)
2. F' U' F U (inverse of F U F' U')
3. R U' R' (partial trigger)

## Metric Considerations

### Half-Turn Metric (HTM)

All moves count as **1 move**:
- U, U', U2 each count as 1
- Used in official WCA notation
- God's number: **20 moves (HTM)**

### Quarter-Turn Metric (QTM)

180° moves count as **2 moves**:
- U and U' count as 1
- U2 counts as 2
- Used in some theoretical analysis
- God's number: **26 moves (QTM)**

### Face Turn Metric (FTM)

Only outer face moves count:
- Slice moves (M, E, S) don't count or count differently
- Less common in modern usage

## Implementation Notes

### In Code

Our implementation (rubik_cube.py) supports:

```python
cube.apply_move('R')      # 90° clockwise
cube.apply_move("R'")     # 90° counter-clockwise
cube.apply_move('R2')     # 180°
cube.apply_move_sequence("R U R' U'")  # Multiple moves
```

**Supported Moves**: U, D, F, B, L, R with modifiers ', 2

**Not Yet Implemented**:
- Wide moves (Rw, Uw, etc.)
- Slice moves (M, E, S)
- Cube rotations (x, y, z)

These can be added in future phases as needed.

## Practice Sequences

### Beginner Sequences

1. **Four Move Cycle**: R U R' U' (repeat 6 times returns to solved)
2. **Six Move Cycle**: R U R' F' (repeat 6 times returns to solved)
3. **Eight Move Cycle**: R U2 R' U' (repeat several times)

### Test Your Understanding

Try these sequences and verify the result:

1. R R R R = solved (four 90° = 360°)
2. R2 R2 = solved (two 180° = 360°)
3. R U R' U' × 6 = solved (sexy move repeated 6 times)

## Notation Standards

### WCA (World Cube Association) Standard

- Official competitions use Singmaster notation
- HTM (Half-Turn Metric) is standard
- No distinction between quarter turns for move count

### Alternative Notations

**Historical**:
- Some old books use different letters or symbols
- Modern solvers universally use Singmaster

**Computer Science**:
- Some algorithms use numerical encoding
- Our implementation uses standard letters internally

## Common Mistakes to Avoid

1. **Confusing L and R orientation**: Always look at the face directly
2. **Misreading prime (')**:  R' is counter-clockwise, not R2
3. **Wrong face**: B (back) is opposite F (front)
4. **Order matters**: R U ≠ U R (moves don't commute generally)
5. **Parsing errors**: "R'U" should be "R' U" (space-separated)

## Tips for Learning

1. **Start with basic moves**: Master U, R, F and their inverses first
2. **Practice recognition**: See "R U R' U'" as a single unit (sexy move)
3. **Finger tricks**: Learn efficient ways to execute moves
4. **Algorithm sheets**: Keep a reference of common algorithms
5. **Visualization**: Try to predict move outcomes mentally

## Resources for Further Study

### Online Tools

- **Ruwix Notation Guide**: https://ruwix.com/the-rubiks-cube/notation/
  - Interactive demonstrations of each move

- **Speedsolving Wiki**: https://www.speedsolving.com/wiki/index.php/Notation
  - Comprehensive notation encyclopedia

- **CubeExplorer**: Software for algorithm analysis
  - Visualizes move sequences

### Recommended Practice

1. Use an online cube simulator to see moves visually
2. Practice writing down scrambles and solutions
3. Learn to read algorithms without looking at the cube
4. Time yourself executing standard sequences

## Summary

**Core Notation**:
- 6 face letters: U, D, F, B, L, R
- 3 modifiers: (none) = 90° CW, ' = 90° CCW, 2 = 180°
- 18 total basic moves

**Advanced**:
- Wide moves: Rw, Uw, etc.
- Slice moves: M, E, S
- Rotations: x, y, z

**Best Practices**:
- Always use standard Singmaster notation
- Space-separate moves in sequences
- Check cube orientation before executing algorithms
- Practice until moves become muscle memory

This notation system is the universal language of Rubik's Cube solving!
