import math
import time
import yfinance as yf
from curl_cffi.requests import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# chrome120 works in slim containers; newer profiles hit a BoringSSL TLS bug
_IMPERSONATE = "chrome120"

# ── EUR conversion ──────────────────────────────────────────────────────────
# Ticker suffix → native currency
_SUFFIX_CURRENCY = {
    ".ST": "SEK",
    ".OL": "NOK",
    ".CO": "DKK",
    ".HE": "EUR",
}

# Cached exchange rates: currency → EUR multiplier
_fx_cache: dict[str, float] = {}
_fx_cache_time: float = 0
_FX_CACHE_TTL = 3600 * 6  # refresh every 6 hours

_FX_PAIRS = {
    "SEK": "SEKEUR=X",
    "NOK": "NOKEUR=X",
    "DKK": "DKKEUR=X",
}


def _refresh_fx_rates():
    """Fetch current exchange rates from yfinance and cache them."""
    global _fx_cache, _fx_cache_time
    if time.time() - _fx_cache_time < _FX_CACHE_TTL and _fx_cache:
        return
    for currency, pair in _FX_PAIRS.items():
        try:
            t = yf.Ticker(pair, session=_get_session())
            rate = t.info.get("regularMarketPrice")
            if rate and rate > 0:
                _fx_cache[currency] = float(rate)
                logger.info(f"FX rate {currency}→EUR: {rate:.6f}")
        except Exception as e:
            logger.warning(f"Failed to fetch FX rate for {pair}: {e}")
    _fx_cache["EUR"] = 1.0
    _fx_cache_time = time.time()


def get_fx_rates() -> dict[str, float]:
    """Return current FX rates (currency → EUR). Fetches if cache is stale."""
    _refresh_fx_rates()
    return _fx_cache


def _ticker_currency(ticker: str) -> str:
    """Determine the native currency of a ticker from its suffix."""
    for suffix, currency in _SUFFIX_CURRENCY.items():
        if ticker.endswith(suffix):
            return currency
    return "EUR"


def _to_eur(value: Optional[float], currency: str) -> Optional[float]:
    """Convert a value from the given currency to EUR."""
    if value is None:
        return None
    if currency == "EUR":
        return value
    rate = _fx_cache.get(currency)
    if rate is None:
        _refresh_fx_rates()
        rate = _fx_cache.get(currency)
    if rate is None:
        logger.warning(f"No FX rate for {currency}, returning unconverted value")
        return value
    return round(value * rate, 4)


def _new_session() -> Session:
    return Session(impersonate=_IMPERSONATE)


_session = _new_session()
_request_count = 0


def _get_session() -> Session:
    """Rotate session every 25 requests to avoid Yahoo rate-limiting."""
    global _session, _request_count
    _request_count += 1
    if _request_count % 25 == 0:
        try:
            _session.close()
        except Exception:
            pass
        _session = _new_session()
    return _session


def _safe_float(val) -> Optional[float]:
    """Convert to float, rejecting inf/nan/stringified variants that asyncpg can't store."""
    if val is None:
        return None
    try:
        f = float(val)
        if math.isfinite(f):
            return f
    except (TypeError, ValueError):
        pass
    return None


