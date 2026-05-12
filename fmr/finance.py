"""Financial computations operating on price or return Series/DataFrames."""

import numpy as np
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


def _individual_drawdowns_series(s: pd.Series) -> pd.DataFrame:
    """Identify individual drawdown events for a single price Series."""
    cols = ["start_date", "end_date", "date_trough", "max_drawdown_pct", "duration_days", "ongoing"]
    s = s.dropna()
    if len(s) < 2:
        return pd.DataFrame(columns=cols)

    cummax = s.cummax()
    in_dd = ((1 - s / cummax) * 100).values > 1e-10

    # Dates where a new all-time high was set (including the very first observation)
    prev_cummax = cummax.shift(1).fillna(-np.inf)
    new_high_dates = s.index[s.values >= prev_cummax.values]

    events = []
    dates = s.index
    n = len(dates)
    i = 0

    while i < n:
        if not in_dd[i]:
            i += 1
            continue

        # Peak: last new-high date strictly before the drawdown's first date
        candidates = new_high_dates[new_high_dates < dates[i]]
        peak_date = candidates[-1] if len(candidates) > 0 else dates[0]
        peak_val = cummax.iloc[i]

        # Walk to the end of the contiguous drawdown block
        j = i
        while j < n and in_dd[j]:
            j += 1

        segment = s.iloc[i:j]
        trough_date = segment.idxmin()
        trough_val = segment.min()

        if j < n:
            end_date = dates[j]
            ongoing = False
        else:
            end_date = dates[-1]
            ongoing = True

        events.append({
            "start_date": peak_date,
            "end_date": end_date,
            "date_trough": trough_date,
            "max_drawdown_pct": (1 - trough_val / peak_val) * 100,
            "duration_days": (end_date - peak_date).days,
            "ongoing": ongoing,
        })
        i = j

    return pd.DataFrame(events, columns=cols) if events else pd.DataFrame(columns=cols)


def compute_individual_drawdowns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Identify individual drawdown events for each asset.

    A drawdown runs from the prior peak through the trough until the price
    returns to the prior peak level (drawdown == 0).  If the series has not
    yet recovered, ``ongoing`` is True and ``end_date`` / ``duration_days``
    use the last available date.

    Returns a DataFrame with columns:
        asset, start_date, end_date, date_trough,
        max_drawdown_pct, duration_days, ongoing
    """
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    parts = []
    for col in prices.columns:
        df = _individual_drawdowns_series(prices[col])
        df.insert(0, "asset", col)
        parts.append(df)

    if not parts:
        return pd.DataFrame(columns=["asset", "start_date", "end_date", "date_trough",
                                     "max_drawdown_pct", "duration_days", "ongoing"])
    return pd.concat(parts, ignore_index=True)


def compute_worst_drawdown_stats(
    drawdown_events: pd.DataFrame,
    ns: list[int] | None = None,
) -> pd.DataFrame:
    """Average max-drawdown and duration for the N worst drawdowns per asset.

    'Worst' is defined by largest ``max_drawdown_pct``.  When an asset has
    fewer than N drawdowns the corresponding value is NaN.

    Parameters
    ----------
    drawdown_events:
        Output of :func:`compute_individual_drawdowns`.
    ns:
        List of N values to compute averages for.  Defaults to [3, 5, 10].

    Returns
    -------
    DataFrame indexed by asset with columns ``avg_max_dd_{n}`` and
    ``avg_duration_{n}`` for each n in *ns*.
    """
    if ns is None:
        ns = [3, 5, 10]

    records = []
    for asset, grp in drawdown_events.groupby("asset"):
        worst = grp.sort_values("max_drawdown_pct", ascending=False)
        row: dict = {"asset": asset}
        for n in ns:
            if len(worst) >= n:
                top = worst.head(n)
                row[f"avg_max_dd_{n}"] = top["max_drawdown_pct"].mean()
                row[f"avg_duration_{n}"] = top["duration_days"].mean()
            else:
                row[f"avg_max_dd_{n}"] = float("nan")
                row[f"avg_duration_{n}"] = float("nan")
        records.append(row)

    return pd.DataFrame(records).set_index("asset")


def compute_annualized_volatility(prices: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Volatility of returns, raw and annualized.

    Annualization uses square-root-of-time scaling based on the average
    calendar-day gap between observations, so the function works for any
    price frequency (daily, weekly, monthly, …).

    Returns
    -------
    DataFrame indexed by asset with columns:
        vol_pct     – standard deviation of period returns (%)
        ann_vol_pct – annualized volatility (%)
    """
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    returns_pct = prices.pct_change().dropna() * 100
    vol = returns_pct.std()

    avg_days = prices.index.to_series().diff().dt.days.dropna().mean()
    ann_factor = (365.25 / avg_days) ** 0.5

    return pd.DataFrame({"vol_pct": vol, "ann_vol_pct": vol * ann_factor})


def compute_yearly_max_drawdowns(prices: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Maximum drawdown within each calendar year.

    For each year the price segment runs from Dec 31 of the previous year
    (the year-opening anchor) through Dec 31 of the target year, so any
    decline below the year-start level is captured.

    Returns
    -------
    DataFrame of max drawdown (%) with years as the index and one column
    per asset.
    """
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    years = prices.index.year.unique()
    result: dict = {}
    for year in sorted(years):
        start = pd.Timestamp(f"{year - 1}-12-31")
        end = pd.Timestamp(f"{year}-12-31")
        segment = prices.loc[start:end]
        if len(segment) < 2:
            continue
        result[year] = compute_drawdowns(segment).max()

    return pd.DataFrame(result).T
