# Data Directory

This directory contains data files used by the Rubik's Cube solving algorithms.

## Structure

### pattern_databases/
Pre-computed pattern databases for Korf's IDA* algorithm.

Pattern databases store optimal distances for subsets of cube pieces, providing admissible heuristics for A* search.

**Contents** (will be created in Phase 3):
- Corner pattern database
- Edge pattern databases (multiple)
- Combined heuristic databases

**Size**: Pattern databases can be several GB in size.

### test_cases/
Standardized test scrambles for benchmarking and evaluation.

**Contents**:
- Easy scrambles (5-10 moves)
- Medium scrambles (15-20 moves)
- Hard scrambles (25+ moves)
- Specific test cases for algorithm validation
- Benchmark suites

**Format**: JSON files with scramble sequences and metadata

## Usage

### Pattern Databases

```python
from src.korf.pattern_db import PatternDatabase

# Load pre-computed database
db = PatternDatabase.load('data/pattern_databases/corner_db.dat')

# Query distance for a cube state
distance = db.lookup(cube)
```

### Test Cases

```python
import json

# Load test scrambles
with open('data/test_cases/benchmark_20.json', 'r') as f:
    test_cases = json.load(f)

for test in test_cases:
    scramble = test['moves']
    difficulty = test['difficulty']
    # Test solver...
```

## Generation

Pattern databases and test cases will be generated during implementation phases:

- **Phase 3 (Weeks 7-8)**: Korf's algorithm - Generate pattern databases
- **Phase 4 (Weeks 9-10)**: Testing framework - Create test case suite

## Storage Notes

- Pattern databases are stored in binary format for efficiency
- Test cases are stored in JSON for readability
- Large files (> 100MB) are excluded from git (see .gitignore)
- Databases can be regenerated using generation scripts

## References

- Korf (1997): Pattern database methodology
- Culberson & Schaeffer (1998): Pattern database theory
