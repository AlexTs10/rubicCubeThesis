# TASK 04: UI Testing & Screenshot Capture

**Priority:** 🟡 MEDIUM
**Status:** ⏳ Pending
**Estimated Time:** 1-2 hours
**Difficulty:** Easy
**Blocker:** No - But important for thesis presentation

---

## 📝 PROBLEM DESCRIPTION

The web UI and demos need manual testing to ensure they work properly for:
1. Thesis defense demonstrations
2. Screenshots for thesis document
3. Validation that all features work correctly

### Current Status:
- ✅ UI exists (`ui/app.py` and multiple pages)
- ✅ CLI demos exist (`demos/` directory)
- ⚠️ No manual testing done in current environment
- ❌ No screenshots captured for thesis

---

## 🎯 ACCEPTANCE CRITERIA

### Web UI (Streamlit):
- [ ] App launches without errors
- [ ] Home page displays correctly
- [ ] Single Solver page works for both algorithms
- [ ] Comparison page shows side-by-side results
- [ ] Educational mode displays algorithm information
- [ ] 3D visualization renders correctly
- [ ] Export functionality works (JSON, CSV)
- [ ] At least 5 screenshots captured

### CLI Demos:
- [ ] `basic_usage.py` runs successfully
- [ ] `thistlethwaite_demo.py` runs successfully
- [ ] `kociemba_demo.py` runs successfully
- [ ] Phase 9 demos run successfully
- [ ] At least 2 CLI screenshots/recordings captured

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Part A: Web UI Testing

#### Step 1: Install UI Dependencies

```bash
# Check if streamlit installed
pip list | grep streamlit

# If not installed
pip install streamlit plotly rich pillow imageio

# Verify installation
streamlit --version
```

---

#### Step 2: Launch Web UI

```bash
# From project root
cd /home/user/rubicCubeThesis

# Launch Streamlit app
streamlit run ui/app.py

# Alternative: Specify port
streamlit run ui/app.py --server.port 8501
```

Expected output:
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

---

#### Step 3: Test Home Page

**Navigate to:** http://localhost:8501

**Verify:**
- [ ] Page loads without errors
- [ ] Project title displays: "Rubik's Cube Solving Algorithms"
- [ ] Navigation sidebar shows: Single Solver, Comparison, Educational
- [ ] Welcome text and overview visible
- [ ] No Python errors in terminal

**Screenshot:** Capture home page

---

#### Step 4: Test Single Solver Page

**Navigate to:** Single Solver (from sidebar)

**Test Thistlethwaite:**
1. Select "Thistlethwaite" from dropdown
2. Click "Generate Random Scramble" (or enter custom scramble)
3. Click "Solve"
4. Verify:
   - [ ] Solution displays
   - [ ] Move count shown
   - [ ] Execution time shown
   - [ ] 3D visualization appears (if implemented)
   - [ ] No errors

**Test Kociemba:**
1. Select "Kociemba" from dropdown
2. Click "Generate Random Scramble"
3. Click "Solve"
4. Verify same elements as above

**Screenshots:**
- Capture solver interface
- Capture solution display
- Capture 3D visualization (if present)

---

#### Step 5: Test Comparison Page

**Navigate to:** Comparison (from sidebar)

**Test:**
1. Enter or generate scramble
2. Click "Compare Algorithms"
3. Verify:
   - [ ] Both algorithms run
   - [ ] Side-by-side results display
   - [ ] Comparison metrics shown (time, moves)
   - [ ] Winner indicated (if implemented)
   - [ ] Charts/graphs display (if implemented)
   - [ ] No errors

**Screenshots:**
- Capture comparison interface
- Capture side-by-side results

---

#### Step 6: Test Educational Page

**Navigate to:** Educational (from sidebar)

**Verify:**
- [ ] Algorithm explanations display
- [ ] Interactive elements work (if any)
- [ ] Code examples shown
- [ ] Theory/background information present
- [ ] No errors

**Screenshot:** Capture educational content

---

#### Step 7: Test Export Functionality

**In any solver page:**

1. Solve a cube
2. Look for Export buttons (JSON, CSV, etc.)
3. Click each export option
4. Verify:
   - [ ] File downloads or data displays
   - [ ] Format is correct
   - [ ] Contains expected data
   - [ ] No errors

