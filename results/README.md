# Results Directory

This directory contains experimental results, performance benchmarks, and analysis outputs.

## Structure

Results will be organized by experiment type and date:

```
results/
├── benchmarks/          # Performance benchmark results
├── experiments/         # Experimental analysis
├── comparisons/         # Algorithm comparison results
├── visualizations/      # Generated plots and charts
└── reports/            # Analysis reports and summaries
```

## Contents

### benchmarks/
Performance measurements for each algorithm:
- Execution time
- Memory usage
- Solution length statistics
- Success rates

**Format**: CSV files with benchmark data

### experiments/
Results from specific experiments:
- Heuristic function comparisons
- Parameter tuning results
- Ablation studies
- Scalability tests

**Format**: JSON with experiment metadata + CSV data

### comparisons/
Direct comparisons between algorithms:
- Thistlethwaite vs Kociemba vs Korf
- Solution quality comparison
- Time-quality tradeoffs
- Statistical significance tests

**Format**: CSV data + matplotlib figures

### visualizations/
Generated plots and charts:
- Performance graphs
- Solution length distributions
- Time complexity plots
- Comparative bar charts

**Format**: PNG, PDF, SVG

### reports/
Analysis summaries and reports:
- Executive summaries
- Detailed analysis documents
- Thesis chapter drafts
- Presentation materials

**Format**: Markdown, PDF

## Usage

### Running Benchmarks

```python
from src.evaluation.benchmark import run_benchmark

# Run benchmark suite
results = run_benchmark(
    algorithm='thistlethwaite',
    test_cases='data/test_cases/benchmark_20.json',
    output_dir='results/benchmarks/'
)
```

### Generating Visualizations

```python
from src.evaluation.visualize import plot_comparison

# Create comparison plot
plot_comparison(
    results=['results/benchmarks/thistlethwaite.csv',
             'results/benchmarks/kociemba.csv',
             'results/benchmarks/korf.csv'],
    output='results/visualizations/algorithm_comparison.png'
)
```

### Analysis Reports

```python
from src.evaluation.analysis import generate_report

# Generate analysis report
generate_report(
    benchmark_dir='results/benchmarks/',
    output='results/reports/phase_analysis.md'
)
```

## Experiments Timeline

### Phase 4 (Weeks 9-10): Distance Estimator & Heuristics
- Heuristic function evaluation
- Distance estimation accuracy
- Comparative analysis

### Phase 5 (Weeks 11-12): Testing & Optimization
- Performance benchmarking
- Memory profiling
- Optimization results

### Phase 6 (Weeks 13-14): Comparative Analysis
- Full algorithm comparison
- Statistical analysis
- Final visualizations

## Data Format

### Benchmark CSV Format
```csv
algorithm,test_case,scramble_length,solution_length,time_ms,memory_mb,solved
thistlethwaite,test_001,20,45,123.4,12.5,true
```

### Experiment JSON Format
```json
{
  "experiment": "heuristic_comparison",
  "date": "2024-03-15",
  "parameters": {...},
  "results": [...]
}
```

## Notes

- Results files are excluded from git (see .gitignore)
- Large result sets should be compressed
- Keep raw data separate from processed data
- Document experiments thoroughly in metadata files

## References

- Benchmark methodology from thesis design
- Statistical analysis guidelines
- Visualization best practices
