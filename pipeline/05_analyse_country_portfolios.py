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
# # International Country Portfolios — Performance Analysis
#
# Value-weighted monthly returns from Ken French's International Country Portfolios.
# All series are anchored at 1 USD on their first available month-end date.

# %%
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns
from fmr.paths import ProjPaths
from fmr.finance import (
    compute_drawdowns,
    compute_yearly_returns,
    compute_annualized_returns,
    compute_individual_drawdowns,
    compute_worst_drawdown_stats,
    compute_annualized_volatility,
    compute_yearly_max_drawdowns,
)

paths = ProjPaths()
prices = pd.read_csv(
    paths.countries_synth_prices_path, index_col="date", parse_dates=True
)

# %% [markdown]
# ## Data coverage

# %% [markdown]
# ### Date ranges

# %%
first_dates = prices.apply(lambda s: s.first_valid_index())
last_dates = prices.apply(lambda s: s.last_valid_index())
order = first_dates.sort_values().index

fig, ax = plt.subplots(figsize=(10, 7))
for i, country in enumerate(order):
    start = mdates.date2num(first_dates[country])
    end = mdates.date2num(last_dates[country])
    ax.barh(i, end - start, left=start, height=0.6, color="steelblue", alpha=0.8)

ax.set_yticks(range(len(order)))
ax.set_yticklabels(order)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.YearLocator(10))
ax.grid(True, axis="x", linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_date_ranges.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_date_ranges.png
# :name: fig-05-country-date-ranges
# Observation window for each country portfolio, sorted by start date.
# ```

# %% [markdown]
# ### Filter to equal-length series
#
# Keep only countries whose data begins at the earliest available date, then
# drop any remaining rows with missing values so that all retained series have
# identical length.

# %%
earliest_start = first_dates.min()
prices = prices.loc[:, first_dates == earliest_start].dropna()

# %% [markdown]
# ## Part 1 — Price and drawdown time series

# %% [markdown]
# ### Prices (linear scale)

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(prices.index, prices.values, linewidth=0.8, alpha=0.7)
ax.set_ylabel("Synthetic price (USD)")
ax.set_xlabel("Date")
ax.legend(prices.columns, ncol=4, fontsize=7, loc="upper left")
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_prices.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_prices.png
# :name: fig-05-country-prices
# Synthetic price of a 1 USD investment in each of the international country
# portfolios since their first available month-end, linear scale.
# ```

# %% [markdown]
# ### Prices (log scale)

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(prices.index, prices.values, linewidth=0.8, alpha=0.7)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax.set_ylabel("Synthetic price (USD, log scale)")
ax.set_xlabel("Date")
ax.legend(prices.columns, ncol=4, fontsize=7, loc="upper left")
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_log_prices.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_log_prices.png
# :name: fig-05-country-log-prices
# Same as above on a logarithmic price axis, making percentage growth
# comparable across the full history.
# ```

# %% [markdown]
# ### Drawdowns

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(prices.index, -compute_drawdowns(prices).values, linewidth=0.8, alpha=0.7)
ax.set_ylabel("Drawdown (%)")
ax.set_xlabel("Date")
ax.legend(prices.columns, ncol=4, fontsize=7, loc="lower left")
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_drawdowns.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_drawdowns.png
# :name: fig-05-country-drawdowns
# Drawdowns from the running all-time high for each country portfolio.
# A value of −20 means the portfolio is 20% below its prior peak.
# ```

# %% [markdown]
# ## Part 2 — Yearly heatmaps

# %% [markdown]
# ### Yearly returns

# %%
yearly = compute_yearly_returns(prices)
yearly.index = yearly.index.year

fig, ax = plt.subplots(figsize=(14, 7))
sns.heatmap(
    yearly.T,
    ax=ax,
    cmap="RdYlGn",
    center=0,
    vmin=-50,
    vmax=50,
    linewidths=0.3,
    cbar_kws={"label": "Return (%)"},
)
ax.set_xlabel("Year")
ax.set_ylabel("Country")
ax.tick_params(axis="x", labelsize=7, rotation=90)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_yearly_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_yearly_heatmap.png
# :name: fig-05-country-yearly-heatmap
# Calendar-year returns for each country portfolio.
# Green = positive, red = negative; scale capped at ±50%.
# ```

# %% [markdown]
# ### Yearly maximum drawdowns

# %%
yearly_dd = compute_yearly_max_drawdowns(prices)
yearly_dd.index = yearly_dd.index.astype(int)

fig, ax = plt.subplots(figsize=(14, 7))
sns.heatmap(
    yearly_dd.T,
    ax=ax,
    cmap="Reds",
    vmin=0,
    vmax=50,
    linewidths=0.3,
    cbar_kws={"label": "Max drawdown (%)"},
)
ax.set_xlabel("Year")
ax.set_ylabel("Country")
ax.tick_params(axis="x", labelsize=7, rotation=90)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_yearly_dd_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_yearly_dd_heatmap.png
# :name: fig-05-country-yearly-dd-heatmap
# Maximum within-year drawdown for each country portfolio.
# Each year's drawdown is anchored to the Dec 31 price of the prior year.
# ```

# %% [markdown]
# ## Part 3 — Risk–return scatterplots

# %%
ann_ret = compute_annualized_returns(prices)
max_dd = compute_drawdowns(prices).max()
vol_stats = compute_annualized_volatility(prices)
dd_events = compute_individual_drawdowns(prices)
dd_stats = compute_worst_drawdown_stats(dd_events, ns=[3, 5, 10])
avg5_dd = dd_stats["avg_max_dd_5"].reindex(prices.columns)

# %% [markdown]
# ### Return vs maximum drawdown

# %%
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(max_dd, ann_ret, s=60, zorder=3)
for country in prices.columns:
    ax.annotate(
        country,
        (max_dd[country], ann_ret[country]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=8,
    )
ax.set_xlabel("Maximum drawdown (%)")
ax.set_ylabel("Annualized return (%)")
ax.grid(True, linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_risk_return.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_risk_return.png
# :name: fig-05-country-risk-return
# Risk–return profile of the country portfolios. Maximum drawdown is used
# as the risk measure; annualized CAGR as the return measure.
# ```

# %% [markdown]
# ### Return vs volatility

# %%
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(vol_stats["ann_vol_pct"], ann_ret, s=60, zorder=3)
for country in prices.columns:
    ax.annotate(
        country,
        (vol_stats.loc[country, "ann_vol_pct"], ann_ret[country]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=8,
    )
ax.set_xlabel("Annualized volatility (%)")
ax.set_ylabel("Annualized return (%)")
ax.grid(True, linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_vol_return.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_vol_return.png
# :name: fig-05-country-vol-return
# Annualized return vs annualized volatility for the country portfolios.
# ```

# %% [markdown]
# ### Return vs average worst drawdown

# %%
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(avg5_dd, ann_ret, s=60, zorder=3)
for country in prices.columns:
    ax.annotate(
        country,
        (avg5_dd[country], ann_ret[country]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=8,
    )
ax.set_xlabel("Average max drawdown — 5 worst episodes (%)")
ax.set_ylabel("Annualized return (%)")
ax.grid(True, linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_dd_return.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_dd_return.png
# :name: fig-05-country-dd-return
# Annualized return vs average of the 5 largest drawdowns per country.
# ```

# %% [markdown]
# ## Part 4 — Drawdown magnitudes and durations

# %% [markdown]
# ### Drawdown magnitude bar chart

# %%
dd_bar = pd.DataFrame({
    "Max drawdown": max_dd,
    "Avg 5 worst": dd_stats["avg_max_dd_5"],
}).sort_values("Max drawdown")

fig, ax = plt.subplots(figsize=(10, 8))
dd_bar.plot(kind="barh", ax=ax, width=0.7)
ax.set_xlabel("Drawdown (%)")
ax.legend(loc="lower right")
ax.grid(True, axis="x", linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_drawdown_bar.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_drawdown_bar.png
# :name: fig-05-country-drawdown-bar
# Maximum drawdown and average of the 5 worst drawdowns per country,
# sorted by maximum drawdown.
# ```

# %% [markdown]
# ### Drawdown duration bar chart

# %%
dur_bar = (dd_stats["avg_duration_5"] / 365).round(1).sort_values()

fig, ax = plt.subplots(figsize=(10, 8))
dur_bar.plot(kind="barh", ax=ax, color="steelblue", width=0.7)
ax.set_xlabel("Average duration of 5 worst drawdowns (years)")
ax.grid(True, axis="x", linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "05_country_dd_duration_bar.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/05_country_dd_duration_bar.png
# :name: fig-05-country-dd-duration-bar
# Average recovery duration (years) of the 5 worst drawdowns per country,
# sorted ascending.
# ```
