# Jupyter Notebooks

Interactive tutorials and deep-dive explanations of the Rubik's Cube solving algorithms.

## Overview

These Jupyter notebooks provide hands-on, interactive learning experiences for understanding the three implemented algorithms and their comparison.

## Available Notebooks

### 01_Introduction.ipynb ✅
**Status:** Complete
**Topics:**
- Rubik's Cube basics
- Cube representation and notation
- Creating and manipulating cubes
- Basic visualization
- Quick solve example

**Recommended for:** Beginners, getting started

---

### 02_Thistlethwaite_Algorithm.ipynb
**Status:** Template available
**Planned Topics:**
- 4-phase group-theoretic approach
- G₀ → G₁ → G₂ → G₃ → G₄ subgroup reduction
- Phase-by-phase walkthrough
- Performance characteristics

**Recommended for:** Understanding group theory approach

---

### 03_Kociemba_Algorithm.ipynb
**Status:** Template available
**Planned Topics:**
- Two-phase IDA* approach
- Coordinate systems explained
- Pruning tables
- Comparison with Thistlethwaite

**Recommended for:** Understanding modern solving techniques

---

### 04_Korf_IDA_Star.ipynb
**Status:** Template available
**Planned Topics:**
- Pattern databases
- Admissible heuristics
- IDA* search algorithm
- Composite heuristic (novel contribution)
- Optimality guarantees

**Recommended for:** AI/search algorithm enthusiasts

---

### 05_Algorithm_Comparison.ipynb ✅
**Status:** Complete
**Topics:**
- Side-by-side algorithm comparison
- Statistical analysis
- Performance visualizations
- Winner analysis
- Integration with Phase 8 results

**Recommended for:** Understanding trade-offs, thesis research

---

### 06_Custom_Experiments.ipynb
**Status:** Template available
**Planned Topics:**
- Blank experimentation notebook
- Pre-loaded utilities
- Example experiments
- Custom analysis templates

**Recommended for:** Advanced users, research

---

## Getting Started

### Prerequisites

```bash
# Install Jupyter
pip install jupyter jupyterlab

# Install project dependencies
pip install -r requirements.txt

# Optional: Install ipywidgets for interactive widgets
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
```

### Running the Notebooks

```bash
# From project root
cd /home/user/rubicCubeThesis

# Start Jupyter Lab (recommended)
jupyter lab notebooks/

# Or start Jupyter Notebook
jupyter notebook notebooks/
```

### Recommended Order

1. **01_Introduction** - Start here!
2. **05_Algorithm_Comparison** - See algorithms in action
3. **02_Thistlethwaite** - Deep dive into first algorithm
4. **03_Kociemba** - Deep dive into second algorithm
5. **04_Korf_IDA_Star** - Deep dive into third algorithm
6. **06_Custom_Experiments** - Your own research

## Features

### Interactive Elements

- **Live code execution** - Run and modify all code cells
- **3D visualizations** - Rotate and view cube states
- **Statistical analysis** - See performance metrics
- **Comparative charts** - Visualize algorithm differences

### Educational Content

Each notebook includes:
- Clear explanations with markdown
- Working code examples
- Visualizations (2D and 3D)
- Performance benchmarks
- References and further reading

## Usage Tips

### For Students

- Read through notebooks sequentially
- Run all cells to see outputs
- Experiment by modifying parameters
- Try the exercises in each notebook

### For Researchers

- Use `05_Algorithm_Comparison` for benchmarking
- Export results to JSON for further analysis
- Modify `06_Custom_Experiments` for your needs
- Integrate with Phase 8 comprehensive testing

### For Thesis

- Notebooks provide reproducible experiments
- Export figures for thesis inclusion
- Statistical analyses ready for reporting
- Code examples for appendices

## Example Usage

### Quick Comparison

```python
# In any notebook
from src.evaluation.algorithm_comparison import AlgorithmComparison
from src.cube.rubik_cube import RubikCube

# Create scramble
cube = RubikCube()
cube.scramble(n_moves=10, seed=42)

# Compare algorithms
comparison = AlgorithmComparison()
result = comparison.compare_on_scramble(cube)

# View results
print(f"Thistlethwaite: {result.thistlethwaite.solution_length} moves")
print(f"Kociemba: {result.kociemba.solution_length} moves")
print(f"Korf: {result.korf.solution_length} moves")
```

### Visualization

```python
from src.cube.visualize_3d import visualize_cube_3d
import matplotlib.pyplot as plt

# Create and visualize cube
cube = RubikCube()
cube.scramble(n_moves=15)

fig = visualize_cube_3d(cube)
plt.show()
```

## Troubleshooting

### Kernel Issues

If the kernel crashes or becomes unresponsive:
```bash
# Restart Jupyter
jupyter notebook stop
jupyter notebook start
```

### Import Errors

Make sure you're running from the project root:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
```

### Visualization Issues

For 3D visualization:
```python
%matplotlib inline  # For static plots
%matplotlib notebook  # For interactive plots (in Jupyter Notebook)
%matplotlib widget  # For interactive plots (in Jupyter Lab)
```

### Memory Issues

If Korf solver uses too much memory:
- Reduce scramble depth (try 10-12 moves)
- Reduce max_depth parameter
- Close other notebooks
- Restart kernel

## Exporting Results

### Export Figures

```python
# Save matplotlib figure
fig.savefig('results/figure1.png', dpi=300, bbox_inches='tight')
```

### Export Data

```python
# Export comparison results
comparison.export_results('results/data.json')
comparison.export_summary_table('results/summary.md', format='markdown')
```

### Export Notebook as PDF

```bash
# Install nbconvert
pip install nbconvert

# Convert to PDF (requires LaTeX)
jupyter nbconvert --to pdf notebooks/01_Introduction.ipynb

# Or convert to HTML
jupyter nbconvert --to html notebooks/01_Introduction.ipynb
```

## Creating Custom Notebooks

To create your own analysis notebook:

1. Copy `06_Custom_Experiments.ipynb` as a template
2. Add your imports and setup
3. Use the comparison framework for testing
4. Export results for thesis inclusion

Example template:
```python
# Standard setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))

from src.cube.rubik_cube import RubikCube
from src.evaluation.algorithm_comparison import AlgorithmComparison
import matplotlib.pyplot as plt

# Your custom code here
```

## Contributing

To add or improve notebooks:

1. Follow the existing structure
2. Include explanatory markdown cells
3. Provide working code examples
4. Add visualizations where appropriate
5. Include references

## See Also

- **Web UI**: `streamlit run ui/app.py` - Interactive browser interface
- **CLI Demos**: `demos/phase9/` - Command-line tools
- **Documentation**: `docs/phase9/` - Detailed guides
- **Phase 8 Results**: Integration with comprehensive testing

## References

1. Thistlethwaite, M. (1981). "52-move algorithm for Rubik's Cube"
2. Kociemba, H. (1992). "Close to God's Algorithm"
3. Korf, R. (1997). "Finding Optimal Solutions to Rubik's Cube Using Pattern Databases"
4. Rokicki et al. (2010). "God's Number is 20"

## Author

Alex Toska
University of Patras
Phase 9: Demos & UI Visualization
2025
