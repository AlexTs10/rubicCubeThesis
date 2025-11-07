# Documentation Index - Quick Navigation

This file helps you navigate all the documentation for the Rubik's Cube Thesis project.

## Start Here

**New to the project?** Start with these in order:

1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** (Executive Overview)
   - Quick stats and status
   - What's implemented
   - Key findings
   - Thesis readiness checklist
   - **Best for**: Understanding the project at a glance

2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (Quick Lookup)
   - Algorithm quick stats
   - Test organization overview
   - Key commands and examples
   - Performance results
   - **Best for**: Finding specific information quickly

3. **[CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md)** (Comprehensive Analysis)
   - Detailed phase breakdown
   - Complete file structure
   - Testing infrastructure details
   - Dependencies and tools
   - Performance analysis
   - **Best for**: Deep understanding of implementation

---

## Algorithm Documentation

### Phase 3: Thistlethwaite Algorithm
- **File**: [PR_THISTLETHWAITE.md](PR_THISTLETHWAITE.md) (11 KB)
- **Contents**: 
  - Algorithm overview and phases
  - Implementation details
  - Coordinate systems and moves
  - Pattern database design
  - Usage examples and testing
- **Best for**: Understanding the 4-phase group-theoretic approach

### Phase 4: Kociemba Algorithm
- **File**: [KOCIEMBA_README.md](KOCIEMBA_README.md) (6.9 KB)
- **Contents**:
  - Algorithm description (Phase 1 & 2)
  - Cubie representation
  - Coordinate systems (6 systems)
  - Move tables and pruning tables
  - Usage examples
- **Best for**: Understanding the 2-phase near-optimal approach

### Phase 5: Distance Estimation
- **File**: [PR_DISTANCE_ESTIMATOR.md](PR_DISTANCE_ESTIMATOR.md) (8.9 KB)
- **Contents**:
  - Pattern database implementation
  - Heuristic functions
  - Accuracy evaluation
  - Performance results
  - Validation framework
- **Best for**: Understanding pattern databases and heuristics

### Phase 7: A* with Heuristics
- **File**: [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md) (9.2 KB)
- **Contents**:
  - A* algorithm implementation
  - IDA* algorithm implementation
  - Novel composite heuristic
  - Performance comparison
  - Empirical findings (A* vs IDA*)
- **Best for**: Understanding search algorithms and optimization

---

## Getting Started

### Installation & Setup
```bash
# Clone and enter project
cd rubicCubeThesis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_thistlethwaite.py -v

# With coverage
pytest --cov=src tests/
```

### Running Demos
```bash
python demos/basic_usage.py
python demos/thistlethwaite_demo.py
python demos/kociemba_demo.py
python demos/distance_estimator_demo.py
python demos/a_star_comparison_demo.py
python demos/visualization_demo.py
```

---

## File Organization by Purpose

### Documentation Files (Root Level)
| File | Purpose | Audience |
|------|---------|----------|
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Executive summary | Everyone |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick lookup guide | Developers |
| [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md) | Comprehensive analysis | Researchers |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | Navigation guide | Everyone |
| [README.md](README.md) | Original project overview | New users |

### Algorithm PRs
| File | Phase | Focus |
|------|-------|-------|
| [PR_THISTLETHWAITE.md](PR_THISTLETHWAITE.md) | 3 | 4-phase group-theoretic |
| [KOCIEMBA_README.md](KOCIEMBA_README.md) | 4 | 2-phase near-optimal |
| [PR_DISTANCE_ESTIMATOR.md](PR_DISTANCE_ESTIMATOR.md) | 5 | Pattern databases |
| [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md) | 7 | A*/IDA* optimization |

### Supporting Documentation
| File | Location | Content |
|------|----------|---------|
| Design Notes | [docs/notes/](docs/notes/) | Group theory, notation, resources |
| Technical Guide | [docs/DISTANCE_ESTIMATOR_README.md](docs/DISTANCE_ESTIMATOR_README.md) | Pattern DB technical details |
| Data README | [data/README.md](data/README.md) | Data structure placeholder |
| Results README | [results/README.md](results/README.md) | Experimental results location |

---

## Code Structure

### Source Code (8,157 lines)
```
src/
├── cube/              # Core representation (1,428 lines)
├── thistlethwaite/    # Phase 3 (1,206 lines)
├── kociemba/          # Phase 4 (1,530 lines)
├── korf/              # Phase 5-7 (2,965 lines)
├── evaluation/        # Testing framework (placeholder)
└── utils/             # Shared utilities
```

### Tests (2,768 lines)
```
tests/
├── unit/              # 8 test files (1,837 lines)
│   ├── test_rubik_cube.py (164)
│   ├── test_moves.py (196)
│   ├── test_cube_advanced.py (311)
│   ├── test_thistlethwaite.py (399)
│   ├── test_kociemba.py (415)
│   ├── test_distance_estimator.py (335)
│   ├── test_a_star_solvers.py (360)
│   └── test_composite_heuristic.py (356)
└── integration/       # 1 test file (231 lines)
    └── test_workflows.py (231)
```

### Demos (6 scripts)
```
demos/
├── basic_usage.py
├── thistlethwaite_demo.py
├── kociemba_demo.py
├── distance_estimator_demo.py
├── a_star_comparison_demo.py
└── visualization_demo.py
```

---

## Key Statistics

### Implementation Scale
- **Total Source Code**: 8,157 lines
- **Total Test Code**: 2,768 lines
- **Documentation**: 9 markdown files, 40+ KB
- **Algorithms**: 3 major implementations
- **Pattern Databases**: 88M corner + 645K×2 edge states

