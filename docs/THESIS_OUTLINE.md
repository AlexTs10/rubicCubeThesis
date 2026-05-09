# Thesis Outline: Αλγόριθμοι Επίλυσης και Βέλτιστης Αναζήτησης για τον Κύβο του Rubik

> Historical planning outline. Some fallback, admissibility, and benchmark-number notes below predate the March 2026 verification pass and should not be cited as final thesis truth.

**Επίπεδο**: Διπλωματική Εργασία (Undergraduate Thesis)
**Πανεπιστήμιο Πατρών** - Τμήμα Ηλεκτρολόγων Μηχανικών και Τεχνολογίας Υπολογιστών
**Επιβλέπων**: Κυριάκος Σγάρμπας

---

## Προτεινόμενη Δομή (60-80 σελίδες)

Για διπλωματική εργασία προπτυχιακού επιπέδου, στόχευσε 60-80 σελίδες ουσιαστικού περιεχομένου. Παρακάτω είναι η δομή με εκτιμώμενο μήκος και οδηγίες για κάθε ενότητα.

---

## ΚΕΦΑΛΑΙΟ 1: ΕΙΣΑΓΩΓΗ (5-7 σελίδες)

### 1.1 Ο Κύβος του Rubik (1-2 σελ.)
**Τι να γράψεις:**
- Σύντομο ιστορικό (Ernő Rubik, 1974)
- Γιατί είναι ενδιαφέρον πρόβλημα για την επιστήμη υπολογιστών
- Μέγεθος χώρου καταστάσεων: 43.252.003.274.489.856.000 διατάξεις

**Πηγές από το repo:**
- `papers/chapter2/` - Ιστορικά papers

### 1.2 Ορισμός του Προβλήματος (1-2 σελ.)
**Τι να γράψεις:**
- Τι σημαίνει "βέλτιστη λύση"
- God's Number = 20 (αποδείχθηκε το 2010)
- Half-Turn Metric (HTM) vs Quarter-Turn Metric (QTM)
- Γιατί η brute-force αναζήτηση είναι αδύνατη

**Αναφορές:**
- cube20.org για το God's Number
- `papers/chapter2/` papers

### 1.3 Στόχοι της Εργασίας (1 σελ.)
**Τι να γράψεις:**
Απλή λίστα των στόχων (αντιγράφοντας από την εκφώνηση):
1. Υλοποίηση αλγορίθμων Thistlethwaite, Kociemba, Korf
2. Αλγόριθμος εκτίμησης απόστασης
3. Εύρεση κατάλληλης ευρετικής για A*

### 1.4 Δομή της Εργασίας (0.5 σελ.)
**Τι να γράψεις:**
Μία παράγραφος που περιγράφει τι περιέχει κάθε κεφάλαιο.

---

## ΚΕΦΑΛΑΙΟ 2: ΘΕΩΡΗΤΙΚΟ ΥΠΟΒΑΘΡΟ (8-10 σελίδες)

### 2.1 Αναπαράσταση του Κύβου (2-3 σελ.)
**Τι να γράψεις:**
- Facelet representation (54 αυτοκόλλητα)
- Cubie representation (20 κομμάτια: 8 γωνίες, 12 ακμές)
- Singmaster notation (U, D, L, R, F, B και παραλλαγές)
- Παράδειγμα με σχήματα

**Κώδικας αναφοράς:**
```
src/cube/rubik_cube.py    - Facelet representation
src/cube/moves.py         - Singmaster notation
src/kociemba/cubie.py     - Cubie representation
```

**Σχήματα να συμπεριλάβεις:**
- Διάγραμμα του κύβου με αρίθμηση facelets
- Πίνακας με τις κινήσεις και τα σύμβολά τους

### 2.2 Στοιχεία Θεωρίας Ομάδων (2-3 σελ.)
**Τι να γράψεις:**
- Τι είναι ομάδα (group) - απλός ορισμός
- Ο κύβος ως ομάδα μεταθέσεων
- Υποομάδες και cosets (γιατί χρειάζονται για Thistlethwaite/Kociemba)
- Γεννήτορες της ομάδας του κύβου

