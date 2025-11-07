# Phase 9 CLI Demos

Enhanced command-line demos for the Rubik's Cube solver project.

## Overview

These demos provide interactive and visual ways to explore the three implemented solving algorithms:
- **Thistlethwaite's Algorithm** (1981)
- **Kociemba's Algorithm** (1992)
- **Korf's IDA*** (1997)

## Demo Scripts

### 1. Interactive Solver (`interactive_solver.py`)

Menu-driven interface for solving cubes with step-by-step visualization.

**Features:**
- Interactive menu system
- Multiple scramble options (random, seeded, custom)
- Solve with any algorithm
- Step-by-step solution playback
- Colorized output (with `rich` library)

**Usage:**
```bash
python demos/phase9/interactive_solver.py
```

**Example Session:**
```
Main Menu
1. Scramble cube (random)
2. Scramble cube (with seed)
3. Apply custom moves
4. Solve with Thistlethwaite
5. Solve with Kociemba
6. Solve with Korf IDA*
7. View solution (step-by-step)
8. Reset cube
9. View cube state
0. Exit
```

### 2. Algorithm Comparison CLI (`algorithm_comparison_cli.py`)

Run all three algorithms on the same scramble and compare results.

**Features:**
- Side-by-side algorithm comparison
- Detailed metrics (moves, time, memory, nodes)
- Winner analysis (fewest moves, fastest, least memory)
- Export results (JSON or Markdown)
- Formatted tables (with `rich` library)

**Usage:**
```bash
python demos/phase9/algorithm_comparison_cli.py [OPTIONS]
```

**Options:**
- `--depth DEPTH`: Scramble depth (default: 10)
- `--seed SEED`: Random seed (default: 42)
- `--thistle-timeout T`: Thistlethwaite timeout in seconds (default: 30)
- `--kociemba-timeout T`: Kociemba timeout in seconds (default: 60)
- `--korf-timeout T`: Korf timeout in seconds (default: 120)
- `--korf-max-depth D`: Korf max search depth (default: 20)
- `--export FILE`: Export results to JSON or Markdown

**Example:**
```bash
# Compare algorithms on a 10-move scramble
python demos/phase9/algorithm_comparison_cli.py --depth 10 --seed 42

# Export results to JSON
python demos/phase9/algorithm_comparison_cli.py --depth 15 --export results.json

# Export summary to Markdown
python demos/phase9/algorithm_comparison_cli.py --depth 10 --export summary.md
```

### 3. Animation Demo (`animation_demo.py`)

Play back solution sequences move-by-move with visual feedback.

**Features:**
- Animated solution playback
- Adjustable speed
- Visual cube state after each move
- Support for all algorithms

**Usage:**
```bash
python demos/phase9/animation_demo.py [OPTIONS]
```

**Options:**
- `--algorithm ALGO`: Algorithm to use (thistlethwaite, kociemba, korf)
- `--depth DEPTH`: Scramble depth (default: 10)
- `--seed SEED`: Random seed (default: 42)
- `--speed SPEED`: Seconds per move (default: 1.0)

**Examples:**
```bash
# Animate Kociemba solution at default speed
python demos/phase9/animation_demo.py --algorithm kociemba --depth 10

# Fast animation (0.3s per move)
python demos/phase9/animation_demo.py --algorithm thistlethwaite --speed 0.3

# Slow animation (2s per move) for presentation
python demos/phase9/animation_demo.py --algorithm korf --depth 8 --speed 2.0
```

### 4. Benchmark Demo (`benchmark_demo.py`)

Quick performance benchmark of all algorithms.

**Features:**
- Test multiple scrambles
- Statistical summary (avg, min, max)
- Winner analysis
- Export results

**Usage:**
```bash
python demos/phase9/benchmark_demo.py [OPTIONS]
```

**Options:**
- `--n-scrambles N`: Number of scrambles to test (default: 10)
- `--depth DEPTH`: Scramble depth (default: 10)
- `--seed SEED`: Random seed (default: 42)
- `--export FILE`: Export results to JSON or Markdown

**Examples:**
```bash
# Quick 10-scramble benchmark
python demos/phase9/benchmark_demo.py --n-scrambles 10 --depth 10

# Larger 50-scramble test
python demos/phase9/benchmark_demo.py --n-scrambles 50 --depth 12

# Export results
python demos/phase9/benchmark_demo.py --n-scrambles 20 --export benchmark.json
```

## Dependencies

### Required
- Python 3.8+
- NumPy
- Project source code (`src/` directory)

### Optional (for enhanced output)
- `rich` - Beautiful CLI formatting, tables, progress bars

Install optional dependencies:
```bash
pip install rich
```

Or install all Phase 9 dependencies:
```bash
pip install -r requirements.txt
```

## Tips & Best Practices

### For Interactive Solver
- Start with `scramble random` and `depth 10` for quick testing
- Use seeded scrambles for reproducible experiments
- Try step-by-step solution viewing to understand algorithm behavior

### For Algorithm Comparison
- Use `depth 7-10` for quick comparisons
- Use `depth 15+` to stress-test Korf algorithm
- Export results for later analysis or thesis inclusion
- Use the same seed to reproduce exact comparisons

### For Animation Demo
- Use `speed 0.5` for comfortable viewing
- Use `speed 2.0` for presentations (gives time to explain)
- Use `speed 0.2` for fast demos
- Best with Thistlethwaite or Kociemba (Korf can be very long)

### For Benchmark
- Use `n-scrambles 10` for quick tests
- Use `n-scrambles 100+` for statistical significance
- Export to JSON for integration with Phase 8 results
- Export to Markdown for thesis inclusion

## Scramble Depth Guidelines

| Depth | Difficulty | Thistlethwaite | Kociemba | Korf |
|-------|-----------|----------------|----------|------|
| 5-7   | Easy      | <0.1s          | <1s      | <2s  |
| 8-10  | Medium    | <0.3s          | 1-3s     | 2-10s|
| 11-15 | Hard      | <0.5s          | 2-8s     | 5-60s|
| 16-20 | Very Hard | <1s            | 5-20s    | 10s-5min|
| 20+   | Extreme   | <2s            | 10-60s   | May timeout|

## Troubleshooting

### "Module not found" errors
Make sure you're running from the project root:
```bash
cd /home/user/rubicCubeThesis
python demos/phase9/interactive_solver.py
```

### Korf timeouts
- Increase `--korf-timeout` (try 300 for 5 minutes)
- Reduce scramble depth (try 10-12 moves)
- Reduce `--korf-max-depth` if you don't need optimality

### Rich library not found
The demos work without `rich`, but output is less pretty:
```bash
pip install rich
```

### Performance issues
- Close other applications
- Use Thistlethwaite for quick demos
- Reduce scramble depth for Korf

## Examples from Thesis

These command sequences were used in the thesis:

```bash
# Figure 1: Algorithm comparison on standard scramble
python demos/phase9/algorithm_comparison_cli.py --depth 10 --seed 42

# Table 1: Performance statistics
python demos/phase9/benchmark_demo.py --n-scrambles 100 --depth 10 --export thesis_benchmark.json

# Demo for thesis defense
python demos/phase9/animation_demo.py --algorithm kociemba --depth 8 --speed 1.5
```

## See Also

- **Web UI**: Run `streamlit run ui/app.py` for interactive browser interface
- **Jupyter Notebooks**: `notebooks/` directory for deep-dive tutorials
- **Phase 8 Demos**: `demos/phase8_comparison_demo.py` for comprehensive testing
- **Documentation**: `docs/phase9/` for detailed guides

## Author

Alex Toska
University of Patras
Phase 9: Demos & UI Visualization
2025
