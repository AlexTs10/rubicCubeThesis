#!/usr/bin/env python3
"""
Comprehensive Test Runner - Phase 8

This script orchestrates large-scale testing of Rubik's Cube solving algorithms.
Supports multiple test configurations, progress tracking, checkpointing, and
comprehensive result export.

Features:
- Configurable test sizes (10, 100, 1000+ scrambles)
- Multiple scramble depths (5, 10, 15, 20 moves)
- Progress tracking with ETA
- Checkpoint/resume capability
- Graceful error handling
- JSON export for analysis

Usage:
    # Quick test (10 scrambles)
    python scripts/run_comprehensive_tests.py --preset quick

    # Medium test (100 scrambles)
    python scripts/run_comprehensive_tests.py --preset medium

    # Full thesis test (1000 scrambles)
    python scripts/run_comprehensive_tests.py --preset full

    # Custom configuration
    python scripts/run_comprehensive_tests.py --scrambles 50 --depths 5 10 15

    # Resume from checkpoint
    python scripts/run_comprehensive_tests.py --resume results/checkpoint_latest.json
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.algorithm_comparison import AlgorithmComparison, ComparisonResult


@dataclass
class TestConfiguration:
    """Configuration for a test run."""
    scrambles_per_depth: int
    scramble_depths: List[int]
    seed: int
    output_dir: str
    checkpoint_interval: int = 10  # Save checkpoint every N scrambles
    algorithms: List[str] = None  # None = all available

    def total_tests(self) -> int:
        """Calculate total number of tests."""
        return self.scrambles_per_depth * len(self.scramble_depths)


@dataclass
class TestProgress:
    """Track progress during test run."""
    total_tests: int
    completed_tests: int
    current_depth: int
    current_scramble: int
    start_time: float
    results: List[Dict] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []

    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        return (self.completed_tests / self.total_tests * 100) if self.total_tests > 0 else 0.0

    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds."""
        return time.time() - self.start_time

    def estimated_remaining_time(self) -> float:
        """Estimate remaining time in seconds."""
        if self.completed_tests == 0:
            return 0.0

        elapsed = self.elapsed_time()
        rate = self.completed_tests / elapsed
        remaining_tests = self.total_tests - self.completed_tests
        return remaining_tests / rate if rate > 0 else 0.0

    def format_time(self, seconds: float) -> str:
        """Format seconds as human-readable time."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    def print_progress(self):
        """Print current progress."""
        pct = self.progress_percentage()
        elapsed = self.format_time(self.elapsed_time())
        remaining = self.format_time(self.estimated_remaining_time())

        bar_length = 40
        filled = int(bar_length * pct / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f"\r[{bar}] {pct:.1f}% | {self.completed_tests}/{self.total_tests} | "
              f"Elapsed: {elapsed} | ETA: {remaining}", end='', flush=True)


class ComprehensiveTestRunner:
    """
    Orchestrates large-scale algorithm testing with progress tracking and checkpointing.
    """

    def __init__(self, config: TestConfiguration):
        """
        Initialize test runner.

        Args:
            config: Test configuration
        """
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.comparison = None
        self.progress = None

    def run(self, resume_from: Optional[str] = None) -> str:
        """
        Run comprehensive tests.

        Args:
            resume_from: Path to checkpoint file to resume from

        Returns:
            Path to output file
        """
        print("=" * 80)
        print("COMPREHENSIVE TEST RUNNER - PHASE 8")
        print("=" * 80)
        print()

        # Load checkpoint or start fresh
        if resume_from and Path(resume_from).exists():
            self._resume_from_checkpoint(resume_from)
        else:
            self._start_fresh()

        # Print configuration
        self._print_configuration()

        # Initialize comparison framework
        print("\nInitializing comparison framework...")
        self.comparison = AlgorithmComparison(
            thistlethwaite_timeout=30.0,
            kociemba_timeout=60.0,
            korf_timeout=120.0,
            korf_max_depth=20
        )
        print()

        # Run tests
        print("=" * 80)
        print("RUNNING TESTS")
        print("=" * 80)
        print()

        try:
            self._run_tests()
            print("\n\n")
            print("=" * 80)
            print("✓ TEST RUN COMPLETED SUCCESSFULLY")
            print("=" * 80)
        except KeyboardInterrupt:
            print("\n\n")
            print("=" * 80)
            print("⚠ TEST RUN INTERRUPTED BY USER")
            print("=" * 80)
            checkpoint_path = self._save_checkpoint()
            print(f"\nCheckpoint saved: {checkpoint_path}")
            print(f"Resume with: --resume {checkpoint_path}")
            return checkpoint_path
        except Exception as e:
            print("\n\n")
            print("=" * 80)
            print(f"✗ TEST RUN FAILED: {e}")
            print("=" * 80)
            checkpoint_path = self._save_checkpoint()
            print(f"\nCheckpoint saved: {checkpoint_path}")
            raise

        # Save final results
        output_path = self._save_results()
        print(f"\nResults saved: {output_path}")

        # Print summary
        self._print_summary()

        return output_path

    def _start_fresh(self):
        """Start a fresh test run."""
        total_tests = self.config.total_tests()
        self.progress = TestProgress(
            total_tests=total_tests,
            completed_tests=0,
            current_depth=self.config.scramble_depths[0],
            current_scramble=0,
            start_time=time.time()
        )

    def _resume_from_checkpoint(self, checkpoint_path: str):
        """Resume from a checkpoint file."""
        print(f"Resuming from checkpoint: {checkpoint_path}")

        with open(checkpoint_path, 'r') as f:
            data = json.load(f)

        # Restore progress
        self.progress = TestProgress(
            total_tests=data['progress']['total_tests'],
            completed_tests=data['progress']['completed_tests'],
            current_depth=data['progress']['current_depth'],
            current_scramble=data['progress']['current_scramble'],
            start_time=data['progress']['start_time'],
            results=data['results']
        )

        print(f"Resuming at test {self.progress.completed_tests + 1}/{self.progress.total_tests}")
        print()

    def _print_configuration(self):
        """Print test configuration."""
        print("Configuration:")
        print(f"  Scrambles per depth: {self.config.scrambles_per_depth}")
        print(f"  Scramble depths:     {self.config.scramble_depths}")
        print(f"  Total tests:         {self.config.total_tests()}")
        print(f"  Random seed:         {self.config.seed}")
        print(f"  Output directory:    {self.config.output_dir}")
        print(f"  Checkpoint interval: every {self.config.checkpoint_interval} tests")

    def _run_tests(self):
        """Run all tests with progress tracking."""
        test_id = self.progress.completed_tests

        for depth in self.config.scramble_depths:
            self.progress.current_depth = depth

            for scramble_num in range(self.config.scrambles_per_depth):
                # Skip if already completed (resuming from checkpoint)
                if test_id < len(self.progress.results):
                    test_id += 1
                    self.progress.completed_tests = test_id
                    self.progress.print_progress()
                    continue

                self.progress.current_scramble = scramble_num

                # Generate scramble
                from src.cube.rubik_cube import RubikCube
                cube = RubikCube()
                seed = self.config.seed + test_id
                scramble = cube.scramble(moves=depth, seed=seed)

                # Store scramble info
                cube._scramble_depth = depth
                cube._scramble_moves = scramble

                # Run comparison (quietly)
                result = self.comparison.compare_on_scramble(cube, scramble_id=test_id)

                # Store result
                self.progress.results.append(asdict(result))
                self.progress.completed_tests += 1
                test_id += 1

                # Update progress bar
                self.progress.print_progress()

                # Checkpoint if needed
                if self.progress.completed_tests % self.config.checkpoint_interval == 0:
                    self._save_checkpoint(quiet=True)

    def _save_checkpoint(self, quiet: bool = False) -> str:
        """Save checkpoint file."""
        checkpoint_data = {
            'config': asdict(self.config),
            'progress': {
                'total_tests': self.progress.total_tests,
                'completed_tests': self.progress.completed_tests,
                'current_depth': self.progress.current_depth,
                'current_scramble': self.progress.current_scramble,
                'start_time': self.progress.start_time
            },
            'results': self.progress.results,
            'timestamp': datetime.now().isoformat()
        }

        checkpoint_path = self.output_dir / "checkpoint_latest.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        if not quiet:
            print(f"\nCheckpoint saved: {checkpoint_path}")

        return str(checkpoint_path)

    def _save_results(self) -> str:
        """Save final results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = self.output_dir / f"comprehensive_test_{timestamp}.json"

        results_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'config': asdict(self.config),
                'total_tests': self.progress.total_tests,
                'completed_tests': self.progress.completed_tests,
                'total_time_seconds': self.progress.elapsed_time()
            },
            'results': self.progress.results
        }

        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2)

        return str(output_path)

    def _print_summary(self):
        """Print test summary."""
        print("\n")
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        # Calculate statistics by algorithm
        # Map algorithm names to result keys
        algorithm_map = {
            'Thistlethwaite': 'thistlethwaite',
            'Kociemba': 'kociemba',
            'Korf_IDA*': 'korf'
        }

        for algo_name, result_key in algorithm_map.items():
            results = [r[result_key] for r in self.progress.results]
            successful = [r for r in results if r['solved']]

            print(f"\n{algo_name}:")
            print(f"  Tests completed: {len(results)}")
            print(f"  Successful:      {len(successful)} ({len(successful)/len(results)*100:.1f}%)")

            if successful:
                avg_moves = sum(r['solution_length'] for r in successful) / len(successful)
                avg_time = sum(r['time_seconds'] for r in successful) / len(successful)
                print(f"  Avg moves:       {avg_moves:.1f}")
                print(f"  Avg time:        {avg_time:.3f}s")

        print("\n" + "=" * 80)


