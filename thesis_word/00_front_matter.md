# FRONT MATTER

---

## TITLE PAGE

**ΠΑΝΕΠΙΣΤΗΜΙΟ ΠΑΤΡΩΝ**
ΠΟΛΥΤΕΧΝΙΚΗ ΣΧΟΛΗ
ΤΜΗΜΑ ΗΛΕΚΤΡΟΛΟΓΩΝ ΜΗΧΑΝΙΚΩΝ ΚΑΙ ΤΕΧΝΟΛΟΓΙΑΣ ΥΠΟΛΟΓΙΣΤΩΝ

ΕΡΓΑΣΤΗΡΙΟ ΕΝΣΥΡΜΑΤΗΣ ΤΗΛΕΠΙΚΟΙΝΩΝΙΑΣ
ΟΜΑΔΑ ΤΕΧΝΗΤΗΣ ΝΟΗΜΟΣΥΝΗΣ

---

**ΔΙΠΛΩΜΑΤΙΚΗ ΕΡΓΑΣΙΑ**

---

# Αλγόριθμοι Βέλτιστης Επίλυσης για τον Κύβο του Rubik

*(Optimal Solution Algorithms for Rubik's Cube)*

---

**Αλέξανδρος Τόσκας**

**Επιβλέπων:**
Κυριάκος Σγάρμπας
Αναπληρωτής Καθηγητής

ΠΑΤΡΑ, 2026

---
---

## ΣΕΛΙΔΑ ΕΓΚΡΙΣΗΣ

Η παρούσα διπλωματική εργασία με τίτλο:

**«Αλγόριθμοι Βέλτιστης Επίλυσης για τον Κύβο του Rubik»**

του φοιτητή **Αλέξανδρου Τόσκα** εγκρίθηκε ομόφωνα από την τριμελή εξεταστική επιτροπή:

| Όνομα | Υπογραφή |
|-------|----------|
| Κυριάκος Σγάρμπας, Αναπληρωτής Καθηγητής | _____________ |
| [Όνομα], [Βαθμίδα] | _____________ |
| [Όνομα], [Βαθμίδα] | _____________ |

Πάτρα, _____________ 2026

---
---

## ΕΥΧΑΡΙΣΤΙΕΣ

Θα ήθελα να ευχαριστήσω τον επιβλέποντα καθηγητή μου, κ. Κυριάκο Σγάρμπα, για την καθοδήγηση και τις πολύτιμες συμβουλές του κατά τη διάρκεια εκπόνησης αυτής της διπλωματικής εργασίας.

[Προσθέστε επιπλέον ευχαριστίες]

Αλέξανδρος Τόσκας
Πάτρα, 2026

---
---

## ΠΕΡΙΛΗΨΗ

Ο κύβος του Rubik αποτελεί ένα από τα πιο διάσημα συνδυαστικά παζλ, με χώρο καταστάσεων που ξεπερνά τις 4.3 × 10¹⁹ διαφορετικές διατάξεις. Η εύρεση βέλτιστων λύσεων—δηλαδή ακολουθιών κινήσεων ελάχιστου μήκους—αποτελεί σημαντικό πρόβλημα στον τομέα της τεχνητής νοημοσύνης και των αλγορίθμων αναζήτησης.

Η παρούσα διπλωματική εργασία πραγματεύεται την υλοποίηση και συγκριτική αξιολόγηση τριών αλγορίθμων επίλυσης του κύβου του Rubik:

- Ο **αλγόριθμος Thistlethwaite** (1981), που χρησιμοποιεί τέσσερις διαδοχικές φάσεις για τη σταδιακή μείωση του χώρου αναζήτησης.
- Ο **αλγόριθμος Kociemba** (1992), που βελτιστοποιεί την προσέγγιση σε δύο φάσεις, επιτυγχάνοντας λύσεις κάτω των 19 κινήσεων.
- Ο **αλγόριθμος Korf** (1997), που εγγυάται βέλτιστες λύσεις χρησιμοποιώντας τον IDA* με pattern databases.

Επιπλέον, υλοποιήθηκε αλγόριθμος εκτίμησης της απόστασης μιας κατάστασης από τη λύση, καθώς και διάφορες ευρετικές συναρτήσεις για τον αλγόριθμο A*. Προτείνεται μια **πρωτότυπη σύνθετη ευρετική** (composite heuristic) που επιλέγει δυναμικά τη βέλτιστη στρατηγική αναζήτησης με βάση χαρακτηριστικά της τρέχουσας κατάστασης, επιτυγχάνοντας μείωση 15-25% στον αριθμό κόμβων που εξετάζονται.

Η πειραματική αξιολόγηση επιβεβαιώνει ότι:
- Ο αλγόριθμος Kociemba επιτυγχάνει λύσεις μέσου μήκους κάτω των 19 κινήσεων σε λιγότερο από 5 δευτερόλεπτα.
- Ο αλγόριθμος Korf εγγυάται βέλτιστες λύσεις (μέγιστο 20 κινήσεις), επιβεβαιώνοντας το «God's Number».
- Ο IDA* υπερτερεί του A* για την επίλυση του κύβου λόγω των χαμηλότερων απαιτήσεων μνήμης.

Η υλοποίηση περιλαμβάνει πλήρη σουίτα δοκιμών (203 tests), διαδραστικές web εφαρμογές για επίδειξη, και εκπαιδευτικό υλικό σε μορφή Jupyter notebooks.

**Λέξεις-κλειδιά:** Κύβος Rubik, αλγόριθμοι αναζήτησης, IDA*, A*, pattern databases, ευρετικές συναρτήσεις, θεωρία ομάδων, βέλτιστη επίλυση

---
---

## ABSTRACT

The Rubik's Cube is one of the most famous combinatorial puzzles, with a state space exceeding 4.3 × 10¹⁹ distinct configurations. Finding optimal solutions—i.e., move sequences of minimum length—is a significant problem in artificial intelligence and search algorithms.

This diploma thesis addresses the implementation and comparative evaluation of three Rubik's Cube solving algorithms:

- **Thistlethwaite's algorithm** (1981), which uses four successive phases to gradually reduce the search space.
- **Kociemba's algorithm** (1992), which optimizes the approach to two phases, achieving solutions under 19 moves.
- **Korf's algorithm** (1997), which guarantees optimal solutions using IDA* with pattern databases.

Additionally, a distance estimation algorithm was implemented, along with various heuristic functions for the A* algorithm. A **novel composite heuristic** is proposed that dynamically selects the optimal search strategy based on the current state's characteristics, achieving a 15-25% reduction in explored nodes.

Experimental evaluation confirms that:
- Kociemba's algorithm achieves solutions averaging under 19 moves in less than 5 seconds.
- Korf's algorithm guarantees optimal solutions (maximum 20 moves), confirming "God's Number".
- IDA* outperforms A* for cube solving due to lower memory requirements.

The implementation includes a comprehensive test suite (203 tests), interactive web applications for demonstration, and educational materials in the form of Jupyter notebooks.

**Keywords:** Rubik's Cube, search algorithms, IDA*, A*, pattern databases, heuristic functions, group theory, optimal solving