---

### Part B: CLI Demo Testing

#### Step 8: Test Basic Usage Demo

```bash
# From project root
python demos/basic_usage.py

# Or with PYTHONPATH
PYTHONPATH=/home/user/rubicCubeThesis:$PYTHONPATH python demos/basic_usage.py
```

**Verify:**
- [ ] Script runs without import errors
- [ ] Cube scrambles and solves
- [ ] Output is readable
- [ ] No crashes

**Optional:** Record terminal output
```bash
script -c "python demos/basic_usage.py" basic_usage_output.txt
```

---

#### Step 9: Test Thistlethwaite Demo

```bash
python demos/thistlethwaite_demo.py
```

**Verify:**
- [ ] Runs successfully
- [ ] Shows phase-by-phase solving
- [ ] Displays solution
- [ ] Performance metrics shown

---

#### Step 10: Test Kociemba Demo

```bash
python demos/kociemba_demo.py
```

**Verify:**
- [ ] Runs successfully
- [ ] Shows two-phase solving
- [ ] Displays solution
- [ ] Performance metrics shown

---

#### Step 11: Test Phase 9 Demos

```bash
# Interactive solver
python demos/phase9/interactive_solver.py

# Algorithm comparison
python demos/phase9/algorithm_comparison_cli.py

# Animation demo
python demos/phase9/animation_demo.py

# Benchmark demo
python demos/phase9/benchmark_demo.py
```

**Verify each:**
- [ ] Runs without errors
- [ ] Rich formatting displays correctly
- [ ] Interactive features work (if any)
- [ ] Output is informative

---

### Part C: Screenshot Organization

#### Step 12: Organize Screenshots

Create screenshot directory:
```bash
mkdir -p screenshots/web_ui
mkdir -p screenshots/cli_demos
```

**Recommended screenshots:**

**Web UI (5-7 screenshots):**
1. `01_home_page.png` - Landing page
2. `02_single_solver_thistlethwaite.png` - Thistlethwaite solving
3. `03_single_solver_kociemba.png` - Kociemba solving
4. `04_comparison.png` - Side-by-side comparison
5. `05_educational.png` - Educational content
6. `06_3d_visualization.png` - 3D cube (if available)
7. `07_export.png` - Export functionality

**CLI Demos (2-3 screenshots):**
1. `01_basic_demo.png` - Basic usage
2. `02_interactive_solver.png` - Interactive demo
3. `03_comparison_cli.png` - Comparison output

---

#### Step 13: Create Screenshot Documentation

**Create:** `screenshots/README.md`

```markdown
# Project Screenshots

## Web UI Screenshots

### Home Page
![Home Page](web_ui/01_home_page.png)
*Main landing page showing project overview*

### Single Solver - Thistlethwaite
![Thistlethwaite](web_ui/02_single_solver_thistlethwaite.png)
*Thistlethwaite algorithm solving a scrambled cube*

[Continue for all screenshots...]

## CLI Demo Screenshots

### Basic Usage
![Basic Demo](cli_demos/01_basic_demo.png)
*Command-line demonstration of basic solving*

[...]

## Usage in Thesis

These screenshots can be used in:
- Chapter 4: Implementation
- Chapter 5: User Interface
- Chapter 6: Results & Evaluation
- Appendix: User Manual
```

---

## 🧪 VERIFICATION COMMANDS

```bash
# 1. Check UI dependencies
pip list | grep -E "streamlit|plotly|rich"

# 2. Verify UI files exist
ls -lh ui/app.py
ls -lh ui/pages/*.py

# 3. Check demo files
ls -lh demos/*.py
ls -lh demos/phase9/*.py

# 4. Test imports without running
python -c "from ui import app; print('✓ UI imports work')"
python -c "import demos.basic_usage; print('✓ Demo imports work')"

# 5. Verify screenshots captured
ls -lh screenshots/web_ui/
ls -lh screenshots/cli_demos/
```

---

## 📁 FILES TO CREATE

