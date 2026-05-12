"""Financial computations operating on price or return Series/DataFrames."""

import pandas as pd


def compute_drawdowns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Drawdown in percent from the running peak.

    Formula: (1 - price / cummax_price) * 100
    A 20% drawdown is returned as 20.0.
    """
    return (1 - prices / prices.cummax()) * 100


def compute_yearly_returns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Calendar-year percentage returns derived from year-end prices."""
    return prices.resample("YE").last().pct_change() * 100


def compute_annualized_returns(prices: pd.DataFrame | pd.Series) -> pd.Series:
    """Annualized percentage return from first to last non-NaN observation.

    Uses the compound annual growth rate formula:
        CAGR = (price_end / price_start) ^ (1 / n_years) - 1
    """
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    results = {}
    for col in prices.columns:
        s = prices[col].dropna()
        n_years = (s.index[-1] - s.index[0]).days / 365.25
        results[col] = ((s.iloc[-1] / s.iloc[0]) ** (1 / n_years) - 1) * 100

    return pd.Series(results, name="annualized_return_pct")
