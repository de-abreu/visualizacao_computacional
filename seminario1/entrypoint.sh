#!/bin/bash
set -euo pipefail

NOTEBOOK="${NOTEBOOK:-app.ipynb}"
BASENAME="$(basename "$NOTEBOOK" .ipynb)"

echo "Converting notebook '$NOTEBOOK' -> '${BASENAME}.py'..."

jupyter nbconvert --to script "$NOTEBOOK" --output "$BASENAME"

echo "Running ${BASENAME}.py ..."
python "${BASENAME}.py"
