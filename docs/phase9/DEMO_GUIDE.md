# Phase 9 Demo Guide

Complete guide for running and demonstrating the Rubik's Cube solving algorithms.

## Quick Start

### Web UI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run ui/app.py
```

Then open your browser to `http://localhost:8501`

### CLI Demos

```bash
# Interactive solver
python demos/phase9/interactive_solver.py

# Algorithm comparison
python demos/phase9/algorithm_comparison_cli.py --depth 10

# Animation
python demos/phase9/animation_demo.py --algorithm kociemba

# Benchmark
python demos/phase9/benchmark_demo.py --n-scrambles 10
```

### Jupyter Notebooks

```bash
# Start Jupyter
jupyter lab notebooks/

# Open: 01_Introduction.ipynb
```

## Detailed Guides

### 1. Web UI Demo

**Best for:** Presentations, interactive exploration, thesis defense

**Features:**
- Single algorithm testing
- Side-by-side comparison
- Educational mode
- Performance metrics
- 3D visualization

**Demo Script:**

1. **Introduction** (2 minutes)
   - "This is an interactive web interface for comparing three Rubik's Cube solving algorithms"
   - Navigate through the sidebar to show available pages

2. **Single Solver Demo** (3 minutes)
   - Select Kociemba algorithm
   - Set scramble depth to 10
   - Click "Generate New Scramble"
   - Click "Solve Cube"
   - Show solution metrics
   - Use animation slider to show step-by-step solving

3. **Comparison Mode** (5 minutes)
   - Navigate to "Algorithm Comparison" page
   - Set scramble depth to 10, seed to 42
   - Click "Run Comparison"
   - Highlight the results table
   - Show winner analysis
   - Discuss trade-offs

4. **Educational Mode** (3 minutes)
   - Navigate to "Educational Mode"
   - Show algorithm explanations
   - Highlight key differences
   - Show glossary

**Tips:**
- Use seed 42 for reproducible results
- Keep scramble depth at 10 for quick demos
- Prepare beforehand by testing the app
- Have backup screenshots in case of technical issues

### 2. CLI Demo

**Best for:** Quick demonstrations, technical audiences

**Interactive Solver Demo:**

```bash
python demos/phase9/interactive_solver.py
```

**Demo Script:**
1. Choose option 2 (Scramble with seed)
2. Enter seed: 42, depth: 10
3. Choose option 9 (View cube state)
4. Choose option 5 (Solve with Kociemba)
5. Choose option 7 (View solution step-by-step)

**Algorithm Comparison Demo:**

```bash
python demos/phase9/algorithm_comparison_cli.py --depth 10 --seed 42
```

Highlights the side-by-side comparison with formatted tables and winner analysis.

### 3. Jupyter Notebook Demo

**Best for:** Technical presentations, deep dives, educational sessions

**Demo Script:**

1. **Open 01_Introduction.ipynb** (5 minutes)
   - Run all cells from top
   - Show cube creation and visualization
   - Demonstrate scrambling
   - Run quick solve example

2. **Open 05_Algorithm_Comparison.ipynb** (7 minutes)
   - Run single scramble comparison
   - Run batch test (10 scrambles)
   - Show statistical summary
   - Display visualization charts

**Tips:**
- Run all cells before presenting to cache results
- Restart kernel if memory issues occur
- Use "Cell → Run All" for quick setup

## Demo Scenarios

### Scenario 1: Thesis Defense (15 minutes)

**Timeline:**
1. **Introduction (2 min)**: Open Web UI, explain project overview
2. **Single Algorithm (3 min)**: Demonstrate Kociemba on sample scramble
3. **Comparison (5 min)**: Run comparison mode, discuss results
4. **Educational (2 min)**: Show algorithm explanations
5. **Q&A (3 min)**: Answer questions, show specific features

**Preparation:**
- Pre-test all features
- Have backup scrambles ready
- Prepare explanation of key findings
- Have Phase 8 results handy for reference

### Scenario 2: Classroom Demo (30 minutes)

**Timeline:**
1. **Introduction (5 min)**: Explain Rubik's Cube problem
2. **Web UI Tour (10 min)**: Show all features interactively
3. **Live Coding (10 min)**: Open Jupyter notebook, run comparisons
4. **Hands-on (5 min)**: Let students try the web interface

**Materials:**
- Web UI running on projector
- Physical Rubik's Cube for demonstration
- Jupyter notebook ready
- Handout with key algorithm differences

### Scenario 3: Quick Demo (5 minutes)

