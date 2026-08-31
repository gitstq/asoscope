#!/usr/bin/env bash
# Cross-platform build script for macOS / Linux.
# Builds a wheel (and sdist) into dist/ using only pip — no third-party
# build tooling is required.
set -euo pipefail

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "[build] python3 not found on PATH" >&2
  exit 1
fi

echo "[build] interpreter: $("$PYTHON" --version 2>&1)"
echo "[build] cleaning previous artifacts"
rm -rf dist build ./*.egg-info

echo "[build] running test suite"
"$PYTHON" -m unittest discover -s tests

echo "[build] building wheel into dist/"
"$PYTHON" -m pip wheel . --no-deps -w dist

echo "[build] artifacts:"
ls -lh dist
echo "[build] done. Install with: $PYTHON -m pip install dist/asoscope_cli-*.whl"
