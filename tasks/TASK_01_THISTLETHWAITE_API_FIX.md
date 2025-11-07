# TASK 01: Fix Thistlethwaite API Parameter Mismatch

**Priority:** 🔴 HIGH
**Status:** ⏳ Pending
**Estimated Time:** 1-2 hours
**Difficulty:** Medium
**Blocker:** Yes - Prevents complete thesis data generation

---

## 📝 PROBLEM DESCRIPTION

The Thistlethwaite solver cannot generate benchmark data because of an API mismatch between the solver implementation and the benchmark script.

### Current Issue:
- **Benchmark script** calls: `solver.solve(cube, max_time=30)`
- **Solver implementation** signature: `solve(cube)` - doesn't accept `max_time`
- **Result:** `TypeError: solve() got an unexpected keyword argument 'max_time'`

### Impact:
- ❌ Cannot generate Thistlethwaite benchmark data
- ❌ Cannot compare Thistlethwaite vs Kociemba quantitatively
- ❌ Missing 50% of thesis performance analysis data

---

## 🎯 ACCEPTANCE CRITERIA

- [ ] Thistlethwaite solver can be called with `max_time` parameter
- [ ] Benchmark script successfully generates 40 test cases for Thistlethwaite
- [ ] No breaking changes to existing tests
- [ ] All existing Thistlethwaite tests still pass
- [ ] Solver gracefully handles timeout if `max_time` exceeded

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Locate the Files

```bash
# Main solver implementation
src/thistlethwaite/solver.py

# Benchmark script (find which one calls it)
grep -r "max_time" --include="*.py" .
```

**Expected files to modify:**
1. `src/thistlethwaite/solver.py` - Add `max_time` parameter
2. Possibly `generate_thesis_data.py` or similar benchmark script

---

### Step 2: Review Current Solver Signature

```bash
# Check current solve method
grep -A 10 "def solve" src/thistlethwaite/solver.py
```

**Current signature (expected):**
```python
def solve(self, cube: RubikCube) -> List[str]:
    """Solve the cube using Thistlethwaite's algorithm."""
```

---

### Step 3: Add max_time Parameter

**Option A: Make max_time Optional (Recommended)**

Modify `src/thistlethwaite/solver.py`:

```python
def solve(self, cube: RubikCube, max_time: Optional[float] = None) -> List[str]:
    """
    Solve the cube using Thistlethwaite's algorithm.

    Args:
        cube: The Rubik's cube to solve
        max_time: Maximum time in seconds (optional, None = no limit)

    Returns:
        List of moves to solve the cube

    Raises:
        TimeoutError: If max_time exceeded (if timeout checking implemented)
    """
    start_time = time.time() if max_time else None

    # ... existing implementation ...

    # Add timeout checks in search loops if max_time provided
    if max_time and (time.time() - start_time) > max_time:
        raise TimeoutError(f"Solver exceeded max_time of {max_time}s")
```

**Option B: Ignore max_time (Quick Fix)**

If timeout functionality isn't needed:

```python
def solve(self, cube: RubikCube, max_time: Optional[float] = None) -> List[str]:
    """
    Solve the cube using Thistlethwaite's algorithm.

    Args:
        cube: The Rubik's cube to solve
        max_time: Maximum time in seconds (currently ignored)

    Returns:
        List of moves to solve the cube
    """
    # Existing implementation unchanged
    # Just accept the parameter for API compatibility
```

---

### Step 4: Add Timeout Logic (If Using Option A)

Find the IDA* search loops in the solver and add checks:

```python
# In phase solve methods
def _solve_phase_N(self, ...):
    for depth in range(max_depth):
        # Add timeout check
        if self.start_time and (time.time() - self.start_time) > self.max_time:
            raise TimeoutError(f"Phase N exceeded timeout")

        # ... existing search logic ...
```

**Files to check:**
- `src/thistlethwaite/ida_star.py` - IDA* implementation
- `src/thistlethwaite/solver.py` - Phase orchestration

---

### Step 5: Update Benchmark Script

Find the benchmark script:

```bash
find . -name "*benchmark*" -o -name "*thesis_data*" | grep -v __pycache__
```

Ensure it calls the solver correctly:

```python
try:
    solution = solver.solve(cube, max_time=30)
    # Record success
except TimeoutError:
    # Record timeout
    solution = None
```

---

### Step 6: Test the Fix