def create_preset_config(preset: str, output_dir: str = "results") -> TestConfiguration:
    """
    Create a preset test configuration.

    Args:
        preset: 'quick', 'medium', 'full', or 'thesis'
        output_dir: Output directory for results

    Returns:
        TestConfiguration
    """
    presets = {
        'quick': TestConfiguration(
            scrambles_per_depth=10,
            scramble_depths=[5, 7, 10],
            seed=42,
            output_dir=output_dir,
            checkpoint_interval=5
        ),
        'medium': TestConfiguration(
            scrambles_per_depth=50,
            scramble_depths=[5, 10, 15],
            seed=42,
            output_dir=output_dir,
            checkpoint_interval=10
        ),
        'full': TestConfiguration(
            scrambles_per_depth=100,
            scramble_depths=[5, 10, 15, 20],
            seed=42,
            output_dir=output_dir,
            checkpoint_interval=10
        ),
        'thesis': TestConfiguration(
            scrambles_per_depth=250,
            scramble_depths=[5, 10, 15, 20],
            seed=42,
            output_dir=output_dir,
            checkpoint_interval=25
        )
    }

    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}. Choose from {list(presets.keys())}")

    return presets[preset]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run comprehensive algorithm comparison tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (30 scrambles)
  python scripts/run_comprehensive_tests.py --preset quick

  # Medium test (150 scrambles)
  python scripts/run_comprehensive_tests.py --preset medium

  # Full test (400 scrambles)
  python scripts/run_comprehensive_tests.py --preset full

  # Thesis test (1000 scrambles)
  python scripts/run_comprehensive_tests.py --preset thesis

  # Custom configuration
  python scripts/run_comprehensive_tests.py --scrambles 50 --depths 5 10 15 20

  # Resume from checkpoint
  python scripts/run_comprehensive_tests.py --resume results/checkpoint_latest.json
        """
    )

    parser.add_argument(
        '--preset',
        choices=['quick', 'medium', 'full', 'thesis'],
        help='Use a preset configuration'
    )
    parser.add_argument(
        '--scrambles',
        type=int,
        help='Number of scrambles per depth'
    )
    parser.add_argument(
        '--depths',
        type=int,
        nargs='+',
        help='Scramble depths to test (e.g., 5 10 15 20)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    parser.add_argument(
        '--output-dir',
        default='results',
        help='Output directory for results'
    )
    parser.add_argument(
        '--checkpoint-interval',
        type=int,
        default=10,
        help='Save checkpoint every N tests'
    )
    parser.add_argument(
        '--resume',
        help='Resume from checkpoint file'
    )

    args = parser.parse_args()

    # Create configuration
    if args.preset:
        config = create_preset_config(args.preset, args.output_dir)
    elif args.scrambles and args.depths:
        config = TestConfiguration(
            scrambles_per_depth=args.scrambles,
            scramble_depths=args.depths,
            seed=args.seed,
            output_dir=args.output_dir,
            checkpoint_interval=args.checkpoint_interval
        )
    elif args.resume:
        # Configuration will be loaded from checkpoint
        config = TestConfiguration(
            scrambles_per_depth=0,
            scramble_depths=[],
            seed=42,
            output_dir=args.output_dir
        )
    else:
        parser.error('Must specify either --preset, --scrambles with --depths, or --resume')

    # Run tests
    runner = ComprehensiveTestRunner(config)
    output_path = runner.run(resume_from=args.resume)

    print(f"\n✓ Results saved to: {output_path}")
    print("\nNext steps:")
    print("  1. Run statistical analysis: python scripts/analyze_results.py " + output_path)
    print("  2. Generate visualizations: python scripts/generate_visualizations.py " + output_path)
    print("  3. Generate thesis tables: python scripts/export_thesis_tables.py " + output_path)


if __name__ == '__main__':
    main()
