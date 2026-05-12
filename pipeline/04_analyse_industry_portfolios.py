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
# # 30 Industry Portfolios — Performance Analysis
#
# Value-weighted daily returns from Ken French's 30 Industry Portfolios.
# All series are anchored at 1 USD on 1926-06-30.

# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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
    paths.industries_synth_prices_path, index_col="date", parse_dates=True
)

# %% [markdown]
# ## Part 1 — Price and drawdown time series

# %% [markdown]
# ### Prices (linear scale)

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(prices.index, prices.values, linewidth=0.6, alpha=0.7)
ax.set_ylabel("Synthetic price (USD)")
ax.set_xlabel("Date")
ax.legend(prices.columns, ncol=5, fontsize=7, loc="upper left")
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_prices.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_prices.png
# :name: fig-04-industry-prices
# Synthetic price of a 1 USD investment in each of the 30 industry portfolios
# since 1926, linear scale.
# ```

# %% [markdown]
# ### Prices (log scale)

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(prices.index, prices.values, linewidth=0.6, alpha=0.7)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax.set_ylabel("Synthetic price (USD, log scale)")
ax.set_xlabel("Date")
ax.legend(prices.columns, ncol=5, fontsize=7, loc="upper left")
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_log_prices.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_log_prices.png
# :name: fig-04-industry-log-prices
# Same as above on a logarithmic price axis, making percentage growth
# comparable across the full history.
# ```

# %% [markdown]
# ### Drawdowns

# %%
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(prices.index, -compute_drawdowns(prices).values, linewidth=0.6, alpha=0.7)
ax.set_ylabel("Drawdown (%)")
ax.set_xlabel("Date")
ax.legend(prices.columns, ncol=5, fontsize=7, loc="lower left")
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_drawdowns.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_drawdowns.png
# :name: fig-04-industry-drawdowns
# Drawdowns from the running all-time high for each of the 30 industry
# portfolios. A value of −20 means the portfolio is 20% below its prior peak.
# ```

# %% [markdown]
# ## Part 2 — Yearly heatmaps

# %% [markdown]
# ### Yearly returns

# %%
yearly = compute_yearly_returns(prices)
yearly.index = yearly.index.year

fig, ax = plt.subplots(figsize=(18, 8))
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
ax.set_ylabel("Industry")
ax.tick_params(axis="x", labelsize=7, rotation=90)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_yearly_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_yearly_heatmap.png
# :name: fig-04-industry-yearly-heatmap
# Calendar-year returns for each of the 30 industry portfolios.
# Green = positive, red = negative; scale capped at ±50%.
# ```

# %% [markdown]
# ### Yearly maximum drawdowns

# %%
yearly_dd = compute_yearly_max_drawdowns(prices)
yearly_dd.index = yearly_dd.index.astype(int)

fig, ax = plt.subplots(figsize=(18, 8))
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
ax.set_ylabel("Industry")
ax.tick_params(axis="x", labelsize=7, rotation=90)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_yearly_dd_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_yearly_dd_heatmap.png
# :name: fig-04-industry-yearly-dd-heatmap
# Maximum within-year drawdown for each of the 30 industry portfolios.
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
for industry in prices.columns:
    ax.annotate(
        industry,
        (max_dd[industry], ann_ret[industry]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=8,
    )
ax.set_xlabel("Maximum drawdown (%)")
ax.set_ylabel("Annualized return (%)")
ax.grid(True, linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_risk_return.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_risk_return.png
# :name: fig-04-industry-risk-return
# Risk–return profile of the 30 industry portfolios. Maximum drawdown is used
# as the risk measure; annualized CAGR as the return measure.
# ```

# %% [markdown]
# ### Return vs volatility

# %%
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(vol_stats["ann_vol_pct"], ann_ret, s=60, zorder=3)
for industry in prices.columns:
    ax.annotate(
        industry,
        (vol_stats.loc[industry, "ann_vol_pct"], ann_ret[industry]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=8,
    )
ax.set_xlabel("Annualized volatility (%)")
ax.set_ylabel("Annualized return (%)")
ax.grid(True, linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_vol_return.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_vol_return.png
# :name: fig-04-industry-vol-return
# Annualized return vs annualized volatility for the 30 industry portfolios.
# ```

# %% [markdown]
# ### Return vs average worst drawdown

# %%
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(avg5_dd, ann_ret, s=60, zorder=3)
for industry in prices.columns:
    ax.annotate(
        industry,
        (avg5_dd[industry], ann_ret[industry]),
        textcoords="offset points",
        xytext=(5, 3),
        fontsize=8,
    )
ax.set_xlabel("Average max drawdown — 5 worst episodes (%)")
ax.set_ylabel("Annualized return (%)")
ax.grid(True, linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_dd_return.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_dd_return.png
# :name: fig-04-industry-dd-return
# Annualized return vs average of the 5 largest drawdowns per industry.
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

fig, ax = plt.subplots(figsize=(10, 12))
dd_bar.plot(kind="barh", ax=ax, width=0.7)
ax.set_xlabel("Drawdown (%)")
ax.legend(loc="lower right")
ax.grid(True, axis="x", linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_drawdown_bar.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_drawdown_bar.png
# :name: fig-04-industry-drawdown-bar
# Maximum drawdown and average of the 5 worst drawdowns per industry,
# sorted by maximum drawdown.
# ```

# %% [markdown]
# ### Drawdown duration bar chart

# %%
dur_bar = (dd_stats["avg_duration_5"] / 365).round(1).sort_values()

fig, ax = plt.subplots(figsize=(10, 12))
dur_bar.plot(kind="barh", ax=ax, color="steelblue", width=0.7)
ax.set_xlabel("Average duration of 5 worst drawdowns (years)")
ax.grid(True, axis="x", linewidth=0.4, alpha=0.6)
fig.tight_layout()
fig.savefig(paths.images_path / "04_industry_dd_duration_bar.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ```{figure} ../../output/images/04_industry_dd_duration_bar.png
# :name: fig-04-industry-dd-duration-bar
# Average recovery duration (years) of the 5 worst drawdowns per industry,
# sorted ascending.
# ```
