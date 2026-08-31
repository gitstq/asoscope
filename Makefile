PYTHON ?= python3

.PHONY: help install dev test clean build wheel sdist

help:
	@echo "asoscope developer targets:"
	@echo "  make install   Install the CLI into the current environment"
	@echo "  make dev       Install in editable mode"
	@echo "  make test      Run the full unittest suite (no network needed)"
	@echo "  make build     Build wheel + sdist into dist/"
	@echo "  make clean     Remove build artifacts"

install:
	$(PYTHON) -m pip install .

dev:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m unittest discover -s tests -v

wheel:
	$(PYTHON) -m pip wheel . --no-deps -w dist

sdist:
	$(PYTHON) -m pip wheel . --no-deps -w dist

build: clean
	$(PYTHON) -m pip wheel . --no-deps -w dist
	@echo "Artifacts in dist/:"
	@ls -la dist || true

clean:
	rm -rf build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