**Πηγές:**
- `docs/notes/01_group_theory_fundamentals.md`
- `papers/chapter3/` - Group theory papers

**Σημείωση:** Μην υπερβάλεις με τα μαθηματικά. Εξήγησε μόνο όσα χρειάζονται για να κατανοηθούν οι αλγόριθμοι.

### 2.3 Αλγόριθμοι Αναζήτησης (3-4 σελ.)
**Τι να γράψεις:**

**2.3.1 BFS και DFS (0.5 σελ.)**
- Σύντομη επανάληψη, ο αναγνώστης τα ξέρει από ΤΝ

**2.3.2 Αλγόριθμος A* (1 σελ.)**
- f(n) = g(n) + h(n)
- Προϋποθέσεις για βέλτιστη λύση (admissible, consistent heuristic)
- Πρόβλημα: μεγάλη κατανάλωση μνήμης

**2.3.3 Αλγόριθμος IDA* (1 σελ.)**
- Iterative deepening με heuristic
- Γιατί είναι καλύτερος για τον κύβο (χαμηλή μνήμη)
- Pseudocode

**2.3.4 Pattern Databases (1-1.5 σελ.)**
- Τι είναι και πώς λειτουργούν
- Γιατί είναι admissible heuristics
- Additive vs max heuristics

**Κώδικας αναφοράς:**
```
src/korf/a_star.py              - A* και IDA* υλοποίηση
src/korf/pattern_database.py    - Pattern database implementation
```

---

## ΚΕΦΑΛΑΙΟ 3: ΑΛΓΟΡΙΘΜΟΣ THISTLETHWAITE (8-10 σελίδες)

### 3.1 Περιγραφή του Αλγορίθμου (2-3 σελ.)
**Τι να γράψεις:**
- Ιστορικό (Morwen Thistlethwaite, 1981)
- Η ιδέα: 4 φάσεις, κάθε φάση περιορίζει τις επιτρεπόμενες κινήσεις
- Οι 4 ομάδες: G₀ → G₁ → G₂ → G₃ → G₄ (solved)

**Πίνακας για κάθε φάση:**
| Φάση | Στόχος | Καταστάσεις | Επιτρεπόμενες Κινήσεις |
|------|--------|-------------|------------------------|
| 1    | Orient edges | 2,048 | Όλες |
| 2    | Orient corners, E-slice | 1,082,565 | F,B,L,R,U,D |
| 3    | Tetrad positions | 352,800 | F²,B²,L²,R²,U,D |
| 4    | Solve | 663,552 | F²,B²,L²,R²,U²,D² |

### 3.2 Υλοποίηση (3-4 σελ.)
**Τι να γράψεις:**
- Σύστημα συντεταγμένων για κάθε φάση
- Πώς υπολογίζονται οι συντεταγμένες (edge orientation, corner orientation, etc.)
- Pattern databases: πώς δημιουργούνται και πώς χρησιμοποιούνται
- IDA* search σε κάθε φάση

**Κώδικας αναφοράς:**
```
src/thistlethwaite/solver.py      - Κύριος solver
src/thistlethwaite/coordinates.py - Σύστημα συντεταγμένων
src/thistlethwaite/tables.py      - Pattern databases
src/thistlethwaite/ida_star.py    - IDA* search
```

**Code snippets να συμπεριλάβεις:**
- Συνάρτηση υπολογισμού edge orientation
- Η κύρια solve() function (simplified)

### 3.3 Αποτελέσματα (2-3 σελ.)
**Τι να γράψεις:**
- Μέγεθος pattern databases (~2MB)
- Μέσο μήκος λύσης
- Χρόνος επίλυσης
- Σύγκριση με θεωρητικό μέγιστο (45-52 κινήσεις)

