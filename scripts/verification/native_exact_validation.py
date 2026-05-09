"""Validation harness for the native exact solver."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
import random
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cube.rubik_cube import RubikCube
from src.kociemba.cubie import ALL_MOVES, CubieCube
from src.korf.native_coordinate_heuristic import NativeCoordinateHeuristic
from src.korf.native_exact_solver import MOVE_ORDER, NativeExactSolver
from src.korf.optimal_solver import KorfOptimalSolver, OPTIMAL_AVAILABLE


CANONICAL_PRESET_NAME = "canonical_3513_case_depth12"
CANONICAL_PRESET = {
    "exhaustive_depth": 3,
    "oracle_depths": [4, 5, 6, 7, 8, 9],
    "oracle_samples_per_depth": 2,
    "max_depth": 12,
    "timeout": 20.0,
    "seed": 42,
    "heuristic_cache_dir": "data/pattern_databases/native_exact",
    "corner_db_path": "data/pattern_databases/corner_db.pkl",
    "disable_corner_db": False,
}
SOURCE_ZIP_PRESET_NAME = "source_zip_smoke_no_corner_db"
SOURCE_ZIP_PRESET = {
    "exhaustive_depth": 2,
    "oracle_depths": [],
    "oracle_samples_per_depth": 0,
    "max_depth": 6,
    "timeout": 5.0,
    "seed": 42,
    "heuristic_cache_dir": "data/pattern_databases/native_exact",
    "corner_db_path": None,
    "disable_corner_db": True,
    "minimal_heuristic": True,
}


@dataclass
class ValidationFailure:
    category: str
    scramble: List[str]
    message: str
    expected_depth: int
    expected_depth_source: str
    case_category: str
    oracle_length: Optional[int] = None
    native_stats: Optional[Dict] = None
    oracle_stats: Optional[Dict] = None


@dataclass
class ValidationCase:
    scramble: List[str]
    expected_depth: int
    use_oracle: bool
    category: str


class ZeroHeuristic:
    """Source-ZIP smoke heuristic that avoids generated coordinate-table caches."""

    def __call__(self, cubie: CubieCube) -> int:
        return 0

    def breakdown(self, cubie: CubieCube) -> Dict[str, int]:
        return {"zero": 0}

    def get_statistics(self) -> Dict[str, object]:
        return {
            "mode": "zero_heuristic_source_zip_smoke",
            "corner_pattern_db_loaded": False,
            "corner_pattern_db_complete": False,
        }


def _state_key(cubie: CubieCube) -> bytes:
    return (
        cubie.corner_perm.tobytes()
        + cubie.corner_orient.tobytes()
        + cubie.edge_perm.tobytes()
        + cubie.edge_orient.tobytes()
    )


def _apply_scramble(scramble: Iterable[str]) -> RubikCube:
    cube = RubikCube()
    cube.apply_moves(list(scramble))
    return cube


def _is_redundant(prev_move: Optional[str], move: str) -> bool:
    if prev_move is None:
        return False

    prev_face = prev_move[0]
    face = move[0]
    if prev_face == face:
        return True

    opposite_pairs = (("U", "D"), ("F", "B"), ("L", "R"))
    for first, second in opposite_pairs:
        if prev_face == second and face == first:
            return True
    return False


def generate_exhaustive_corpus(max_depth: int) -> List[ValidationCase]:
    """Generate unique exact-depth states up to the requested depth."""
    start = CubieCube()
    queue = deque([(start, [], None)])
    seen = {_state_key(start)}
    corpus: List[ValidationCase] = []

    while queue:
        cubie, path, last_move = queue.popleft()
        depth = len(path)
        if depth == max_depth:
            continue

        for move in MOVE_ORDER:
            if _is_redundant(last_move, move):
                continue

            next_cubie = cubie.multiply(ALL_MOVES[move])
            key = _state_key(next_cubie)
            if key in seen:
                continue

            next_path = path + [move]
            seen.add(key)
            corpus.append(
                ValidationCase(
                    scramble=next_path,
                    expected_depth=len(next_path),
                    use_oracle=False,
                    category="exhaustive",
                )
            )
            queue.append((next_cubie, next_path, move))

    return corpus


def generate_random_corpus(
    *,
    depths: Sequence[int],
    samples_per_depth: int,
    seed: int,
) -> List[ValidationCase]:
    """Generate reproducible deeper samples for oracle agreement."""
    rng = random.Random(seed)
    corpus: List[ValidationCase] = []
    seen = set()
    moves = list(MOVE_ORDER)

    for depth in depths:
        count = 0
        while count < samples_per_depth:
            scramble: List[str] = []
            last_move: Optional[str] = None
            while len(scramble) < depth:
                move = rng.choice(moves)
                if _is_redundant(last_move, move):
                    continue
                scramble.append(move)
                last_move = move

            cubie = CubieCube()
            for move in scramble:
                cubie = cubie.multiply(ALL_MOVES[move])
            key = _state_key(cubie)
            if key in seen:
                continue

            seen.add(key)
            corpus.append(
                ValidationCase(
                    scramble=scramble,
                    expected_depth=depth,
                    use_oracle=True,
                    category="oracle_sample",
                )
            )
            count += 1

    return corpus


def build_corpus_generation(
    *,
    exhaustive_depth: int,
    oracle_depths: Sequence[int],
    oracle_samples_per_depth: int,
    seed: int,
    preset: Optional[str] = None,
) -> Dict[str, object]:
    """Capture the exact corpus recipe in every generated report."""
    corpus_generation: Dict[str, object] = {
        "exhaustive_depth": exhaustive_depth,
        "oracle_depths": list(oracle_depths),
        "oracle_samples_per_depth": oracle_samples_per_depth,
        "seed": seed,
    }
    if preset is not None:
        corpus_generation["preset"] = preset
    return corpus_generation


def apply_preset(args: argparse.Namespace) -> argparse.Namespace:
    """Expand a named preset into the concrete validation parameters."""
    if args.preset == "canonical":
        for key, value in CANONICAL_PRESET.items():
            setattr(args, key, list(value) if isinstance(value, tuple) else value)
    elif args.preset == "source-zip":
        for key, value in SOURCE_ZIP_PRESET.items():
            setattr(args, key, list(value) if isinstance(value, tuple) else value)
    return args


def validate_corpus(
    corpus: Sequence[ValidationCase],
    *,
    corpus_generation: Dict[str, object],
    use_oracle: bool,
    max_depth: int,
    timeout: float,
    heuristic_cache_dir: str,
    corner_db_path: Optional[str],
    disable_corner_db: bool,
    minimal_heuristic: bool = False,
    require_corner_db: bool = False,
) -> Dict:
    oracle_required_cases = sum(1 for case in corpus if case.use_oracle)
    if oracle_required_cases and not use_oracle:
        raise ValueError(
            f"{oracle_required_cases} oracle-dependent validation cases require "
            "the external optimal oracle. Install the RubikOptimal backend or "
            "run --preset source-zip for the source-contained smoke check."
        )

    if require_corner_db:
        if disable_corner_db:
            raise ValueError("--disable-corner-db cannot be combined with a preset that requires it.")
        if corner_db_path is None:
            raise ValueError("A corner DB path is required for this validation preset.")
        corner_db_file = Path(corner_db_path)
        if not corner_db_file.exists():
            raise FileNotFoundError(
                f"Canonical native exact validation requires {corner_db_file}. "
                "Generate it first with scripts/generate_corner_database.py or "
                "run --preset source-zip for the source-archive smoke check."
            )

    heuristic = (
        ZeroHeuristic()
        if minimal_heuristic
        else NativeCoordinateHeuristic(
            cache_dir=heuristic_cache_dir,
            corner_db_path=None if disable_corner_db else corner_db_path,
            load_corner_db_if_available=not disable_corner_db,
        )
    )
    if require_corner_db:
        heuristic.require_corner_pattern_db(corner_db_path)

    heuristic_stats = heuristic.get_statistics() if hasattr(heuristic, "get_statistics") else {}
    corner_db_loaded = bool(heuristic_stats.get("corner_pattern_db_loaded", False))
    corner_db_complete = bool(heuristic_stats.get("corner_pattern_db_complete", False))
    oracle = KorfOptimalSolver() if use_oracle else None
    failures: List[ValidationFailure] = []
    results = []

    for case in corpus:
        cube = _apply_scramble(case.scramble)
        oracle_length: Optional[int] = None
        oracle_stats: Optional[Dict] = None

        if oracle is not None and case.use_oracle:
            oracle_result = oracle.solve(cube, verbose=False, timeout=timeout)
            if oracle_result is None:
                failures.append(
                    ValidationFailure(
                        category="oracle_incomplete",
                        scramble=case.scramble,
                        message="oracle did not complete",
                        expected_depth=case.expected_depth,
                        expected_depth_source="generated_length",
                        case_category=case.category,
                    )
                )
            else:
                oracle_moves, oracle_stats = oracle_result
                oracle_length = len(oracle_moves)

        native_solver = NativeExactSolver(heuristic=heuristic, max_depth=max_depth, timeout=timeout)
        native_result = native_solver.solve(cube)
        native_stats = native_solver.get_statistics()

        if native_result is None:
            failures.append(
                ValidationFailure(
                    category="native_incomplete",
                    scramble=case.scramble,
                    message=(
                        f"native solver did not complete for oracle depth {oracle_length}"
                        if oracle_length is not None
                        else f"native solver did not complete for generated length {case.expected_depth}"
                    ),
                    expected_depth=oracle_length if oracle_length is not None else case.expected_depth,
                    expected_depth_source="oracle_length" if oracle_length is not None else "generated_length",
                    case_category=case.category,
                    oracle_length=oracle_length,
                    native_stats=native_stats,
                    oracle_stats=oracle_stats,
                )
            )
            continue

        native_moves, _ = native_result
        expected_depth = oracle_length if oracle_length is not None else case.expected_depth
        if len(native_moves) != expected_depth:
            failures.append(
                ValidationFailure(
                    category="oracle_disagreement" if oracle_length is not None else "native_depth_mismatch",
                    scramble=case.scramble,
                    message=f"native depth {len(native_moves)} != expected depth {expected_depth}",
                    expected_depth=expected_depth,
                    expected_depth_source="oracle_length" if oracle_length is not None else "generated_length",
                    case_category=case.category,
                    oracle_length=oracle_length,
                    native_stats=native_stats,
                    oracle_stats=oracle_stats,
                )
            )

        record = {
            "scramble": case.scramble,
            "expected_depth": case.expected_depth,
            "expected_depth_source": "oracle_length" if oracle_length is not None else "generated_length",
            "category": case.category,
            "native_length": len(native_moves),
            "native_stats": native_stats,
        }

        if oracle_length is not None:
            record["oracle_length"] = oracle_length
            record["oracle_stats"] = oracle_stats

        results.append(record)

    failure_categories: Dict[str, int] = {}
    for failure in failures:
        failure_categories[failure.category] = failure_categories.get(failure.category, 0) + 1

    return {
        "config": {
            "corpus_generation": corpus_generation,
            "use_oracle": use_oracle,
            "max_depth": max_depth,
            "timeout": timeout,
            "heuristic_cache_dir": heuristic_cache_dir,
            "corner_db_path": corner_db_path,
            "disable_corner_db": disable_corner_db,
            "corner_db_loaded": corner_db_loaded,
            "corner_db_complete": corner_db_complete,
        },
        "summary": {
            "total_cases": len(corpus),
            "successful_cases": len(results),
            "failure_count": len(failures),
            "failure_categories": failure_categories,
        },
        "total_cases": len(corpus),
        "failures": [asdict(failure) for failure in failures],
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preset",
        choices=("manual", "canonical", "source-zip"),
        default="canonical",
        help=(
            "Named validation preset. The default 'canonical' preset reproduces "
            "the thesis corpus and report schema. 'source-zip' is a smaller "
            "fully contained smoke preset that does not require corner_db.pkl."
        ),
    )
    parser.add_argument("--exhaustive-depth", type=int, default=3)
    parser.add_argument("--oracle-depths", type=int, nargs="*", default=[4, 5])
    parser.add_argument("--oracle-samples-per-depth", type=int, default=3)
    parser.add_argument("--max-depth", type=int, default=7)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--heuristic-cache-dir",
        default="data/pattern_databases/native_exact",
        help="Cache directory for the small admissible coordinate tables",
    )
    parser.add_argument(
        "--corner-db-path",
        default="data/pattern_databases/corner_db.pkl",
        help="Path to the full corner pattern database cache",
    )
    parser.add_argument(
        "--disable-corner-db",
        action="store_true",
        help="Force validation to use only the smaller coordinate heuristic tables",
    )
    parser.add_argument(
        "--minimal-heuristic",
        action="store_true",
        help="Use a zero heuristic for tiny source-ZIP smoke validation without generated move-table caches.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/validation/native_exact",
        help="Directory for JSON validation artifacts",
    )
    args = apply_preset(parser.parse_args())

    exhaustive_corpus = generate_exhaustive_corpus(args.exhaustive_depth)
    random_corpus = generate_random_corpus(
        depths=args.oracle_depths,
        samples_per_depth=args.oracle_samples_per_depth,
        seed=args.seed,
    )
    corpus = exhaustive_corpus + random_corpus
    corpus_generation = build_corpus_generation(
        exhaustive_depth=args.exhaustive_depth,
        oracle_depths=args.oracle_depths,
        oracle_samples_per_depth=args.oracle_samples_per_depth,
        seed=args.seed,
        preset=(
            CANONICAL_PRESET_NAME
            if args.preset == "canonical"
            else SOURCE_ZIP_PRESET_NAME if args.preset == "source-zip" else None
        ),
    )
    corpus_generation.update(
        {
            "exhaustive_cases": len(exhaustive_corpus),
            "oracle_cases": len(random_corpus),
            "total_cases": len(corpus),
        }
    )

    try:
        report = validate_corpus(
            corpus,
            corpus_generation=corpus_generation,
            use_oracle=OPTIMAL_AVAILABLE and bool(random_corpus),
            max_depth=args.max_depth,
            timeout=args.timeout,
            heuristic_cache_dir=args.heuristic_cache_dir,
            corner_db_path=args.corner_db_path,
            disable_corner_db=args.disable_corner_db,
            minimal_heuristic=args.minimal_heuristic,
            require_corner_db=args.preset == "canonical",
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Validation prerequisite failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from None

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"native_exact_validation_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)

    print(f"Wrote validation report to {output_path}")
    print(f"Preset: {args.preset}")
    print(f"Total cases: {report['total_cases']}")
    print(f"Failures: {len(report['failures'])}")


if __name__ == "__main__":
    main()
