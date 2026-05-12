# Contribution Conventions

This document describes the project structure and conventions.
It is written for human contributors and AI agents alike.

## Project Structure

```
project-root/
├── fmr/                     # Python package — shared utilities
│   ├── __init__.py
│   ├── paths.py             # Centralized path configuration
│   ├── finance.py           # Financial computations (drawdowns, returns)
│   └── country_codes.py     # Ken French filename → ISO 3166-1 alpha-3 mapping
├── pipeline/                # Data pipeline scripts
│   ├── 01_download_*.py     # Pure data acquisition (no charts)
│   ├── 02_process_*.py      # Data cleaning and transformation
│   ├── 03_create_*.py       # Derived datasets
│   └── 04_analyse_*.py      # Analysis scripts → become book notebooks
├── book/                    # MyST Jupyter Book source
│   ├── notebooks/           # Executed .ipynb files (produced by Snakemake)
│   ├── markdown/            # Static hand-written content
│   └── myst.yml             # Book configuration and table of contents
├── data/
│   ├── downloads/           # Raw downloaded data (git-ignored)
│   └── processed/           # Processed/transformed data (git-ignored)
├── output/
│   ├── images/              # Chart images saved by pipeline scripts (git-tracked)
│   └── reports/             # Report files
├── Snakefile                # Pipeline definition
└── pyproject.toml           # Dependencies managed by uv
```

## Tools

| Tool | Purpose |
|------|---------|
| **uv** | Package and environment management |
| **Snakemake** | Pipeline orchestration (dependency-aware task runner) |
| **jupytext** | Execute `.py` analysis scripts → `.ipynb` notebooks |
| **MyST / mystmd** | Build the HTML book from notebooks and markdown |

## Snakemake Primer

Snakemake is a Make-inspired workflow manager written in Python.
It reads the `Snakefile` in the project root.

### Core concept: rules

A rule declares *how* to produce an output from inputs:

```python
rule my_stage:
    input:
        data   = "data/processed/something.csv",
        script = "pipeline/04_analyse.py",
    output:
        notebook = "book/notebooks/04_analyse.ipynb",
        img      = "output/images/04_chart.png",
    shell:
        "MPLBACKEND=Agg uv run jupytext ..."
```

Snakemake compares **file modification timestamps**: if all outputs are newer
than all inputs, the rule is skipped.

### Download rules

Download rules have no inputs, only a `directory()` output. Snakemake skips
the rule when the directory already exists; it runs when the directory is absent.

```python
rule download_something:
    output:
        directory("data/downloads/something"),
    shell:
        "uv run python pipeline/01_download_something.py"
```

To force a fresh download: delete the directory and re-run, or use
`snakemake --cores 1 -R <rule>`.

### Running the pipeline

```bash
snakemake --cores 1 -n       # dry-run: show what would execute
snakemake --cores 4          # run with up to 4 parallel jobs
snakemake --cores 1 <file>   # build one specific output file
snakemake --cores 1 -R <rule>  # force-re-run a specific rule
```

Or via Make shortcuts:

```bash
make run       # snakemake --cores 4
make dry-run   # snakemake --cores 1 -n
make serve     # myst start (local book preview)
```

### The `rule all` convention

The top of the Snakefile defines a pseudo-rule whose inputs are the final
targets. Running `snakemake --cores N` (no target argument) builds these:

```python
rule all:
    input:
        "book/notebooks/04_analyse_industry_portfolios.ipynb",
```

## Pipeline Conventions

### Script numbering

| Prefix | Type | Purpose |
|--------|------|---------|
| `01_download_*` | Pure data | Download and extract raw data |
| `02_process_*` | Pure data | Clean and reshape raw data |
| `03_create_*` | Pure data | Derive new datasets from processed data |
| `04_analyse_*` | Analysis | Produce charts and notebook |

### Pure data scripts (`01_*`, `02_*`, `03_*`)
- No charts or visualizations.
- Read/write data files only.
- Not converted to notebooks.

### Analysis scripts (`04_*` and higher)
- Use jupytext `# %%` cell markers and a jupytext/kernelspec header.
- Save all figures to `output/images/` via `fig.savefig()`.
- Use MyST `{figure}` directives in `# %% [markdown]` cells.
- Snakemake runs them via jupytext → produces an executed `.ipynb` in `book/notebooks/`.

