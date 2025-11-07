"""Test validation suite with Korf IDA* solver"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluation.validation import ValidationSuite
from src.korf.a_star import IDAStarSolver
from src.korf.composite_heuristic import create_heuristic

print("Initializing validation suite...")
suite = ValidationSuite()

print("Creating Korf IDA* solver...")
korf_solver = IDAStarSolver(
    heuristic=create_heuristic('manhattan'),  # Use Manhattan for speed
    max_depth=25,
    timeout=120.0  # 2 minutes timeout
)

print("\nRunning validation tests...")
results = suite.run_all_validations(algorithms=[korf_solver])

# Print report
suite.print_report(results)

# Export report
suite.export_validation_report(results, 'results/validation_report.md')

print("\n✓ Validation complete!")
