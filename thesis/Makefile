# Makefile for LaTeX thesis compilation

MAIN = main
LATEX = pdflatex
BIBER = biber

.PHONY: all clean view

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib chapters/*.tex
	$(LATEX) $(MAIN)
	$(BIBER) $(MAIN)
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)

quick:
	$(LATEX) $(MAIN)

clean:
	rm -f *.aux *.bbl *.bcf *.blg *.log *.out *.toc *.lof *.lot *.run.xml *.synctex.gz
	rm -f chapters/*.aux

view: $(MAIN).pdf
	open $(MAIN).pdf || xdg-open $(MAIN).pdf

# Watch for changes and recompile (requires fswatch or inotifywait)
watch:
	@echo "Watching for changes..."
	while true; do \
		inotifywait -e modify $(MAIN).tex chapters/*.tex references.bib; \
		make quick; \
	done