### Jupytext header for analysis scripts

```python
# ---
# jupytext:
#   text_representation:
#     format_name: percent
# kernelspec:
#   display_name: Python 3
#   language: python
#   name: python3
# ---
```

### Saving figures and referencing them

```python
# %%
fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(...)
fig.savefig(paths.images_path / "04_my_chart.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_my_chart.png
# :name: fig-04-my-chart
# Caption describing the figure.
# ```
```

The path `../../output/images/` is relative to `book/notebooks/` where the
generated `.ipynb` lives.

Naming convention: `<script_number>_<descriptive_name>.png`.

### Snakemake rule for analysis scripts

```python
rule analyse_something:
    input:
        script = "pipeline/04_analyse_something.py",
        data   = "data/processed/something.csv",
    output:
        notebook = "book/notebooks/04_analyse_something.ipynb",
        img      = "output/images/04_chart.png",
    shell:
        """
        MPLBACKEND=Agg uv run jupytext --to notebook --execute \
            --set-kernel python3 \
            --output {output.notebook} {input.script} && \
        uv run python -c "
import nbformat
nb = nbformat.read('{output.notebook}', as_version=4)
nb.cells = [c for c in nb.cells
            if not (c.cell_type == 'raw' and 'jupytext' in c.source)]
nb.metadata.pop('jupytext', None)
nbformat.write(nb, '{output.notebook}')
"
        """
```

The post-processing step strips the raw jupytext metadata cell and the
notebook-level jupytext key that MyST does not recognize.
`MPLBACKEND=Agg` makes `plt.show()` a no-op in headless mode.

## Path Conventions

All scripts must be runnable from any working directory. Use `ProjPaths`
from `fmr/paths.py`:

```python
from fmr.paths import ProjPaths

paths = ProjPaths()

df = pd.read_csv(paths.countries_synth_prices_path)
fig.savefig(paths.images_path / "04_chart.png")
```

Key paths:

| Property | Directory |
|----------|-----------|
| `paths.data_path` | `data/` |
| `paths.downloads_path` | `data/downloads/` |
| `paths.processed_data_path` | `data/processed/` |
| `paths.images_path` | `output/images/` |
| `paths.pipeline_path` | `pipeline/` |
| `paths.international_countries_path` | `data/downloads/ken_french/international_countries/` |
| `paths.international_countries_monthly_returns_path` | `data/processed/ken_french/international_countries/monthly_returns/` |
| `paths.industry_portfolios_30_path` | `data/downloads/ken_french/industry_portfolios_30/` |
| `paths.industry_portfolios_30_daily_returns_path` | `data/processed/ken_french/industry_portfolios_30/daily_returns.csv` |
| `paths.countries_synth_prices_path` | `data/processed/ken_french/countries_synth_prices.csv` |
| `paths.industries_synth_prices_path` | `data/processed/ken_french/industries_synth_prices.csv` |

## Adding a New Pipeline Stage

1. **Write the script** in `pipeline/`.
2. **Add a property** to `fmr/paths.py` for every new data file:
   ```python
   @property
   def my_new_file(self) -> Path:
       """One-line description."""
       return self.processed_data_path / "my_data.csv"
   ```
3. **Add a rule** to `Snakefile` with `input`, `output`, and `shell`.
4. **Add the notebook** to `rule all` in `Snakefile` (if analysis).
5. **Add the notebook** to the `toc` in `book/myst.yml`.

## Git Conventions

| Tracked | Not tracked |
|---------|-------------|
| `pipeline/*.py` source files | `data/downloads/*` |
| `book/notebooks/*.ipynb` generated notebooks | `data/processed/*` |
| `output/images/*.png` generated charts | `.venv/` |
| `book/markdown/*.md` static content | `.snakemake/` |

Notebooks and images are tracked so the book can be rebuilt from git without
re-running the pipeline (CI only runs `myst build`).

## Workflow Summary

```
1. Write pipeline script in pipeline/
2. Add Snakemake rule in Snakefile
3. make run          ← execute pipeline
4. make serve        ← preview book locally
5. git add / commit  ← commit notebooks + images
6. git push          ← CI deploys to GitHub Pages
```