**Δεδομένα από:**
```
results/benchmarks/thesis/thesis_data_*.csv - Benchmark results
tests/unit/test_thistlethwaite.py - Test results
```

**Σημείωση:** Η υλοποίησή σου χρησιμοποιεί fallback στον Kociemba για κάποιες περιπτώσεις - εξήγησε γιατί (πρακτική επιλογή για robustness).

---

## ΚΕΦΑΛΑΙΟ 4: ΑΛΓΟΡΙΘΜΟΣ KOCIEMBA (8-10 σελίδες)

### 4.1 Περιγραφή του Αλγορίθμου (2-3 σελ.)
**Τι να γράψεις:**
- Εξέλιξη από Thistlethwaite (Herbert Kociemba, 1992)
- Η ιδέα: 2 φάσεις αντί για 4
- Phase 1: G₀ → G₁ = ⟨U,D,R²,L²,F²,B²⟩
- Phase 2: G₁ → Solved
- Γιατί είναι πιο αποδοτικός (μικρότερος συνολικός χώρος αναζήτησης)

### 4.2 Σύστημα Συντεταγμένων (2-3 σελ.)
**Τι να γράψεις:**
- Phase 1 coordinates: corner orientation, edge orientation, UD-slice
- Phase 2 coordinates: corner permutation, edge permutation, UD-slice permutation
- Πώς γίνεται η μετατροπή facelet → cubie

**Κώδικας αναφοράς:**
```
src/kociemba/coord.py    - Coordinate calculations
src/kociemba/cubie.py    - Cubie representation
```

**Πίνακας:**
| Συντεταγμένη | Εύρος | Περιγραφή |
|--------------|-------|-----------|
| Corner Orientation | 0-2186 | 3⁷ = 2187 |
| Edge Orientation | 0-2047 | 2¹¹ = 2048 |
| UD-Slice | 0-494 | C(12,4) = 495 |
| ... | ... | ... |

### 4.3 Move Tables και Pruning Tables (1-2 σελ.)
**Τι να γράψεις:**
- Move tables: προ-υπολογισμένες μεταβάσεις συντεταγμένων
- Pruning tables: heuristic distances
- Μέγεθος στη μνήμη (~80MB)

**Κώδικας αναφοράς:**
```
src/kociemba/moves.py    - Move tables
src/kociemba/pruning.py  - Pruning tables
```

### 4.4 Υλοποίηση και Αποτελέσματα (2-3 σελ.)
**Τι να γράψεις:**
- Two-phase IDA* search
- Threshold management μεταξύ φάσεων
- Αποτελέσματα: <19 κινήσεις μέσο όρο, <5 δευτερόλεπτα

**Κώδικας αναφοράς:**
```
src/kociemba/solver.py - Main solver
```

**Σχήματα:**
- Flowchart του two-phase algorithm
- Γράφημα χρόνου vs βάθος scramble

---

## ΚΕΦΑΛΑΙΟ 5: ΑΛΓΟΡΙΘΜΟΣ KORF - ΒΕΛΤΙΣΤΗ ΕΠΙΛΥΣΗ (10-12 σελίδες)

### 5.1 Εισαγωγή στη Βέλτιστη Επίλυση (1-2 σελ.)
**Τι να γράψεις:**
- Τι σημαίνει "βέλτιστη" λύση
- Γιατί είναι δύσκολο (exponential search space)
- Richard Korf's contribution (1997)

### 5.2 Pattern Databases για Βέλτιστη Επίλυση (3-4 σελ.)
**Τι να γράψεις:**

**5.2.1 Corner Pattern Database**
- 8! × 3⁷ = 88,179,840 καταστάσεις
- ~42MB αποθήκευση
- Χρόνος δημιουργίας

**5.2.2 Edge Pattern Databases**
- Γιατί χωρίζουμε τις ακμές (12! × 2¹² πολύ μεγάλο)
- δύο default 6-edge databases στο τρέχον artifact
- γιατί τα lightweight/native edge components δεν πρέπει να παρουσιαστούν ως πλήρες classical edge-PDB stack αν δεν υπάρχει πλήρης cache