def fetch_stock_info(ticker: str) -> Optional[dict]:
    """Fetch stock info from yfinance. All monetary values converted to EUR."""
    try:
        _refresh_fx_rates()
        ccy = _ticker_currency(ticker)
        t = yf.Ticker(ticker, session=_get_session())
        info = t.info
        if not info or info.get("regularMarketPrice") is None:
            return None
        return {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName", ticker),
            "exchange": info.get("exchange", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": _to_eur(_safe_float(info.get("marketCap")), ccy),
            "description": info.get("longBusinessSummary", ""),
            "price": _to_eur(_safe_float(info.get("regularMarketPrice") or info.get("currentPrice")), ccy),
            "change_pct": _safe_float(info.get("regularMarketChangePercent")),  # pct, no conversion
            "pe": _safe_float(info.get("trailingPE")),
            "pb": _safe_float(info.get("priceToBook")),
            "ps": _safe_float(info.get("priceToSalesTrailing12Months")),
            "ev_ebitda": _safe_float(info.get("enterpriseToEbitda")),
            "div_yield": _safe_float(info.get("dividendYield")),
            "roe": _pct(info.get("returnOnEquity")),
            "margin": _pct(info.get("profitMargins")),
            "eps": _to_eur(_safe_float(info.get("trailingEps")), ccy),
            "revenue": _to_eur(_safe_float(info.get("totalRevenue")), ccy),
            "revenue_growth": _pct(info.get("revenueGrowth")),
            "perf_1y": _pct(info.get("52WeekChange")),
            "report_quarter": _report_quarter(info.get("mostRecentQuarter")),
            "shares_outstanding": _safe_float(info.get("sharesOutstanding")),  # count, no conversion
            "enterprise_value": _to_eur(_safe_float(info.get("enterpriseValue")), ccy),
            "book_value_per_share": _to_eur(_safe_float(info.get("bookValue")), ccy),
        }
    except Exception as e:
        logger.warning(f"Failed to fetch {ticker}: {e}")
        return None


def fetch_price_history(ticker: str, period: str = "2y") -> list[dict]:
    """Fetch OHLCV history. Prices converted to EUR."""
    try:
        _refresh_fx_rates()
        ccy = _ticker_currency(ticker)
        t = yf.Ticker(ticker, session=_get_session())
        df = t.history(period=period)
        if df.empty:
            return []
        rows = []
        for date, row in df.iterrows():
            rows.append({
                "ticker": ticker,
                "date": date.strftime("%Y-%m-%d"),
                "open": round(_to_eur(row["Open"], ccy) or 0, 2),
                "high": round(_to_eur(row["High"], ccy) or 0, 2),
                "low": round(_to_eur(row["Low"], ccy) or 0, 2),
                "close": round(_to_eur(row["Close"], ccy) or 0, 2),
                "volume": int(row["Volume"]),
            })
        return rows
    except Exception as e:
        logger.warning(f"Failed to fetch prices for {ticker}: {e}")
        return []


def fetch_annual_financials(ticker: str) -> list[dict]:
    """Fetch annual income statement data. Monetary values converted to EUR."""
    try:
        _refresh_fx_rates()
        ccy = _ticker_currency(ticker)
        t = yf.Ticker(ticker, session=_get_session())
        inc = t.income_stmt
        if inc is None or inc.empty:
            return []
        rows = []
        for col in inc.columns:
            year = col.year
            revenue = _get_val(inc, col, "Total Revenue")
            net_income = _get_val(inc, col, "Net Income")
            eps_val = _get_val(inc, col, "Basic EPS") or _get_val(inc, col, "Diluted EPS")
            margin = None
            if revenue and net_income and revenue != 0:
                margin = round(net_income / revenue * 100, 2)
            operating_income = _get_val(inc, col, "Operating Income")
            ebitda = _get_val(inc, col, "EBITDA", "Normalized EBITDA")
            gross_profit = _get_val(inc, col, "Gross Profit")
            rows.append({
                "ticker": ticker,
                "year": year,
                "revenue": _to_eur(revenue, ccy),
                "operating_income": _to_eur(_safe_float(operating_income), ccy),
                "ebitda": _to_eur(_safe_float(ebitda), ccy),
                "net_income": _to_eur(net_income, ccy),
                "eps": _to_eur(eps_val, ccy),
                "profit_margin": margin,  # pct, no conversion
                "gross_profit": _to_eur(_safe_float(gross_profit), ccy),
            })
        return rows
    except Exception as e:
        logger.warning(f"Failed to fetch financials for {ticker}: {e}")
        return []


def _report_quarter(ts) -> Optional[str]:
    if ts is None:
        return None
    try:
        from datetime import datetime
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts)
        else:
            dt = ts
        q = (dt.month - 1) // 3 + 1
        return f"Q{q}-{dt.year}"
    except Exception:
        return None


def _pct(val) -> Optional[float]:
    if val is None:
        return None
    f = _safe_float(val)
    if f is None:
        return None
    return round(f * 100, 2)


def _get_val(df, col, *names):
    for name in names:
        if name in df.index:
            v = df.loc[name, col]
            if v is not None and str(v) != "nan":
                return float(v)
    return None