### Testing Scale
- **Test Files**: 8 unit + 1 integration + 2 quick tests
- **Test Classes**: 20+
- **Test Methods**: 100+
- **Coverage Areas**: Foundation, algorithms, integration, workflows

### Development Progress
- **Phases Completed**: 7/7 (100%)
- **Commits**: 20+ tracked in git history
- **Status**: Ready for thesis writing and defense

---

## Research Contributions

### Novel Components
1. **Composite Heuristic** (Phase 7, `src/korf/composite_heuristic.py`)
   - Adaptive heuristic selection based on cube state
   - 15-25% reduction in node expansions
   - Maintains admissibility guarantee

2. **A* vs IDA* Analysis** (Phase 7, `src/korf/solver_comparison.py`)
   - Empirical comparison framework
   - Memory vs time trade-off analysis
   - Practical findings: IDA* solves 100x more cubes

3. **Pattern Database Infrastructure** (Phase 5, `src/korf/`)
   - Comprehensive pattern DB design
   - Nibble compression (4 bits per distance)
   - Validation framework with accuracy metrics

---

## Quick Command Reference

### Test Execution
```bash
pytest tests/                           # Run all tests
pytest tests/unit/ -v                   # Verbose unit tests
pytest --cov=src tests/                 # With coverage report
pytest tests/unit/test_thistlethwaite.py # Specific test file
```

### Demo Execution
```bash
python demos/basic_usage.py             # Basic example
python demos/thistlethwaite_demo.py     # Thistlethwaite solver
python demos/kociemba_demo.py           # Kociemba solver
python demos/a_star_comparison_demo.py  # A* vs IDA* comparison
python demos/visualization_demo.py      # Visualization examples
```

### Project Verification
```bash
python verify_setup.py                  # Check environment
python debug_phase1.py                  # Phase debugging
python debug_coords.py                  # Coordinate debugging
```

---

## Recommended Reading Order

### For Developers
1. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick overview
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Understand scope
3. Code exploration starting with `src/cube/`
4. [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md) - Deep understanding

### For Researchers
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Context
2. Algorithm PRs in order: Thistlethwaite → Kociemba → Distance → A*/IDA*
3. [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md) - Implementation details
4. Source code for specific algorithms

### For Thesis Writing
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overview
2. Algorithm PRs for technical details
3. [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md) - Comprehensive analysis
4. Source code and test files for validation data

### For Presentation/Defense
1. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Key metrics
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Overall narrative
3. [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md) - Research contributions
4. Performance tables and comparison results

---

## Technical Details by Topic

### Algorithms
- **Thistlethwaite (4-phase)**: [PR_THISTLETHWAITE.md](PR_THISTLETHWAITE.md)
- **Kociemba (2-phase)**: [KOCIEMBA_README.md](KOCIEMBA_README.md)
- **Korf (IDA* with pattern DBs)**: [PR_DISTANCE_ESTIMATOR.md](PR_DISTANCE_ESTIMATOR.md)
- **A* and IDA***: [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md)

### Pattern Databases
- **Design and Implementation**: [PR_DISTANCE_ESTIMATOR.md](PR_DISTANCE_ESTIMATOR.md)
- **Technical Details**: [docs/DISTANCE_ESTIMATOR_README.md](docs/DISTANCE_ESTIMATOR_README.md)
- **Source Code**: `src/korf/pattern_database.py`, `corner_database.py`, `edge_database.py`

### Heuristics
- **All heuristics**: [PR_DISTANCE_ESTIMATOR.md](PR_DISTANCE_ESTIMATOR.md)
- **Composite heuristic**: [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md)
- **Source Code**: `src/korf/heuristics.py`, `composite_heuristic.py`

### Performance Analysis
- **A* vs IDA* comparison**: [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md)
- **Framework**: `src/korf/solver_comparison.py`
- **Results**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) performance tables

---

## Document Quick Links

### Start Here
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - ⭐ Best entry point
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - ⭐ Quick lookup
- [README.md](README.md) - Original overview

### Deep Dives
- [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md) - Complete analysis
- [PR_THISTLETHWAITE.md](PR_THISTLETHWAITE.md) - 4-phase algorithm
- [KOCIEMBA_README.md](KOCIEMBA_README.md) - 2-phase algorithm
- [PR_DISTANCE_ESTIMATOR.md](PR_DISTANCE_ESTIMATOR.md) - Pattern databases
- [PHASE7_PR_DESCRIPTION.md](PHASE7_PR_DESCRIPTION.md) - A*/IDA* & research

### Code Structure
- [docs/DISTANCE_ESTIMATOR_README.md](docs/DISTANCE_ESTIMATOR_README.md) - Technical guide
- [docs/notes/](docs/notes/) - Design notes

---

## Version Information

**Project Status**: ✅ PHASE 7/7 COMPLETE  
**Last Updated**: November 7, 2025  
**Author**: Alex Toska  
**Institution**: University of Patras  

**Code Statistics**:
- Source: 8,157 lines
- Tests: 2,768 lines  
- Documentation: 40+ KB
- Algorithms: 3 complete
- Test Coverage: 100+ test methods

**Ready for**:
- Thesis writing ✅
- Academic presentation ✅
- Defense preparation ✅
- Publication ✅

---

## Need Help?

1. **Understanding the project**: Start with [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. **Finding specific code**: Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. **Implementation details**: See [CODEBASE_OVERVIEW.md](CODEBASE_OVERVIEW.md)
4. **Algorithm specifics**: Read the appropriate PR file
5. **Running code**: Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md) command section
6. **Testing**: Check test files in `tests/` directory

---