**Κώδικας αναφοράς:**
```
src/korf/pattern_database.py  - Base class
src/korf/corner_database.py   - Corner DB
src/korf/edge_database.py     - Edge DB
```

### 5.3 IDA* με Pattern Database Heuristics (2-3 σελ.)
**Τι να γράψεις:**
- Πώς συνδυάζονται οι heuristics (max ή sum)
- Admissibility proof
- Pseudocode της υλοποίησης

**Κώδικας αναφοράς:**
```
src/korf/a_star.py           - IDA* implementation
src/korf/heuristics.py       - Heuristic functions
src/korf/optimal_solver.py   - External exact backend wrapper for final benchmark numbers
src/korf/native_exact_solver.py - Repository-native exact API and distance recognizer
```

### 5.4 Αποτελέσματα (2-3 σελ.)
**Τι να γράψεις:**
- Korf exact backend solved 97/100 final benchmark scrambles; 3 requested scramble length 20 cases timed out
- Μέσο μήκος λύσης 9.12 κινήσεις on completed Korf benchmark runs
- Χρόνος επίλυσης 2.66s average on completed Korf benchmark runs, with timeout sensitivity on hard cases
- Trade-off: χρόνος vs optimality

**Δεδομένα από:**
```
results/benchmarks/thesis/thesis_results_combined.json
tests/unit/test_native_exact_solver.py
tests/unit/test_a_star_solvers.py
```

---

## ΚΕΦΑΛΑΙΟ 6: ΕΚΤΙΜΗΣΗ ΑΠΟΣΤΑΣΗΣ ΚΑΙ ΕΥΡΕΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ (8-10 σελίδες)

### 6.1 Το Πρόβλημα της Εκτίμησης Απόστασης (1-2 σελ.)
**Τι να γράψεις:**
- Ορισμός: πόσες κινήσεις χρειάζονται για να λυθεί
- Γιατί είναι χρήσιμο (heuristic για search, UI feedback)
- Δυσκολία: δεν μπορούμε να ξέρουμε χωρίς να λύσουμε

### 6.2 Υλοποιημένες Ευρετικές (3-4 σελ.)
**Τι να γράψεις:**

**6.2.1 Απλές Ευρετικές**
- Hamming distance (πόσα cubies σε λάθος θέση)
- Manhattan distance (άθροισμα αποστάσεων)

**6.2.2 Pattern Database Heuristics**
- Corner heuristic
- Edge heuristic
- Maximum of both

**6.2.3 Composite Heuristic (Πρωτότυπη Συνεισφορά)**
- Adaptive επιλογή heuristic βάσει κατάστασης
- Entropy-based analysis
- Διατήρηση admissibility

**Κώδικας αναφοράς:**
```
src/korf/heuristics.py           - Basic heuristics
src/korf/composite_heuristic.py  - Composite heuristic
src/korf/distance_estimator.py   - Distance estimator
```

### 6.3 Σύγκριση A* vs IDA* (2-3 σελ.)
**Τι να γράψεις:**
- Πειραματική σύγκριση
- A*: καλύτερο σε μικρά βάθη, memory-intensive
- IDA*: καλύτερο για deep search, επαναλαμβάνει nodes
- Συμπέρασμα: IDA* προτιμάται για τον κύβο

**Δεδομένα από:**
```
tests/unit/test_a_star_solvers.py - Comparison tests
docs/DISTANCE_ESTIMATOR_README.md
```

### 6.4 Αποτελέσματα Εκτίμησης (1-2 σελ.)
**Τι να γράψεις:**
- Ακρίβεια εκτίμησης σε σχέση με πραγματική απόσταση
- Πότε η εκτίμηση είναι ακριβής/ανακριβής
- Πίνακας/γράφημα σύγκρισης heuristics

---

