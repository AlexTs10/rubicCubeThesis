# Thesis LaTeX Project

## Structure

```
thesis/
├── main.tex              # Main document (compile this)
├── references.bib        # Bibliography (IEEE format)
├── Makefile              # Build commands
├── chapters/
│   ├── 00_titlepage.tex
│   ├── 00_approval.tex
│   ├── 00_acknowledgements.tex
│   ├── 00_abstract_gr.tex    # DONE (draft)
│   ├── 00_abstract_en.tex    # DONE (draft)
│   ├── 01_introduction.tex   # DONE (draft)
│   ├── 02_background.tex     # TODO
│   ├── 03_thistlethwaite.tex # TODO
│   ├── 04_kociemba.tex       # TODO
│   ├── 05_korf.tex           # TODO
│   ├── 06_heuristics.tex     # TODO
│   ├── 07_evaluation.tex     # TODO
│   ├── 08_implementation.tex # TODO
│   ├── 09_conclusions.tex    # TODO
│   ├── appendix_a.tex        # TODO
│   └── appendix_b.tex        # TODO
├── figures/                  # Benchmark figures (copied from ../figures/)
└── code/                     # Code snippets for appendix
```

## Compilation

### Requirements
- pdflatex
- biber (for bibliography)
- Standard LaTeX packages (should come with TeX Live or MiKTeX)

### Commands

```bash
# Full compilation (recommended first time)
make

# Quick compilation (no bibliography update)
make quick

# Clean auxiliary files
make clean

# View PDF
make view
```

### Manual Compilation

```bash
pdflatex main
biber main
pdflatex main
pdflatex main
```

## Writing Guide

1. Each chapter is in a separate file in `chapters/`
2. Edit individual chapter files, not `main.tex`
3. Add citations to `references.bib`
4. Use `\cite{key}` to cite references
5. Figures go in `figures/`

## Citation Examples

```latex
% In text
According to Korf \cite{korf1997finding}, pattern databases...

% Multiple citations
Several approaches exist \cite{korf1997finding,kociemba1992close,thistlethwaite1981}.

% With page number
As shown in \cite[p. 702]{korf1997finding}...
```

## Math Examples

```latex
% Inline
The state space has $4.3 \times 10^{19}$ configurations.

% Display
\begin{equation}
    f(n) = g(n) + h(n)
    \label{eq:astar}
\end{equation}

% Reference
As shown in Equation \ref{eq:astar}...
```

## Code Listings

```latex
\begin{lstlisting}[caption={IDA* algorithm},label={lst:idastar}]
def ida_star(cube, heuristic):
    threshold = heuristic(cube)
    while True:
        result = search(cube, 0, threshold)
        if result == FOUND:
            return solution
        threshold = result
\end{lstlisting}
```

## Progress Tracking

- [ ] Abstracts (GR/EN) - review and finalize
- [ ] Chapter 1: Introduction - expand
- [ ] Chapter 2: Background - write
- [ ] Chapter 3: Thistlethwaite - write
- [ ] Chapter 4: Kociemba - write
- [ ] Chapter 5: Korf - write
- [ ] Chapter 6: Heuristics - write (important: your novel contribution!)
- [ ] Chapter 7: Evaluation - write
- [ ] Chapter 8: Implementation - write
- [ ] Chapter 9: Conclusions - write
- [ ] Appendices - complete
- [ ] Final review and formatting
