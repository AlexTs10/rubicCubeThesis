# Chapter 08: Implementation - Detailed Specification

**Title (Greek):** Υλοποίηση
**Goal:** Document the software architecture and implementation decisions
**Target:** ~2,500 words (8-10 pages with figures and diagrams)
**Key takeaway:** The implementation demonstrates clean separation of concerns through modular design, enabling independent algorithm development and fair comparison

---

## Section 8.1: System Architecture (~400 words)

### 8.1.1 Directory Structure (~200 words)

**Points to Cover:**
1. Modular organization by algorithm: `src/cube/`, `src/thistlethwaite/`, `src/kociemba/`, `src/korf/`
2. Separation of concerns: representation, algorithms, evaluation
3. Total codebase: ~10,700 lines of Python

**Figure 8.1: Directory Tree**
```
src/
├── cube/                # Core representation (303 lines)
├── thistlethwaite/     # 4-phase algorithm (1,757 lines)
├── kociemba/           # 2-phase algorithm (1,967 lines)
├── korf/               # Optimal solver (3,534 lines)
└── evaluation/         # Comparison framework (500+ lines)
```

### 8.1.2 Module Dependencies (~200 words)

**Points to Cover:**
1. Core `cube` module has no dependencies on algorithms
2. Each algorithm depends only on `cube` (not on each other)
3. Evaluation module aggregates all algorithms

**Dependency Diagram:**
```
           evaluation
          /    |    \
thistlethwaite kociemba korf
          \    |    /
             cube
```

---

## Section 8.2: Cube Representation (~500 words)

### 8.2.1 Facelet-Based Representation (~250 words)

**Points to Cover:**
1. 6 faces × 9 facelets = 54 values
2. NumPy array: `state.shape = (6, 9)`
3. Face indices: U(0), D(1), F(2), B(3), L(4), R(5)
4. Facelet indices per face: standard 0-8 pattern

**Design Decision:** Facelet chosen over cubie for:
- Intuitive mapping to physical cube
- Efficient numpy operations
- Direct state comparison for hashing

**Code References:**
- `src/cube/rubik_cube.py:58-80` - State initialization
- `src/cube/rubik_cube.py:119-183` - Move application

### 8.2.2 Cubie Adapter Pattern (~250 words)

**Points to Cover:**
1. CubieCube class for coordinate calculations
2. Conversion functions: `from_facelet_cube()`, `to_facelet_cube()`
3. Separates user-facing interface from algorithm internals

**Pattern Implementation:**
```python
class CubieCube:
    corner_perm: np.array   # 8 positions
    corner_orient: np.array # 3 orientations each
    edge_perm: np.array     # 12 positions
    edge_orient: np.array   # 2 orientations each
```

**Code References:**
- `src/kociemba/cubie.py:30-114` - CubieCube class
- `src/kociemba/cubie.py:231-352` - `from_facelet_cube()`
- `src/kociemba/cubie.py:355-422` - `to_facelet_cube()`

---

## Section 8.3: Design Patterns (~600 words)

### 8.3.1 Lazy Loading Pattern (~200 words)

**Points to Cover:**
1. Pattern databases loaded only when first needed
2. Benefits: fast initialization, memory efficiency
3. Implementation: `_ensure_databases_loaded()` method

**Code Example:**
```python
class ThistlethwaiteSolver:
    def __init__(self):
        self._databases_loaded = False

    def _ensure_databases_loaded(self):
        if self._databases_loaded:
            return
        # Load expensive databases
        self._databases_loaded = True
```

**Code References:**
- `src/thistlethwaite/solver.py:58-65` - Lazy initialization
- `src/kociemba/solver.py:56-73` - `_initialize()` method

### 8.3.2 Factory Pattern (~200 words)

**Points to Cover:**
1. Heuristic creation via `create_heuristic(type_string)`
2. Decouples solver from specific heuristic implementation
3. Enables easy extension with new heuristics

**Code References:**
- `src/korf/composite_heuristic.py:399-423` - `create_heuristic()` factory

### 8.3.3 Load-or-Generate Caching (~200 words)

**Points to Cover:**
1. Check for cached file on disk
2. If exists: load (fast path)
3. If not: generate and save for future use
4. Format: pickle with numpy arrays

**Code References:**
- `src/thistlethwaite/tables.py:105-119` - `load_or_generate()`
- `src/kociemba/pruning.py:57-102` - Pruning table caching

---

## Section 8.4: Algorithm Implementations (~600 words)

### 8.4.1 Thistlethwaite Implementation (~200 words)

**Points to Cover:**
1. Four-phase structure with phase-specific classes
2. Coordinates module: 8 different coordinate systems
3. Pattern database per phase
4. Fallback to Kociemba on timeout

**Key Files:**
- `solver.py`: Main coordinator (377 lines)
- `coordinates.py`: 8 coordinate systems (451 lines)
- `tables.py`: Pattern database collection (325 lines)
- `ida_star.py`: Phase search (313 lines)

**Code References:**
- `src/thistlethwaite/solver.py:22-350` - ThistlethwaiteSolver class
- `src/thistlethwaite/solver.py:282-318` - Phase goal checks