## ΚΕΦΑΛΑΙΟ 7: ΠΕΙΡΑΜΑΤΙΚΗ ΑΞΙΟΛΟΓΗΣΗ (6-8 σελίδες)

### 7.1 Μεθοδολογία (1-2 σελ.)
**Τι να γράψεις:**
- Test set: random scrambles σε διάφορα βάθη (5, 10, 15, 20 κινήσεις)
- Μετρικές: μήκος λύσης, χρόνος, μνήμη, nodes expanded
- Περιβάλλον εκτέλεσης (Python version, hardware specs)

### 7.2 Σύγκριση Αλγορίθμων (3-4 σελ.)
**Τι να γράψεις:**

**Πίνακας σύγκρισης:**
| Αλγόριθμος | Μέσο Μήκος | Μέσος Χρόνος | Μνήμη | Βέλτιστος; |
|------------|------------|--------------|-------|------------|
| Thistlethwaite | 23.62 | 1.24s | see final JSON | Όχι |
| Kociemba | 14.33 | 4.62s | see final JSON | Όχι, near-optimal/practical |
| Korf/IDA* | 9.12 on completed runs | 2.66s on completed runs | see final JSON | Ναι, only when the external exact backend completes before timeout |

Use `results/benchmarks/thesis/thesis_results_combined.json` for final benchmark values. The Korf row is based on the recorded external `optimal_external` backend and solved 97/100 benchmark scrambles; do not present timeout cases as solved or treat the exploratory composite heuristic as generally admissible.

**Γραφήματα από:**
```
figures/fig1_solution_length_boxplot.png
figures/fig2_time_comparison.png
figures/fig3_memory_comparison.png
figures/fig4_success_rate.png
figures/fig5_solution_distribution.png
figures/fig6_nodes_comparison.png
figures/fig7_performance_vs_depth.png
```

### 7.3 Συζήτηση (1-2 σελ.)
**Τι να γράψεις:**
- Πότε να χρησιμοποιήσεις κάθε αλγόριθμο
- Trade-offs: ταχύτητα vs optimality vs μνήμη
- Πρακτικές εφαρμογές

---

## ΚΕΦΑΛΑΙΟ 8: ΥΛΟΠΟΙΗΣΗ ΚΑΙ ΕΠΙΔΕΙΞΗ (4-6 σελίδες)

### 8.1 Αρχιτεκτονική Κώδικα (2-3 σελ.)
**Τι να γράψεις:**
- Δομή του project
- Class diagram (απλοποιημένο)
- Πώς συνδέονται τα modules

**Διάγραμμα:**
```
src/
├── cube/           # Core cube representation
├── thistlethwaite/ # Phase 3 algorithm
├── kociemba/       # Phase 4 algorithm
├── korf/           # Phase 5-7 algorithms
└── evaluation/     # Testing and analysis
```

### 8.2 Web Εφαρμογές (1-2 σελ.)
**Τι να γράψεις:**
- Next.js interactive webapp
- Streamlit educational UI
- Screenshots

**Αναφορά:**
```
webapp/  - Next.js application
ui/      - Streamlit application
```

### 8.3 Testing (1 σελ.)
**Τι να γράψεις:**
- `python -m pytest tests --collect-only -q` currently reports `285 tests collected`
- `python -m pytest tests -q` is the supported full-suite command for the current docs snapshot
- Test coverage per module
- Integration tests

---

## ΚΕΦΑΛΑΙΟ 9: ΣΥΜΠΕΡΑΣΜΑΤΑ (3-4 σελίδες)

### 9.1 Σύνοψη Αποτελεσμάτων (1-2 σελ.)
**Τι να γράψεις:**
- Όλοι οι στόχοι επιτεύχθηκαν
- Τι υλοποιήθηκε (bullets)
- Κύρια ευρήματα

### 9.2 Συνεισφορές (0.5-1 σελ.)
**Τι να γράψεις:**
- Πλήρης υλοποίηση 3 αλγορίθμων σε Python
- Composite heuristic (πρωτότυπη συνεισφορά)
- Educational materials (notebooks, web apps)

