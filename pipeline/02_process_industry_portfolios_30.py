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
# # Ken French 30 Industry Portfolios — Daily Returns
#
# Extracts the average value-weighted daily returns from the Ken French
# 30 Industry Portfolios file and saves a single tidy CSV.

# %%
import re
import pandas as pd
from pathlib import Path
from fmr.paths import ProjPaths

paths = ProjPaths()

src = next(paths.industry_portfolios_30_path.glob("*.txt"))
out = paths.industry_portfolios_30_daily_returns_path
out.parent.mkdir(parents=True, exist_ok=True)

# %%
lines = src.read_text(encoding="latin-1").splitlines()

# Find "Average Value Weighted Returns -- Daily"
start = None
for i, line in enumerate(lines):
    if re.search(r"Average Value Weighted Returns\s*--\s*Daily", line):
        start = i + 1  # next line is column headers
        break

if start is None:
    raise ValueError("Could not find 'Average Value Weighted Returns -- Daily' section")

columns = lines[start].split()
data_start = start + 1

records = []
for line in lines[data_start:]:
    stripped = line.strip()
    if not stripped:
        break
    parts = stripped.split()
    if not re.match(r"^\d{8}$", parts[0]):
        break
    date = pd.to_datetime(parts[0], format="%Y%m%d")
    values = [float(v) for v in parts[1:]]
    records.append([date] + values)

df = pd.DataFrame(records, columns=["date"] + columns)
df = df.set_index("date")

# Replace missing value sentinels with NaN
df = df.replace(-99.99, float("nan")).replace(-999.0, float("nan"))

print(df.head())
print(f"\nRows: {len(df)}, from {df.index[0].date()} to {df.index[-1].date()}")
print(f"Columns: {list(df.columns)}")

df.to_csv(out)
print(f"\nSaved → {out}")
