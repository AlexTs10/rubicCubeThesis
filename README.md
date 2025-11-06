# Rubik's Cube Solving Algorithms - Master's Thesis

**Author:** Alexandru Teișanu
**Institution:** University of Bucharest
**Program:** Master's in Artificial Intelligence

## Overview

This repository contains the implementation and comparative analysis of three classical Rubik's Cube solving algorithms for my master's thesis:

1. **Thistlethwaite's Algorithm** (1981) - Group-theoretic approach with 4 subgroups
2. **Kociemba's Algorithm** (1992) - Two-phase algorithm used in speed-solving
3. **Korf's Algorithm** (1997) - IDA* with pattern databases for optimal solutions

## Research Goals

- Implement all three algorithms in Python with clean, well-documented code
- Develop a distance estimator to evaluate cube states
- Design and compare heuristic functions for A* optimal solving
- Perform comprehensive performance analysis across multiple metrics:
  - Solution quality (move count)
  - Time complexity
  - Space complexity
  - Success rate on various scramble difficulties

## Project Structure

```
rubik-thesis/
├── src/
│   ├── cube/              # Core cube representation and operations
│   ├── thistlethwaite/    # Thistlethwaite algorithm implementation
│   ├── kociemba/          # Kociemba two-phase algorithm
│   ├── korf/              # Korf's IDA* with pattern databases
│   ├── utils/             # Shared utilities and helpers
│   └── evaluation/        # Testing and benchmarking framework
├── data/
│   ├── pattern_databases/ # Precomputed pattern databases for Korf
│   └── test_cases/        # Standardized test scrambles
├── tests/                 # Unit, integration, and performance tests
├── results/               # Experimental results and visualizations
├── docs/                  # Thesis chapters and documentation
└── demos/                 # Example scripts and demonstrations
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd rubicCubeThesis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver

# Create a solved cube
cube = RubikCube()

# Scramble it
cube.scramble(moves=20)

# Solve using Thistlethwaite
solver = ThistlethwaiteSolver()
solution = solver.solve(cube)
print(f"Solution: {solution}")
```

## Development Timeline

- **Week 1-2:** Foundation & Setup (Current Phase)
- **Week 3-4:** Thistlethwaite Implementation
- **Week 5-6:** Kociemba Implementation
- **Week 7-8:** Korf Implementation
- **Week 9-10:** Distance Estimator & Heuristics
- **Week 11-12:** Testing & Optimization
- **Week 13-14:** Comparative Analysis
- **Week 15-16:** Thesis Writing & Defense Preparation

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run performance benchmarks
pytest tests/performance/ --benchmark-only
```

## Documentation

- Detailed implementation notes in `docs/notes/`
- Thesis chapters in `docs/thesis_chapters/`
- Algorithm references and papers in `docs/references/`

## Key References

1. Thistlethwaite, M. (1981). *52-move algorithm for Rubik's cube*
2. Kociemba, H. (1992). *Close to God's Algorithm*
3. Korf, R. (1997). *Finding Optimal Solutions to Rubik's Cube Using Pattern Databases*
4. Rokicki et al. (2010). *Diameter of the Rubik's Cube Group is 20*

## License

This project is created for academic purposes as part of a master's thesis.

## Contact

For questions or collaboration: alexandru.teisanu@[university-email]
