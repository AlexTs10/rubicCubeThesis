# Chapter 07: Evaluation - Corrected Specification

## Overview
- Title: `Πειραματική Αξιολόγηση`
- Goal: present a reproducible comparison of the corrected pure Thistlethwaite path, the Kociemba two-phase solver, and the exact Korf optimal backend under a common scramble corpus
- Source of truth: `results/benchmarks/thesis/thesis_results_combined.json`
- Figure directory used by LaTeX: `thesis/figures/`

## Methodology
- Dataset: 100 scrambles total, with 25 scrambles each at nominal depths 5, 10, 15, and 20.
- Environment: Apple M3, 16 GB RAM, macOS 26.2, Python 3.12.2.
- Time budgets:
  - Thistlethwaite: 30 s
  - Kociemba: 60 s
  - Korf: 120 s
- Korf benchmark path: external exact backend via `src/korf/optimal_solver.py`, with timeout enforced by the local wrapper.
- Metrics:
  - success rate
  - solution length
  - solve time
  - process RSS delta
  - nodes explored for Korf

## Correct Tables

### Success Rates
| Depth | Thistlethwaite | Kociemba | Korf IDA* |
|-------|----------------|----------|-----------|
| 5 | 25/25 (100%) | 25/25 (100%) | 25/25 (100%) |
| 10 | 25/25 (100%) | 25/25 (100%) | 25/25 (100%) |
| 15 | 25/25 (100%) | 25/25 (100%) | 25/25 (100%) |
| 20 | 25/25 (100%) | 25/25 (100%) | 22/25 (88%) |

### Average Solution Length
| Depth | Thistlethwaite | Kociemba | Korf IDA* |
|-------|----------------|----------|-----------|
| 5 | 8.76 | 5.60 | 3.96 |
| 10 | 24.84 | 9.92 | 7.40 |
| 15 | 30.00 | 19.84 | 11.56 |
| 20 | 30.88 | 21.96 | 14.18 |

### Average Solve Time (successful solves only)
| Depth | Thistlethwaite | Kociemba | Korf IDA* |
|-------|----------------|----------|-----------|
| 5 | 0.054 s | 0.374 s | 0.001 s |
| 10 | 1.054 s | 0.201 s | 0.002 s |
| 15 | 2.029 s | 8.163 s | 0.424 s |
| 20 | 1.821 s | 9.749 s | 11.229 s |

### Korf Nodes Explored
| Depth | Avg Nodes (successful solves only) |
|-------|------------------------------------|
| 5 | 55.00 |
| 10 | 147.64 |
| 15 | 96,177.96 |
| 20 | 6,606,970.64 |

## Key Claims The Chapter May Make
- Thistlethwaite and Kociemba both achieved 100% success on the 100-scramble benchmark corpus.
- Korf remained fully successful through depth 15 and dropped only at depth 20, where 3 of 25 cases hit the enforced 120-second timeout.
- Korf produced the shortest solutions whenever it completed, confirming its role as the optimal baseline.
- Kociemba remained the strongest overall compromise between solution quality, reliability, and resource cost.
- The corrected pure Thistlethwaite implementation is now empirically reliable, but its solution lengths remain substantially longer than those of Kociemba and Korf.
- Korf’s node count and memory usage grow sharply at depth 20, illustrating the practical cost of exact optimal search.

## Claims The Chapter Must Not Make
- Do not say Korf becomes intractable beyond depth 10.
- Do not say Thistlethwaite is hybrid or fallback-assisted in the benchmark path.
- Do not say Kociemba is always the fastest algorithm in this corpus.
- Do not describe the benchmarked Korf path as the internal composite-heuristic solver.

## Figures
- `fig1_solution_length_boxplot.png`
- `fig2_time_comparison.png`
- `fig3_memory_comparison.png`
- `fig4_success_rate.png`
- `fig5_solution_distribution.png`
- `fig6_nodes_comparison.png`
- `fig7_performance_vs_depth.png`

## Recommendation Table
| Use Case | Recommended | Rationale |
|----------|-------------|-----------|
| Good practical default | Kociemba | 100% success, shorter solutions than Thistlethwaite, much lower memory cost than Korf |
| Exact optimal solution / verification | Korf IDA* | Optimal solutions when search completes within 120 s |
| Educational group-reduction solver | Thistlethwaite | Pure four-phase structure, 100% success in the corrected implementation |

## Supporting Files
- `src/evaluation/algorithm_comparison.py`
- `scripts/benchmarks/regenerate_thesis_benchmarks.py`
- `scripts/benchmarks/analyze_thesis_data.py`
- `src/evaluation/visualizations.py`
- `results/benchmarks/thesis/thesis_bench_d5.json`
- `results/benchmarks/thesis/thesis_bench_d10.json`
- `results/benchmarks/thesis/thesis_bench_d15.json`
- `results/benchmarks/thesis/thesis_bench_d20.json`
- `results/benchmarks/thesis/thesis_results_combined.json`
