import math
import yfinance as yf
from curl_cffi.requests import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# chrome120 works in slim containers; newer profiles hit a BoringSSL TLS bug
_IMPERSONATE = "chrome120"


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
    """Fetch stock info from yfinance."""
    try:
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
            "market_cap": _safe_float(info.get("marketCap")),
            "description": info.get("longBusinessSummary", ""),
            "price": _safe_float(info.get("regularMarketPrice") or info.get("currentPrice")),
            "change_pct": _safe_float(info.get("regularMarketChangePercent")),
            "pe": _safe_float(info.get("trailingPE")),
            "pb": _safe_float(info.get("priceToBook")),
            "ps": _safe_float(info.get("priceToSalesTrailing12Months")),
            "ev_ebitda": _safe_float(info.get("enterpriseToEbitda")),
            "div_yield": _pct(info.get("dividendYield")),
            "roe": _pct(info.get("returnOnEquity")),
            "margin": _pct(info.get("profitMargins")),
            "eps": _safe_float(info.get("trailingEps")),
            "revenue": _safe_float(info.get("totalRevenue")),
            "revenue_growth": _pct(info.get("revenueGrowth")),
            "perf_1y": _pct(info.get("52WeekChange")),
            "report_quarter": _report_quarter(info.get("mostRecentQuarter")),
        }
    except Exception as e:
        logger.warning(f"Failed to fetch {ticker}: {e}")
        return None


def fetch_price_history(ticker: str, period: str = "2y") -> list[dict]:
    """Fetch OHLCV history."""
    try:
        t = yf.Ticker(ticker, session=_get_session())
        df = t.history(period=period)
        if df.empty:
            return []
        rows = []
        for date, row in df.iterrows():
            rows.append({
                "ticker": ticker,
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })
        return rows
    except Exception as e:
        logger.warning(f"Failed to fetch prices for {ticker}: {e}")
        return []


def fetch_annual_financials(ticker: str) -> list[dict]:
    """Fetch annual income statement data."""
    try:
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
            rows.append({
                "ticker": ticker,
                "year": year,
                "revenue": revenue,
                "net_income": net_income,
                "eps": eps_val,
                "profit_margin": margin,
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
