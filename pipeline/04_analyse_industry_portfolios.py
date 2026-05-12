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
from fmr.finance import compute_drawdowns, compute_yearly_returns, compute_annualized_returns

paths = ProjPaths()
prices = pd.read_csv(
    paths.industries_synth_prices_path, index_col="date", parse_dates=True
)

# %% [markdown]
# ## Prices (linear scale)

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
# ## Prices (log scale)

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
# ## Yearly returns heatmap

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
# ## Risk–return scatterplot

# %%
max_dd = compute_drawdowns(prices).max()
ann_ret = compute_annualized_returns(prices)

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