### Screenshots:
1. `screenshots/web_ui/01_home_page.png`
2. `screenshots/web_ui/02_single_solver_thistlethwaite.png`
3. `screenshots/web_ui/03_single_solver_kociemba.png`
4. `screenshots/web_ui/04_comparison.png`
5. `screenshots/web_ui/05_educational.png`
6. `screenshots/cli_demos/01_basic_demo.png`
7. `screenshots/cli_demos/02_interactive_solver.png`

### Documentation:
8. `screenshots/README.md` - Screenshot index and descriptions

### Test Logs (Optional):
9. `ui_testing_log.md` - Notes from manual testing
10. `demo_test_results.txt` - CLI demo outputs

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue 1: Streamlit Not Found

```bash
# Solution: Install streamlit
pip install streamlit plotly rich pillow imageio

# Verify
streamlit --version
```

---

### Issue 2: Port Already in Use

```bash
# Error: Address already in use
# Solution: Use different port
streamlit run ui/app.py --server.port 8502

# Or kill existing process
pkill -f streamlit
```

---

### Issue 3: Import Errors in UI

```bash
# Error: ModuleNotFoundError: No module named 'src'
# Solution: Run from project root
cd /home/user/rubicCubeThesis
streamlit run ui/app.py

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/user/rubicCubeThesis"
```

---

### Issue 4: Demo PYTHONPATH Issues

```bash
# Error: ModuleNotFoundError in demos
# Solution: Set PYTHONPATH
export PYTHONPATH=/home/user/rubicCubeThesis:$PYTHONPATH

# Or run from project root
cd /home/user/rubicCubeThesis
python demos/basic_usage.py
```

---

### Issue 5: No Display for Screenshots

```bash
# If on headless server, install virtual display
sudo apt-get install xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# Or use SSH with X forwarding
ssh -X user@server
```

---

### Issue 6: Rich Formatting Not Displaying

```bash
# Issue: CLI demos show ugly output
# Solution: Ensure terminal supports colors
export TERM=xterm-256color

# Or disable rich formatting temporarily
# (Check demo code for --no-rich flag)
```

---

## ⏱️ TIME BREAKDOWN

- **Setup & installation:** 10 minutes
- **Web UI testing:** 30-45 minutes (thorough testing of all pages)
- **Screenshot capture:** 15-20 minutes (Web UI)
- **CLI demo testing:** 15-20 minutes
- **CLI screenshot capture:** 10 minutes
- **Documentation:** 10-15 minutes

**Total:** 1.5-2 hours

---

## 📊 SUCCESS METRICS

You'll know you're done when:

1. ✅ Web UI launches without errors
2. ✅ All 3 pages tested (Single Solver, Comparison, Educational)
3. ✅ Both algorithms work in UI
4. ✅ 5-7 web UI screenshots captured
5. ✅ At least 3 CLI demos tested successfully
6. ✅ 2-3 CLI screenshots/logs captured
7. ✅ screenshots/README.md created
8. ✅ No critical bugs found (or logged for fixing)

---

## 🎓 THESIS USAGE

These screenshots will be used in:

- **Chapter 4 (Implementation):** Show architecture through UI
- **Chapter 5 (User Interface):** Document usability
- **Chapter 6 (Results):** Show algorithm comparisons visually
- **Appendix A (User Manual):** Demonstrate features
- **Defense Presentation:** Visual slides

---

## 🔗 RELATED TASKS

- **TASK_03:** Use benchmark data in UI demos
- **TASK_05:** Jupyter notebooks complement UI

---

## 📚 REFERENCES

- `ui/app.py` - Main UI entry point
- `ui/pages/` - Individual page implementations
- `demos/phase9/DEMO_GUIDE.md` - Demo usage instructions
- TESTING_REPORT.md (lines 33-62) - Previous UI validation notes

---

## 🎯 QUICK START

**Fastest path to completion:**

```bash
# 1. Install dependencies
pip install streamlit plotly rich

# 2. Launch UI
streamlit run ui/app.py

# 3. Test each page and capture screenshots

# 4. Test CLI demos
python demos/basic_usage.py
python demos/kociemba_demo.py
python demos/thistlethwaite_demo.py

# 5. Organize screenshots
mkdir -p screenshots/{web_ui,cli_demos}
# Move/rename screenshots

# 6. Done!
```

---

**Next Step:** Install dependencies and launch the Streamlit UI!