### 8.4.2 Kociemba Implementation (~200 words)

**Points to Cover:**
1. Two-phase structure: G₀ → G₁ → Solved
2. Six coordinate systems
3. Move tables for O(1) transitions
4. Pruning tables for heuristics

**Key Files:**
- `solver.py`: Main solver (479 lines)
- `coord.py`: 6 coordinate systems (436 lines)
- `moves.py`: Move tables (266 lines)
- `pruning.py`: Pruning tables (322 lines)

**Code References:**
- `src/kociemba/solver.py:79-187` - Main solve method
- `src/kociemba/coord.py:377-436` - CoordCube class

### 8.4.3 Korf Implementation (~200 words)

**Points to Cover:**
1. IDA* with pattern database heuristics
2. Corner database: 88M states (~44 MB)
3. Edge databases: split into two groups
4. Composite heuristic for adaptive search

**Key Files:**
- `a_star.py`: A*/IDA* implementations (443 lines)
- `pattern_database.py`: Infrastructure (282 lines)
- `corner_database.py`: Corner PDB (204 lines)
- `composite_heuristic.py`: Novel heuristic (424 lines)

**Code References:**
- `src/korf/a_star.py:271-443` - IDAStarSolver class
- `src/korf/pattern_database.py:211-282` - BFS generation

---

## Section 8.5: Data Persistence (~400 words)

### 8.5.1 Pattern Database Storage (~200 words)

**Points to Cover:**
1. Pickle format for numpy arrays
2. Nibble compression: 2 values per byte
3. Directory structure: `data/pattern_databases/`

**Table 8.1: Database Sizes**
| Database | States | Uncompressed | Compressed |
|----------|--------|--------------|------------|
| Phase 0 (EO) | 2,048 | 2 KB | 1 KB |
| Phase 1 (CO+ES) | 1,082,565 | 1 MB | 500 KB |
| Phase 2 (Tetrad) | 70 | 70 B | 35 B |
| Phase 3 (CP) | 40,320 | 40 KB | 20 KB |
| Corner PDB | 88,179,840 | 88 MB | 44 MB |

**Code References:**
- `src/korf/pattern_database.py:135-174` - Save/load methods

### 8.5.2 Benchmark Results Storage (~200 words)

**Points to Cover:**
1. JSON format for portability
2. One file per scramble depth
3. Contains: algorithm results, metrics, timestamps

**File Structure:**
```json
{
  "metadata": {"depth": 10, "trials": 25},
  "results": [
    {
      "scramble_id": 1,
      "thistlethwaite": {...},
      "kociemba": {...},
      "korf": {...}
    }
  ]
}
```

---

## Section 8.6: Testing Infrastructure (~300 words)

### 8.6.1 Unit Tests (~150 words)

**Points to Cover:**
1. 13 test files covering all modules
2. pytest framework
3. Coverage: cube operations, algorithms, heuristics

**Test Categories:**
- `test_rubik_cube.py`: Core representation
- `test_thistlethwaite.py`: Phase algorithm
- `test_kociemba.py`: Two-phase algorithm
- `test_a_star_solvers.py`: Search algorithms
- `test_composite_heuristic.py`: Novel heuristic

**Code References:**
- `tests/unit/` - All unit tests

### 8.6.2 Integration Tests (~150 words)

**Points to Cover:**
1. End-to-end workflow tests
2. Scramble-and-solve verification
3. Visualization pipeline tests

**Code References:**
- `tests/integration/test_workflows.py`

---

## Section 8.7: Summary (~200 words)

**Key Implementation Decisions:**
1. Facelet representation for intuitive user interface
2. Cubie adapter for efficient coordinate calculation
3. Lazy loading for responsive initialization
4. Modular design enabling fair algorithm comparison

**Technical Metrics:**
- Total: ~10,700 lines of Python
- Test coverage: 13 unit test files + 1 integration
- Demo scripts: 12 demonstration programs

**Transition to Chapter 9:**
"Chapter 9 summarizes the thesis findings and discusses the research contribution of the composite heuristic."

---

## Writing Checklist

### Figures
- [ ] Figure 8.1: Directory structure tree
- [ ] Figure 8.2: Module dependency diagram
- [ ] Figure 8.3: Facelet representation diagram
- [ ] Figure 8.4: CubieCube adapter pattern
- [ ] Figure 8.5: Lazy loading sequence diagram
- [ ] Figure 8.6: Data persistence architecture

### Tables
- [ ] Table 8.1: Database Sizes

### Code Listings
- [ ] Listing 8.1: Facelet state initialization
- [ ] Listing 8.2: Cubie conversion
- [ ] Listing 8.3: Lazy loading pattern
- [ ] Listing 8.4: Factory pattern

### Cross-References
- [ ] Chapter 2 (Background) for representation theory
- [ ] Chapters 3-5 for algorithm details
- [ ] Chapter 6 (Heuristics) for composite implementation
- [ ] Chapter 7 (Evaluation) for benchmark methodology
