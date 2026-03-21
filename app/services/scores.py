"""Compute investment scoring models: Graham Number, Piotroski F-Score, Magic Formula."""
import math
from typing import Optional


def graham_number(eps: Optional[float], book_value_per_share: Optional[float]) -> Optional[float]:
    """Graham Number = sqrt(22.5 * EPS * Book Value Per Share).
    Returns None if inputs are missing or negative."""
    if eps is None or book_value_per_share is None:
        return None
    if eps <= 0 or book_value_per_share <= 0:
        return None
    return round(math.sqrt(22.5 * eps * book_value_per_share), 2)


def piotroski_f_score(
    # Current year
    net_income: Optional[float],
    operating_cf: Optional[float],
    total_assets: Optional[float],
    total_assets_prev: Optional[float],
    total_debt: Optional[float],
    total_debt_prev: Optional[float],
    current_assets: Optional[float],
    current_liabilities: Optional[float],
    current_assets_prev: Optional[float],
    current_liabilities_prev: Optional[float],
    shares_outstanding: Optional[float],
    shares_outstanding_prev: Optional[float],
    gross_profit: Optional[float],
    revenue: Optional[float],
    gross_profit_prev: Optional[float],
    revenue_prev: Optional[float],
    net_income_prev: Optional[float],
) -> Optional[int]:
    """Piotroski F-Score (0-9). Higher is better.
    Returns None if insufficient data."""
    score = 0
    checks = 0

    # 1. Profitability: net income > 0
    if net_income is not None:
        if net_income > 0:
            score += 1
        checks += 1

    # 2. Operating cash flow > 0
    if operating_cf is not None:
        if operating_cf > 0:
            score += 1
        checks += 1

    # 3. ROA increasing (net_income / total_assets)
    if net_income is not None and total_assets and net_income_prev is not None and total_assets_prev:
        roa = net_income / total_assets
        roa_prev = net_income_prev / total_assets_prev
        if roa > roa_prev:
            score += 1
        checks += 1

    # 4. Quality of earnings: OCF > net income
    if operating_cf is not None and net_income is not None:
        if operating_cf > net_income:
            score += 1
        checks += 1

    # 5. Leverage: long-term debt decreasing
    if total_debt is not None and total_debt_prev is not None:
        if total_debt < total_debt_prev:
            score += 1
        checks += 1

    # 6. Liquidity: current ratio increasing
    if (current_assets and current_liabilities and
            current_assets_prev and current_liabilities_prev):
        cr = current_assets / current_liabilities
        cr_prev = current_assets_prev / current_liabilities_prev
        if cr > cr_prev:
            score += 1
        checks += 1

    # 7. No dilution: shares not increased
    if shares_outstanding is not None and shares_outstanding_prev is not None:
        if shares_outstanding <= shares_outstanding_prev:
            score += 1
        checks += 1

    # 8. Gross margin increasing
    if gross_profit and revenue and gross_profit_prev and revenue_prev:
        gm = gross_profit / revenue
        gm_prev = gross_profit_prev / revenue_prev
        if gm > gm_prev:
            score += 1
        checks += 1

    # 9. Asset turnover increasing
    if revenue and total_assets and revenue_prev and total_assets_prev:
        at = revenue / total_assets
        at_prev = revenue_prev / total_assets_prev
        if at > at_prev:
            score += 1
        checks += 1

    if checks < 4:
        return None  # Not enough data to be meaningful

    return score


def magic_formula_ranks(stocks: list[dict]) -> list[dict]:
    """Compute Magic Formula rank for a list of stocks.
    Each stock dict needs: ticker, operating_income, enterprise_value, net_fixed_assets,
    current_assets, current_liabilities.
    Returns list with added earnings_yield, return_on_capital, magic_rank."""

    # Compute earnings yield and return on capital
    scored = []
    for s in stocks:
        oi = s.get("operating_income")
        ev = s.get("enterprise_value")
        nfa = s.get("net_fixed_assets")
        ca = s.get("current_assets")
        cl = s.get("current_liabilities")

        ey = None
        roc = None

        if oi and ev and ev > 0:
            ey = oi / ev

        if oi and nfa is not None and ca is not None and cl is not None:
            working_capital = ca - cl
            invested_capital = nfa + working_capital
            if invested_capital > 0:
                roc = oi / invested_capital

        scored.append({**s, "earnings_yield": ey, "return_on_capital": roc})

    # Rank by earnings yield (higher = better rank)
    ey_valid = [s for s in scored if s["earnings_yield"] is not None]
    ey_valid.sort(key=lambda s: s["earnings_yield"], reverse=True)
    ey_ranks = {s["ticker"]: i + 1 for i, s in enumerate(ey_valid)}

    # Rank by return on capital (higher = better rank)
    roc_valid = [s for s in scored if s["return_on_capital"] is not None]
    roc_valid.sort(key=lambda s: s["return_on_capital"], reverse=True)
    roc_ranks = {s["ticker"]: i + 1 for i, s in enumerate(roc_valid)}

    # Combined rank
    for s in scored:
        ey_r = ey_ranks.get(s["ticker"])
        roc_r = roc_ranks.get(s["ticker"])
        if ey_r and roc_r:
            s["magic_rank"] = ey_r + roc_r
        else:
            s["magic_rank"] = None

    # Sort by magic rank (lower = better)
    scored.sort(key=lambda s: s["magic_rank"] if s["magic_rank"] is not None else 999999)

    return scored
