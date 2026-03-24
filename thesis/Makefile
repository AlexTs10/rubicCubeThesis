# Makefile for thesis compilation

ROOT := $(abspath ..)
MAIN := main
PYTHON ?= python3
WORKFLOW := $(ROOT)/scripts/thesis_workflow.py

.PHONY: all auto local docker quick clean view

all: auto

auto:
	$(PYTHON) $(WORKFLOW) build --mode auto

local:
	$(PYTHON) $(WORKFLOW) build --mode local

docker:
	$(PYTHON) $(WORKFLOW) build --mode docker

quick: auto

clean:
	rm -f *.aux *.bbl *.bcf *.blg *.log *.out *.toc *.lof *.lot *.run.xml *.synctex.gz *.xdv
	rm -f *.fdb_latexmk *.fls
	rm -f chapters/*.aux

view: $(MAIN).pdf
	open $(MAIN).pdf || xdg-open $(MAIN).pdf

$(MAIN).pdf: auto
