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
# # Synthetic Prices from Percentage Returns
#
# Converts percentage returns to synthetic price series anchored at 1 USD.
# Each series is prepended with a base period at value 1, then compounded:
#   R = 1 + r_pct / 100,  price = cumprod(R)

# %%
import pandas as pd
from fmr.paths import ProjPaths

paths = ProjPaths()
paths.ken_french_processed_path.mkdir(parents=True, exist_ok=True)

# %%
# --- Countries (monthly) ---

country_files = sorted(paths.international_countries_monthly_returns_path.glob("*.csv"))

series = {}
for f in country_files:
    iso3 = f.stem
    s = pd.read_csv(f, index_col="date", parse_dates=True)["pct_return"]
    base_date = s.index[0] - pd.offsets.MonthEnd(1)
    s = pd.concat([pd.Series([0.0], index=[base_date]), s])
    series[iso3] = (1 + s / 100).cumprod()

countries = pd.DataFrame(series)
countries.index.name = "date"
countries.to_csv(paths.countries_synth_prices_path)
print(f"Countries: {countries.shape} → {paths.countries_synth_prices_path}")

# %%
# --- Industries (daily) ---

df = pd.read_csv(paths.industry_portfolios_30_daily_returns_path, index_col="date", parse_dates=True)

base_date = df.index[0] - pd.Timedelta(days=1)
base_row = pd.DataFrame([[0.0] * len(df.columns)], index=[base_date], columns=df.columns)
df = pd.concat([base_row, df])

industries = (1 + df / 100).cumprod()
industries.index.name = "date"
industries.to_csv(paths.industries_synth_prices_path)
print(f"Industries: {industries.shape} → {paths.industries_synth_prices_path}")
