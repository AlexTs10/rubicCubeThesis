"""
Visualization Module - Phase 8

This module generates publication-quality charts and graphs for thesis presentation.
Creates various plot types comparing algorithm performance across metrics.

Features:
- Box plots (solution length distributions)
- Bar charts (time, memory comparison)
- Line charts (performance vs scramble depth)
- Scatter plots (nodes explored)
- Histograms (distribution analysis)
- Export to PNG/PDF for thesis

Usage:
    from src.evaluation.visualizations import VisualizationGenerator

    viz = VisualizationGenerator('results/comprehensive_test.json')
    viz.generate_all_figures(output_dir='figures/')
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

# Set publication-quality style
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.5)
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'


class VisualizationGenerator:
    """
    Generate publication-quality visualizations for thesis.
    """

    def __init__(self, results_path: str):
        """
        Initialize visualization generator.

        Args:
            results_path: Path to results JSON file
        """
        self.results_path = Path(results_path)
        self.data = self._load_results()
        self.algorithm_data = self._extract_algorithm_data()

        # Color scheme for algorithms
        self.colors = {
            'Thistlethwaite': '#3498db',  # Blue
            'Kociemba': '#e74c3c',        # Red
            'Korf_IDA*': '#2ecc71'        # Green
        }

    def _load_results(self) -> Dict:
        """Load results from JSON file."""
        with open(self.results_path, 'r') as f:
            return json.load(f)

    def _extract_algorithm_data(self) -> Dict:
        """Extract and organize data by algorithm."""
        algorithm_map = {
            'Thistlethwaite': 'thistlethwaite',
            'Kociemba': 'kociemba',
            'Korf_IDA*': 'korf'
        }

        # Initialize data for all algorithms
        data = {
            algo_name: {
                'solution_lengths': [],
                'times': [],
                'memories': [],
                'nodes': [],
                'scramble_depths': []
            }
            for algo_name in algorithm_map.keys()
        }

        for result in self.data['results']:
            scramble_depth = result['scramble_depth']

            for algo_name, result_key in algorithm_map.items():
                algo_result = result[result_key]

                if algo_result['solved']:
                    data[algo_name]['solution_lengths'].append(algo_result['solution_length'])
                    data[algo_name]['times'].append(algo_result['time_seconds'])
                    data[algo_name]['memories'].append(algo_result['memory_mb'])
                    data[algo_name]['scramble_depths'].append(scramble_depth)

                    if algo_result['nodes_explored'] is not None:
                        data[algo_name]['nodes'].append(algo_result['nodes_explored'])

        return data

    def generate_all_figures(self, output_dir: str = 'figures/'):
        """
        Generate all thesis figures.

        Args:
            output_dir: Directory to save figures
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print("Generating thesis figures...")
        print("=" * 70)

        # Figure 1: Solution Length Comparison (Box Plot)
        print("\n1. Solution Length Comparison (Box Plot)...")
        self.plot_solution_length_boxplot(
            str(output_path / 'fig1_solution_length_boxplot.png')
        )

        # Figure 2: Time Performance Comparison (Bar Chart)
        print("2. Time Performance Comparison (Bar Chart)...")
        self.plot_time_comparison_bar(
            str(output_path / 'fig2_time_comparison.png')
        )

        # Figure 3: Memory Usage Comparison (Bar Chart)
        print("3. Memory Usage Comparison (Bar Chart)...")
        self.plot_memory_comparison_bar(
            str(output_path / 'fig3_memory_comparison.png')
        )

        # Figure 4: Success Rate Comparison (Bar Chart)
        print("4. Success Rate Comparison (Bar Chart)...")
        self.plot_success_rate_bar(
            str(output_path / 'fig4_success_rate.png')
        )

        # Figure 5: Solution Length Distribution (Histogram)
        print("5. Solution Length Distribution (Histogram)...")
        self.plot_solution_distribution_hist(
            str(output_path / 'fig5_solution_distribution.png')
        )

        # Figure 6: Nodes Explored Comparison (if available)
        if any(self.algorithm_data[algo]['nodes'] for algo in self.algorithm_data):
            print("6. Nodes Explored Comparison...")
            self.plot_nodes_comparison(
                str(output_path / 'fig6_nodes_comparison.png')
            )

        # Figure 7: Performance vs Scramble Depth (Line Chart)
        print("7. Performance vs Scramble Depth...")
        self.plot_performance_vs_depth(
            str(output_path / 'fig7_performance_vs_depth.png')
        )

        print("\n" + "=" * 70)
        print(f"✓ All figures saved to: {output_path}")
        print("\nFigures generated:")
        for fig_file in sorted(output_path.glob('fig*.png')):
            print(f"  - {fig_file.name}")

    def plot_solution_length_boxplot(self, output_path: str):
        """Generate box plot comparing solution lengths."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data
        data_to_plot = []
        labels = []
        colors_list = []

        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            lengths = self.algorithm_data[algo_name]['solution_lengths']
            if lengths:
                data_to_plot.append(lengths)
                labels.append(algo_name)
                colors_list.append(self.colors[algo_name])

        if not data_to_plot:
            print("  ⚠ No data available for box plot")
            return

        # Create box plot
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                        showmeans=True, meanline=True)

        # Color boxes
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Solution Length (moves)')
        ax.set_title('Solution Length Comparison')
        ax.grid(True, alpha=0.3)

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")

    def plot_time_comparison_bar(self, output_path: str):
        """Generate bar chart comparing average solve times."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate means
        algorithms = []
        times = []
        colors_list = []

        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            time_data = self.algorithm_data[algo_name]['times']
            if time_data:
                algorithms.append(algo_name)
                times.append(np.mean(time_data))
                colors_list.append(self.colors[algo_name])

        if not algorithms:
            print("  ⚠ No data available for time comparison")
            return

        # Create bar chart
        x_pos = np.arange(len(algorithms))
        bars = ax.bar(x_pos, times, color=colors_list, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}s',
                   ha='center', va='bottom', fontsize=12)

        ax.set_ylabel('Average Time (seconds)')
        ax.set_title('Algorithm Speed Comparison')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(algorithms)
        ax.grid(True, alpha=0.3, axis='y')

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")

    def plot_memory_comparison_bar(self, output_path: str):
        """Generate bar chart comparing memory usage."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate means
        algorithms = []
        memories = []
        colors_list = []

        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            memory_data = self.algorithm_data[algo_name]['memories']
            if memory_data:
                algorithms.append(algo_name)
                memories.append(np.mean(memory_data))
                colors_list.append(self.colors[algo_name])

        if not algorithms:
            print("  ⚠ No data available for memory comparison")
            return

        # Create bar chart
        x_pos = np.arange(len(algorithms))
        bars = ax.bar(x_pos, memories, color=colors_list, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f} MB',
                   ha='center', va='bottom', fontsize=12)

        ax.set_ylabel('Average Memory Usage (MB)')
        ax.set_title('Memory Usage Comparison')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(algorithms)
        ax.grid(True, alpha=0.3, axis='y')

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")

    def plot_success_rate_bar(self, output_path: str):
        """Generate bar chart comparing success rates."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate success rates
        total_tests = len(self.data['results'])

        algorithms = []
        success_rates = []
        colors_list = []

        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            solved_count = len(self.algorithm_data[algo_name]['solution_lengths'])
            success_rate = (solved_count / total_tests) * 100 if total_tests > 0 else 0

            algorithms.append(algo_name)
            success_rates.append(success_rate)
            colors_list.append(self.colors[algo_name])

        # Create bar chart
        x_pos = np.arange(len(algorithms))
        bars = ax.bar(x_pos, success_rates, color=colors_list, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=12)

        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Algorithm Success Rate Comparison')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(algorithms)
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis='y')

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")

    def plot_solution_distribution_hist(self, output_path: str):
        """Generate histogram showing solution length distributions."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot histogram for each algorithm
        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            lengths = self.algorithm_data[algo_name]['solution_lengths']
            if lengths:
                ax.hist(lengths, bins=20, alpha=0.5, label=algo_name,
                       color=self.colors[algo_name], edgecolor='black')

        ax.set_xlabel('Solution Length (moves)')
        ax.set_ylabel('Frequency')
        ax.set_title('Solution Length Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")

    def plot_nodes_comparison(self, output_path: str):
        """Generate box plot comparing nodes explored."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data
        data_to_plot = []
        labels = []
        colors_list = []

        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            nodes = self.algorithm_data[algo_name]['nodes']
            if nodes:
                data_to_plot.append(nodes)
                labels.append(algo_name)
                colors_list.append(self.colors[algo_name])

        if not data_to_plot:
            print("  ⚠ No node data available")
            return

        # Create box plot
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                        showmeans=True, meanline=True)

        # Color boxes
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Nodes Explored')
        ax.set_title('Search Efficiency Comparison (Nodes Explored)')
        ax.set_yscale('log')  # Log scale for better visualization
        ax.grid(True, alpha=0.3)

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")

    def plot_performance_vs_depth(self, output_path: str):
        """Generate line chart showing performance vs scramble depth."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate average solution length by depth for each algorithm
        for algo_name in ['Thistlethwaite', 'Kociemba', 'Korf_IDA*']:
            depths_data = defaultdict(list)

            for depth, length in zip(
                self.algorithm_data[algo_name]['scramble_depths'],
                self.algorithm_data[algo_name]['solution_lengths']
            ):
                depths_data[depth].append(length)

            if depths_data:
                depths = sorted(depths_data.keys())
                avg_lengths = [np.mean(depths_data[d]) for d in depths]

                ax.plot(depths, avg_lengths, marker='o', linewidth=2,
                       label=algo_name, color=self.colors[algo_name], markersize=8)

        ax.set_xlabel('Scramble Depth (moves)')
        ax.set_ylabel('Average Solution Length (moves)')
        ax.set_title('Algorithm Performance vs Scramble Depth')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.savefig(output_path)
        plt.close()
        print(f"  ✓ Saved: {output_path}")


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.evaluation.visualizations <results_file.json>")
        sys.exit(1)

    results_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'figures/'

    viz = VisualizationGenerator(results_path)
    viz.generate_all_figures(output_dir=output_dir)

    print("\n✓ Visualization complete!")
    print(f"\nFigures saved to: {output_dir}")
    print("\nRecommended thesis figures:")
    print("  - fig1_solution_length_boxplot.png  → Chapter 5: Results")
    print("  - fig2_time_comparison.png          → Chapter 5: Performance Analysis")
    print("  - fig4_success_rate.png             → Chapter 5: Algorithm Reliability")
    print("  - fig7_performance_vs_depth.png     → Chapter 6: Scalability Analysis")


if __name__ == '__main__':
    main()