```bash
# Test 1: Verify existing tests still pass
pytest tests/unit/test_thistlethwaite.py -v

# Test 2: Quick manual test
python -c "
from src.cube.rubik_cube import RubikCube
from src.thistlethwaite.solver import ThistlethwaiteSolver

cube = RubikCube()
cube.scramble(moves=10, seed=42)
solver = ThistlethwaiteSolver()

# Test with max_time
solution = solver.solve(cube, max_time=30)
print(f'Solution length: {len(solution)}')

# Test without max_time (backward compatibility)
cube2 = RubikCube()
cube2.scramble(moves=10, seed=43)
solution2 = solver.solve(cube2)
print(f'Solution length: {len(solution2)}')
"

# Test 3: Run benchmark script
python generate_thesis_data.py  # Or whatever the script is named
```

---

## 🧪 VERIFICATION COMMANDS

```bash
# 1. Check solver signature accepts max_time
python -c "import inspect; from src.thistlethwaite.solver import ThistlethwaiteSolver; print(inspect.signature(ThistlethwaiteSolver.solve))"

# Expected output: (self, cube: src.cube.rubik_cube.RubikCube, max_time: Optional[float] = None)

# 2. Run all Thistlethwaite tests
pytest tests/unit/test_thistlethwaite.py -v

# Expected: All 33 tests pass

# 3. Test backward compatibility
python demos/thistlethwaite_demo.py

# Expected: Runs without errors

# 4. Generate benchmark data
python generate_thesis_data.py

# Expected: Creates files with Thistlethwaite data
```

---

## 📁 FILES TO MODIFY

### Primary (Must Modify):
1. **`src/thistlethwaite/solver.py`**
   - Add `max_time` parameter to `solve()` method
   - Add imports: `from typing import Optional`
   - Optionally add `import time` for timeout logic

### Secondary (May Need to Modify):
2. **`src/thistlethwaite/ida_star.py`**
   - Add timeout checks in search loops (if implementing full timeout)

3. **Benchmark script** (find with grep)
   - Ensure proper error handling for TimeoutError

### Tertiary (Review Only):
4. **`tests/unit/test_thistlethwaite.py`**
   - May want to add test for `max_time` parameter
   - Verify existing tests still pass

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue 1: Import Errors
```python
# If you see: NameError: name 'Optional' is not defined
# Fix: Add to imports
from typing import Optional, List
```

### Issue 2: time Module Not Imported
```python
# If you see: NameError: name 'time' is not defined
# Fix: Add to imports
import time
```

### Issue 3: Tests Fail After Changes
```bash
# Run tests with verbose output to see what broke
pytest tests/unit/test_thistlethwaite.py -v -s

# Check if any tests are passing explicit arguments
grep "solve(" tests/unit/test_thistlethwaite.py
```

### Issue 4: Can't Find Benchmark Script
```bash
# Search for scripts that use Thistlethwaite
grep -r "ThistlethwaiteSolver" --include="*.py" . | grep -v test | grep -v __pycache__

# Common locations:
# - ./generate_thesis_data.py
# - ./scripts/benchmark.py
# - ./scripts/run_comprehensive_tests.py
```

---

## ⏱️ TIME BREAKDOWN

- **Investigation:** 15-30 minutes (review code, find files)
- **Implementation:** 30-45 minutes (add parameter, timeout logic)
- **Testing:** 15-30 minutes (run tests, verify)
- **Benchmark Run:** 10-20 minutes (generate full dataset)

**Total:** 1-2 hours

---

## 📊 SUCCESS METRICS

You'll know you're done when:

1. ✅ `solver.solve(cube)` still works (backward compatible)
2. ✅ `solver.solve(cube, max_time=30)` works (new feature)
3. ✅ All 33 Thistlethwaite tests pass
4. ✅ Benchmark script generates Thistlethwaite data
5. ✅ No regression in existing demos

---

## 🔗 RELATED TASKS

- **TASK_03:** Re-run benchmarks (depends on this task)
- **TASK_02:** Verify tests (should do in parallel)

---

## 📚 REFERENCES

- TESTING_REPORT.md (lines 149-162) - Original issue description
- src/thistlethwaite/solver.py - Implementation file
- src/kociemba/solver.py - Reference for similar API (check if it has max_time)

---

**Next Step:** Start with reviewing current solver signature and choose Option A or B above.
