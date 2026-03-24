# Project Screenshots

This directory contains optional UI screenshots and visual documentation for the Rubik's Cube Solving Algorithms thesis project.

The written thesis does not rely on these screenshots as canonical evidence for
the benchmark results. They are supplementary assets for demos, appendix-style
usage notes, or defense material.

No screenshot assets are committed in the current tree. Capture them locally if
you want presentation backups or appendix illustrations.

## Directory Structure

- `web_ui/` - Screenshots from the Streamlit web interface

## Web UI Screenshots

### Home Page
**File:** `web_ui/01_home_page.png`
**Description:** Main landing page showing project overview and navigation

**Status:** 📸 To be captured by user
**What to capture:**
- Project title: "Rubik's Cube Solving Algorithms"
- Navigation sidebar (Single Solver, Comparison, Educational)
- Welcome text and overview
- Clean layout without errors

---

### Single Solver - Thistlethwaite
**File:** `web_ui/02_single_solver_thistlethwaite.png`
**Description:** Thistlethwaite algorithm solving interface

**Status:** 📸 To be captured by user
**What to capture:**
1. Select "Thistlethwaite" from dropdown
2. Generate or enter a scramble
3. Click "Solve"
4. Capture the solution display showing:
   - Move sequence
   - Move count
   - Execution time
   - Phase breakdown (if available)

---

### Single Solver - Kociemba
**File:** `web_ui/03_single_solver_kociemba.png`
**Description:** Kociemba algorithm solving interface

**Status:** 📸 To be captured by user
**What to capture:**
1. Select "Kociemba" from dropdown
2. Generate or enter a scramble
3. Click "Solve"
4. Capture the solution display

---

### Comparison Page
**File:** `web_ui/04_comparison.png`
**Description:** Side-by-side algorithm comparison

**Status:** 📸 To be captured by user
**What to capture:**
1. Enter or generate a scramble
2. Click "Compare Algorithms"
3. Capture side-by-side results showing:
   - Both algorithm solutions
   - Performance metrics (time, moves)
   - Comparison charts (if available)

---

### Educational Page
**File:** `web_ui/05_educational.png`
**Description:** Educational content and algorithm explanations

**Status:** 📸 To be captured by user
**What to capture:**
- Algorithm theory and background
- Code examples or pseudocode
- Interactive elements (if any)
- Visual explanations

---

### 3D Visualization (Optional)
**File:** `web_ui/06_3d_visualization.png`
**Description:** 3D cube rendering (if implemented)

**Status:** 📸 To be captured by user (if available)
**What to capture:**
- Interactive 3D cube view
- Rotation and manipulation controls

---

### Export Functionality (Optional)
**File:** `web_ui/07_export.png`
**Description:** Data export features (JSON, CSV, etc.)

**Status:** 📸 To be captured by user (if available)
**What to capture:**
- Export buttons or menu
- Downloaded file preview

---

## Supplementary Use

These screenshots can be used in optional supplementary material:

### Chapter 8: Implementation
- UI architecture screenshots
- Code structure visualization

### Appendix A: User Manual
- Step-by-step feature demonstrations
- Usage examples

### Defense Presentation
- Visual slides showing the working application
- Live demo backup materials

---

## How to Capture Web UI Screenshots

### Prerequisites
1. Ensure Streamlit is running:
   ```bash
   streamlit run ui/app.py
   ```
2. Open browser to http://localhost:8501

### Recommended Screenshot Tool
- **macOS:** Cmd+Shift+4 (select area) or Cmd+Shift+3 (full screen)
- **Windows:** Windows+Shift+S (Snipping Tool)
- **Linux:** gnome-screenshot -a (select area)

### Naming Convention
Use the format: `##_description.png`
- Example: `01_home_page.png`, `02_single_solver_thistlethwaite.png`

### Quality Guidelines
- **Resolution:** Minimum 1280x720, preferred 1920x1080
- **Format:** PNG (lossless) for UI screenshots
- **Content:** Include full page context, avoid cropping important elements
- **Browser:** Use Chrome/Firefox with clean interface (no bookmarks bar)

---

## Screenshot Checklist

### Web UI (Optional)
- [ ] `01_home_page.png` - Landing page
- [ ] `02_single_solver_thistlethwaite.png` - Thistlethwaite solving
- [ ] `03_single_solver_kociemba.png` - Kociemba solving
- [ ] `04_comparison.png` - Algorithm comparison
- [ ] `05_educational.png` - Educational content

### Web UI (Optional - if features exist)
- [ ] `06_3d_visualization.png` - 3D cube view
- [ ] `07_export.png` - Export functionality

## Technical Notes

### Streamlit Launch Command
```bash
streamlit run ui/app.py --server.port 8501
```

### UI Pages Location
- Main app: `ui/app.py`
- Pages: `ui/pages/*.py`
  - Single Solver
  - Comparison
  - Educational

### Demo Scripts Location
- Basic demos: `demos/*.py`
- Phase 9 demos: `demos/phase9/*.py`

---

## Contact

For questions about screenshots or documentation:
- Alex Toska
- University of Patras
- Thesis: Rubik's Cube Solving Algorithms

---

**Last Updated:** 2026-03-21
**Status:** Optional supplementary screenshots pending capture
