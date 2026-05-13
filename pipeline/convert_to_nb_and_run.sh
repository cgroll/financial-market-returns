#!/bin/bash
set -e
MPLBACKEND=Agg uv run jupytext --to notebook --execute --set-kernel python3 --output "$2" "$1"
uv run python -c "
import nbformat
nb = nbformat.read('$2', as_version=4)
nb.cells = [c for c in nb.cells if not (c.cell_type == 'raw' and 'jupytext' in c.source)]
nb.metadata.pop('jupytext', None)
nbformat.write(nb, '$2')
"
