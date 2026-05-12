# ---
# jupytext:
#   text_representation:
#     format_name: percent
# kernelspec:
#   display_name: Python 3
#   language: python
#   name: python3
# ---

# %% [markdown]
# # Ken French International Country Returns
#
# Parses the value-weight dollar market returns from the Ken French
# international country data files and saves one CSV per country.

# %%
import re
import shutil
import pandas as pd
from pathlib import Path
from fmr.paths import ProjPaths
from fmr.country_codes import FRENCH_TO_ISO3

paths = ProjPaths()
src = paths.international_countries_path
dest = paths.international_countries_monthly_returns_path

if dest.exists():
    shutil.rmtree(dest)
dest.mkdir(parents=True)

# %%
def parse_vw_dollar_mkt(filepath: Path) -> pd.Series:
    """Extract the Mkt column from the first Value-Weight Dollar Returns section."""
    lines = filepath.read_text().splitlines()

    # Find the first "Value-Weight Dollar Returns" header line
    start = None
    for i, line in enumerate(lines):
        if "Value-Weight Dollar Returns" in line:
            # Data begins 3 lines later (two header lines + column names)
            start = i + 3
            break

    if start is None:
        raise ValueError(f"No 'Value-Weight Dollar Returns' section found in {filepath}")

    records = {}
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            break  # blank line marks end of section
        parts = stripped.split()
        if not re.match(r"^\d{6}$", parts[0]):
            break  # non-data line (shouldn't happen, but guard anyway)
        yyyymm = parts[0]
        mkt = float(parts[1])
        records[yyyymm] = mkt

    s = pd.Series(records, name="pct_return")
    s.index = pd.to_datetime(s.index, format="%Y%m") + pd.offsets.MonthEnd(0)
    s.index.name = "date"
    return s


# %%
for country_file in sorted(src.glob("*.Dat")):
    stem = country_file.stem
    iso3 = FRENCH_TO_ISO3[stem]
    s = parse_vw_dollar_mkt(country_file)
    out = dest / f"{iso3}.csv"
    s.to_csv(out, header=True)
    print(f"{stem}: {len(s)} rows ({s.index[0].date()} – {s.index[-1].date()}) → {out.name}")