**Timeline:**
1. **Web UI (2 min)**: Open comparison mode, run preset scramble
2. **Results (2 min)**: Explain metrics and winners
3. **Conclusion (1 min)**: Summary of findings

**Preparation:**
- Have comparison page pre-loaded
- Use seed 42 for consistency
- Know the expected results

## Troubleshooting

### Web UI Issues

**Problem:** Port 8501 already in use
```bash
# Use different port
streamlit run ui/app.py --server.port 8502
```

**Problem:** UI not loading
- Check if dependencies installed: `pip install streamlit`
- Restart Streamlit: `Ctrl+C` and run again
- Clear browser cache

**Problem:** Korf solver timeout
- Increase timeout in sidebar
- Reduce scramble depth to 10-12
- Use "max depth" setting

### CLI Issues

**Problem:** Rich library not installed
```bash
pip install rich
```
Demos work without it but output is less formatted.

**Problem:** Import errors
Make sure you're in the project root:
```bash
cd /home/user/rubicCubeThesis
python demos/phase9/interactive_solver.py
```

### Jupyter Issues

**Problem:** Kernel dies during Korf
- Restart kernel
- Reduce scramble depth
- Close other notebooks

**Problem:** Matplotlib not displaying
```python
%matplotlib inline
```

**Problem:** Import errors
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
```

## Recording Demos

### Screen Recording

For video demos:

**macOS:**
```bash
# Use QuickTime Player
# File → New Screen Recording
```

**Linux:**
```bash
# Use SimpleScreenRecorder or OBS
sudo apt install simplescreenrecorder
```

**Windows:**
```bash
# Use Windows Game Bar
# Win + G
```

### Screenshots

For thesis figures:

**In Web UI:**
- Use browser screenshot tools
- Or press `Print Screen` / `Cmd+Shift+4`

**In Jupyter:**
```python
# Save figure
fig.savefig('thesis_figure.png', dpi=300, bbox_inches='tight')
```

## Best Practices

### For Presentations

1. **Test beforehand** - Run all demos before presenting
2. **Have backups** - Screenshots, videos, or slides
3. **Know the numbers** - Memorize key metrics (avg moves, times)
4. **Prepare explanations** - Be ready to explain any algorithm
5. **Manage time** - Use quick scrambles (depth 10) for demos

### For Teaching

1. **Start simple** - Use interactive solver with depth 5-7
2. **Build up** - Progress to comparison mode
3. **Visualize** - Use 3D visualizations extensively
4. **Hands-on** - Let students try the web interface
5. **Relate** - Connect to concepts (search, heuristics, optimization)

### For Research

1. **Document** - Record exact parameters (seed, depth, timeouts)
2. **Export** - Save all results to JSON/Markdown
3. **Reproduce** - Use same seeds for reproducibility
4. **Batch test** - Use large sample sizes (100+ scrambles)
5. **Validate** - Compare with Phase 8 comprehensive results

## Advanced Tips

### Custom Scrambles

```python
# In Python/Jupyter
from src.cube.rubik_cube import RubikCube

cube = RubikCube()
# Apply specific sequence
for move in ["R", "U", "R'", "U'", "F2"]:
    cube.apply_move(move)
```

### Performance Tuning

For faster demos:
- Use Thistlethwaite (fastest)
- Reduce scramble depth
- Increase timeout if needed

For optimal solutions:
- Use Korf (but be patient)
- Reduce max_depth for speed
- Use depth 10-12 scrambles

### Exporting Results

```bash
# CLI comparison
python demos/phase9/algorithm_comparison_cli.py --depth 10 --export results.json

# Benchmark
python demos/phase9/benchmark_demo.py --n-scrambles 50 --export benchmark.md
```

## FAQ

**Q: Which demo should I use for thesis defense?**
A: Web UI comparison mode - it's visual, interactive, and comprehensive.

**Q: How do I make demos faster?**
A: Use Thistlethwaite algorithm and depth 10 scrambles.

**Q: Can I use these demos offline?**
A: Yes, all demos work offline after installing dependencies.

**Q: How do I export figures for thesis?**
A: Web UI: screenshot, Jupyter: `fig.savefig()`, CLI: use --export

**Q: What if Korf times out during presentation?**
A: Have a pre-computed result ready, or use depth 8-10 scrambles.

## Support

For issues or questions:
- Check troubleshooting section above
- Review README files in each directory
- Check Phase 9 plan: `PHASE9_PLAN.md`

## Author

Alex Toska
University of Patras
Phase 9: Demos & UI Visualization
2025