def fetch_quarterly_financials(ticker: str) -> list[dict]:
    """Fetch quarterly income statement data. Monetary values converted to EUR."""
    try:
        _refresh_fx_rates()
        ccy = _ticker_currency(ticker)
        t = yf.Ticker(ticker, session=_get_session())
        inc = t.quarterly_income_stmt
        if inc is None or inc.empty:
            return []
        rows = []
        for col in inc.columns:
            period = f"{col.year}-Q{(col.month - 1) // 3 + 1}"
            revenue = _get_val(inc, col, "Total Revenue")
            operating_income = _get_val(inc, col, "Operating Income")
            ebitda = _get_val(inc, col, "EBITDA", "Normalized EBITDA")
            net_income = _get_val(inc, col, "Net Income")
            eps_val = _get_val(inc, col, "Basic EPS", "Diluted EPS")
            margin = None
            if revenue and net_income and revenue != 0:
                margin = round(net_income / revenue * 100, 2)
            rows.append({
                "ticker": ticker,
                "period": period,
                "revenue": _to_eur(_safe_float(revenue), ccy),
                "operating_income": _to_eur(_safe_float(operating_income), ccy),
                "ebitda": _to_eur(_safe_float(ebitda), ccy),
                "net_income": _to_eur(_safe_float(net_income), ccy),
                "eps": _to_eur(_safe_float(eps_val), ccy),
                "profit_margin": _safe_float(margin),  # pct, no conversion
            })
        return rows
    except Exception as e:
        logger.warning(f"Failed to fetch quarterly financials for {ticker}: {e}")
        return []


def fetch_balance_sheet(ticker: str) -> list[dict]:
    """Fetch annual balance sheet data. All values converted to EUR."""
    try:
        _refresh_fx_rates()
        ccy = _ticker_currency(ticker)
        t = yf.Ticker(ticker, session=_get_session())
        bs = t.balance_sheet
        if bs is None or bs.empty:
            return []
        rows = []
        for col in bs.columns:
            year = col.year
            total_assets = _get_val(bs, col, "Total Assets")
            total_debt = _get_val(bs, col, "Total Debt")
            cash = _get_val(bs, col, "Cash And Cash Equivalents",
                            "Cash Cash Equivalents And Short Term Investments")
            net_debt = None
            if total_debt is not None and cash is not None:
                net_debt = total_debt - cash
            total_equity = _get_val(bs, col, "Stockholders Equity",
                                    "Total Equity Gross Minority Interest")
            intangible_assets = _get_val(bs, col, "Goodwill And Other Intangible Assets",
                                         "Intangible Assets")
            current_assets = _get_val(bs, col, "Current Assets")
            current_liabilities = _get_val(bs, col, "Current Liabilities")
            net_fixed_assets = None
            if total_assets is not None and current_assets is not None:
                nfa = total_assets - current_assets
                if intangible_assets is not None:
                    nfa -= intangible_assets
                net_fixed_assets = nfa
            rows.append({
                "ticker": ticker,
                "year": year,
                "total_assets": _to_eur(_safe_float(total_assets), ccy),
                "total_debt": _to_eur(_safe_float(total_debt), ccy),
                "net_debt": _to_eur(_safe_float(net_debt), ccy),
                "cash": _to_eur(_safe_float(cash), ccy),
                "total_equity": _to_eur(_safe_float(total_equity), ccy),
                "intangible_assets": _to_eur(_safe_float(intangible_assets), ccy),
                "current_assets": _to_eur(_safe_float(current_assets), ccy),
                "current_liabilities": _to_eur(_safe_float(current_liabilities), ccy),
                "net_fixed_assets": _to_eur(_safe_float(net_fixed_assets), ccy),
            })
        return rows
    except Exception as e:
        logger.warning(f"Failed to fetch balance sheet for {ticker}: {e}")
        return []


def fetch_cashflow(ticker: str) -> list[dict]:
    """Fetch annual cash flow data. All values converted to EUR."""
    try:
        _refresh_fx_rates()
        ccy = _ticker_currency(ticker)
        t = yf.Ticker(ticker, session=_get_session())
        cf = t.cashflow
        if cf is None or cf.empty:
            return []
        rows = []
        for col in cf.columns:
            year = col.year
            operating_cf = _get_val(cf, col, "Operating Cash Flow")
            capex = _get_val(cf, col, "Capital Expenditure")
            free_cf = None
            if operating_cf is not None and capex is not None:
                free_cf = operating_cf + capex  # capex is negative in yfinance
            rows.append({
                "ticker": ticker,
                "year": year,
                "operating_cf": _to_eur(_safe_float(operating_cf), ccy),
                "capex": _to_eur(_safe_float(capex), ccy),
                "free_cf": _to_eur(_safe_float(free_cf), ccy),
            })
        return rows
    except Exception as e:
        logger.warning(f"Failed to fetch cashflow for {ticker}: {e}")
        return []
