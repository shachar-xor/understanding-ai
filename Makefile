# Makefile for the "Understanding AI for Geeks" presentation.
#
#   make            build the .pptx (creates the venv on first run)
#   make assets     regenerate the matplotlib/photo PNGs in assets/
#   make install    create .venv and install pinned dependencies
#   make open       build, then open the deck in PowerPoint
#   make clean      remove the generated .pptx
#   make help       list targets

PPTX   := understanding_ai_for_geeks.pptx
VENV   := .venv
PY     := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

.DEFAULT_GOAL := build
.PHONY: build assets install open clean help

# Build the presentation. Order-only dep on the venv so it is created if missing.
# Refuses to overwrite while the deck is open in PowerPoint (lock would clobber it).
build: | $(PY)
	@if lsof "$(PPTX)" >/dev/null 2>&1; then \
		echo "ERROR: $(PPTX) is open (PowerPoint). Close it first, then re-run make."; \
		exit 1; \
	fi
	$(PY) build_presentation.py

# Regenerate the generated image assets (diagrams, ideas spectrum, d20 cutout).
assets: | $(PY)
	$(PY) generate_agent_diagram.py
	$(PY) generate_context_growth.py
	$(PY) generate_mapreduce_tree.py
	$(PY) generate_got_assets.py
	$(PY) generate_ideas_spectrum.py
	$(PY) make_d20_asset.py

install: $(PY)

# Create the virtualenv and install dependencies. The recipe's target is the
# interpreter itself, so it only runs when .venv is missing.
$(PY): requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	@touch $(PY)

open: build
	open "$(PPTX)"

clean:
	rm -f "$(PPTX)"

help:
	@echo "Targets:"
	@echo "  build    (default) build $(PPTX)"
	@echo "  assets   regenerate PNGs in assets/"
	@echo "  install  create .venv and install dependencies"
	@echo "  open     build then open in PowerPoint"
	@echo "  clean    remove $(PPTX)"