### 9.3 Μελλοντική Εργασία (1 σελ.)
**Τι να γράψεις:**
- Μεγαλύτεροι κύβοι (4×4×4, 5×5×5)
- GPU acceleration
- Machine learning approaches
- Symmetry exploitation

---

## ΒΙΒΛΙΟΓΡΑΦΙΑ

**Πηγές από:**
```
papers/BIBLIOGRAPHY_INDEX.md
papers/chapter1-7/  - 51 papers
```

Αναμενόμενες αναφορές: 25-40

---

## ΠΑΡΑΡΤΗΜΑ Α: ΟΔΗΓΟΣ ΕΓΚΑΤΑΣΤΑΣΗΣ ΚΑΙ ΧΡΗΣΗΣ (2-3 σελίδες)

**Τι να συμπεριλάβεις:**
- Requirements
- Installation steps
- Παραδείγματα χρήσης CLI
- Πώς να τρέξεις τα demos

---

## ΠΑΡΑΡΤΗΜΑ Β: ΕΠΙΛΕΓΜΕΝΟΣ ΚΩΔΙΚΑΣ (5-10 σελίδες)

**Τι να συμπεριλάβεις:**
- Κύριες functions με σχόλια
- Pseudocode για τους αλγορίθμους
- Μην βάλεις όλο τον κώδικα - μόνο τα highlights

---

## Πρακτικές Συμβουλές Συγγραφής

### Γλώσσα
- Γράψε στα Ελληνικά
- Τεχνικοί όροι: χρησιμοποίησε τον αγγλικό όρο με ελληνική εξήγηση την πρώτη φορά
  - π.χ. "pattern database (βάση δεδομένων προτύπων)"
- Μετά τη πρώτη αναφορά, μπορείς να χρησιμοποιείς τον αγγλικό όρο

### Σχήματα
- Κάθε κεφάλαιο πρέπει να έχει 2-4 σχήματα
- Χρησιμοποίησε τα έτοιμα από `figures/`
- Πρόσθεσε διαγράμματα για τους αλγορίθμους

### Κώδικας
- Μην βάζεις μεγάλα blocks κώδικα στο κύριο κείμενο
- Χρησιμοποίησε pseudocode ή μικρά snippets
- Ο πλήρης κώδικας πάει στο παράρτημα ή αναφέρεται στο repository

### Μαθηματικά
- Χρησιμοποίησε μαθηματική σημειογραφία όπου βοηθάει
- Μην υπερβάλλεις - αυτή είναι διπλωματική μηχανικού, όχι μαθηματικού

### Αναφορές
- Κάθε claim πρέπει να έχει αναφορά
- Ο κώδικάς σου είναι αναφορά (π.χ. "όπως φαίνεται στο src/korf/a_star.py")

---

## Χρονοδιάγραμμα Συγγραφής (Πρόταση)

| Εβδομάδα | Κεφάλαια | Σελίδες |
|----------|----------|---------|
| 1 | Κεφ. 1-2 | ~15 |
| 2 | Κεφ. 3-4 | ~20 |
| 3 | Κεφ. 5-6 | ~20 |
| 4 | Κεφ. 7-9, Παραρτήματα | ~20 |
| 5 | Revision, Βιβλιογραφία | - |

---

## Checklist Πριν την Υποβολή

- [ ] Όλα τα κεφάλαια γραμμένα
- [ ] Σχήματα με λεζάντες και αρίθμηση
- [ ] Πίνακες με τίτλους
- [ ] Βιβλιογραφία σε σωστή μορφή
- [ ] Περίληψη (Ελληνικά + Αγγλικά)
- [ ] Ευχαριστίες
- [ ] Πίνακας περιεχομένων
- [ ] Spell check
- [ ] PDF formatting σύμφωνα με τις οδηγίες του τμήματος
