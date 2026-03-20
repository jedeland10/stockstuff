#!/usr/bin/env python3
"""Backfill price history, financials, balance sheet, and cash flow for all seeded stocks."""
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncpg
from curl_cffi.requests import Session as CffiSession
from app.config import DATABASE_URL
from app.database import init_db
from app.services.fetcher import _safe_float, _get_val
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

_BATCH = 20
_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={range}&interval=1d"


def _make_session():
    return CffiSession(impersonate="chrome120")


def _fetch_prices_direct(ticker: str, session: CffiSession, period: str = "10y") -> list[tuple]:
    """Fetch prices via Yahoo chart API directly — no cookie/crumb needed."""
    try:
        url = _CHART_URL.format(ticker=ticker, range=period)
        r = session.get(url, timeout=20)
        if r.status_code != 200:
            logger.warning(f"  Chart API {r.status_code} for {ticker}")
            return []
        data = r.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return []
        result = result[0]
        timestamps = result.get("timestamp", [])
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])

        rows = []
        for j, ts in enumerate(timestamps):
            c = closes[j] if j < len(closes) else None
            if c is None:
                continue
            rows.append((
                ticker,
                datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d"),
                round(opens[j], 2) if opens[j] is not None else None,
                round(highs[j], 2) if highs[j] is not None else None,
                round(lows[j], 2) if lows[j] is not None else None,
                round(c, 2),
                int(volumes[j]) if volumes[j] is not None else 0,
            ))
        return rows
    except Exception as e:
        logger.warning(f"  Failed prices for {ticker}: {e}")
        return []


def _fetch_all_financials(ticker: str, session: CffiSession):
    """Fetch all financial data for a ticker in one go (reuses yf.Ticker object)."""
    try:
        t = yf.Ticker(ticker, session=session)

        # Annual income statement
        annual = []
        inc = t.income_stmt
        if inc is not None and not inc.empty:
            for col in inc.columns:
                revenue = _safe_float(_get_val(inc, col, "Total Revenue"))
                net_income = _safe_float(_get_val(inc, col, "Net Income"))
                eps = _safe_float(_get_val(inc, col, "Basic EPS", "Diluted EPS"))
                operating_income = _safe_float(_get_val(inc, col, "Operating Income"))
                ebitda = _safe_float(_get_val(inc, col, "EBITDA", "Normalized EBITDA"))
                margin = None
                if revenue and net_income and revenue != 0:
                    margin = round(net_income / revenue * 100, 2)
                annual.append((ticker, col.year, revenue, operating_income, ebitda, net_income, eps, margin))

        # Quarterly income statement
        quarterly = []
        qinc = t.quarterly_income_stmt
        if qinc is not None and not qinc.empty:
            for col in qinc.columns:
                period = f"{col.year}-Q{(col.month - 1) // 3 + 1}"
                revenue = _safe_float(_get_val(qinc, col, "Total Revenue"))
                operating_income = _safe_float(_get_val(qinc, col, "Operating Income"))
                ebitda = _safe_float(_get_val(qinc, col, "EBITDA", "Normalized EBITDA"))
                net_income = _safe_float(_get_val(qinc, col, "Net Income"))
                eps = _safe_float(_get_val(qinc, col, "Basic EPS", "Diluted EPS"))
                margin = None
                if revenue and net_income and revenue != 0:
                    margin = round(net_income / revenue * 100, 2)
                quarterly.append((ticker, period, revenue, operating_income, ebitda, net_income, eps, margin))

        # Balance sheet
        balance = []
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            for col in bs.columns:
                total_assets = _safe_float(_get_val(bs, col, "Total Assets"))
                total_debt = _safe_float(_get_val(bs, col, "Total Debt"))
                cash = _safe_float(_get_val(bs, col, "Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"))
                net_debt = None
                if total_debt is not None and cash is not None:
                    net_debt = total_debt - cash
                total_equity = _safe_float(_get_val(bs, col, "Stockholders Equity", "Total Equity Gross Minority Interest"))
                intangible = _safe_float(_get_val(bs, col, "Goodwill And Other Intangible Assets", "Intangible Assets"))
                balance.append((ticker, col.year, total_assets, total_debt, _safe_float(net_debt), cash, total_equity, intangible))

        # Cash flow
        cashflows = []
        cf = t.cashflow
        if cf is not None and not cf.empty:
            for col in cf.columns:
                ocf = _safe_float(_get_val(cf, col, "Operating Cash Flow"))
                capex = _safe_float(_get_val(cf, col, "Capital Expenditure"))
                fcf = None
                if ocf is not None and capex is not None:
                    fcf = ocf + capex
                cashflows.append((ticker, col.year, ocf, capex, _safe_float(fcf)))

        return annual, quarterly, balance, cashflows
    except Exception as e:
        logger.warning(f"  Failed financials for {ticker}: {e}")
        return [], [], [], []


async def backfill():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)
        tickers = [r["ticker"] for r in await conn.fetch("SELECT ticker FROM stocks")]

        total = len(tickers)
        session = _make_session()

        for i, ticker in enumerate(tickers, 1):
            if (i - 1) % _BATCH == 0 and i > 1:
                try:
                    session.close()
                except Exception:
                    pass
                session = _make_session()
                logger.info("  [rotated session]")

            logger.info(f"[{i}/{total}] Backfilling {ticker}...")

            # Prices
            has_prices = await conn.fetchval(
                "SELECT 1 FROM prices WHERE ticker = $1 LIMIT 1", ticker
            )
            if not has_prices:
                prices = _fetch_prices_direct(ticker, session)
                if prices:
                    await conn.executemany("""
                        INSERT INTO prices (ticker, date, open, high, low, close, volume)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (ticker, date) DO NOTHING
                    """, prices)
                    logger.info(f"  {len(prices)} price rows")
            else:
                logger.info(f"  prices exist, skipping")

            # All financials in one yf.Ticker call
            annual, quarterly, balance, cashflows = _fetch_all_financials(ticker, session)

            if annual:
                await conn.executemany("""
                    INSERT INTO financials_annual (ticker, year, revenue, operating_income, ebitda, net_income, eps, profit_margin)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (ticker, year) DO UPDATE SET
                        revenue=EXCLUDED.revenue, operating_income=EXCLUDED.operating_income,
                        ebitda=EXCLUDED.ebitda, net_income=EXCLUDED.net_income,
                        eps=EXCLUDED.eps, profit_margin=EXCLUDED.profit_margin
                """, annual)
                logger.info(f"  {len(annual)} annual rows")

            if quarterly:
                await conn.executemany("""
                    INSERT INTO financials_quarterly (ticker, period, revenue, operating_income, ebitda, net_income, eps, profit_margin)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (ticker, period) DO UPDATE SET
                        revenue=EXCLUDED.revenue, operating_income=EXCLUDED.operating_income,
                        ebitda=EXCLUDED.ebitda, net_income=EXCLUDED.net_income,
                        eps=EXCLUDED.eps, profit_margin=EXCLUDED.profit_margin
                """, quarterly)
                logger.info(f"  {len(quarterly)} quarterly rows")

            if balance:
                await conn.executemany("""
                    INSERT INTO balance_sheet (ticker, year, total_assets, total_debt, net_debt, cash, total_equity, intangible_assets)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (ticker, year) DO UPDATE SET
                        total_assets=EXCLUDED.total_assets, total_debt=EXCLUDED.total_debt,
                        net_debt=EXCLUDED.net_debt, cash=EXCLUDED.cash,
                        total_equity=EXCLUDED.total_equity, intangible_assets=EXCLUDED.intangible_assets
                """, balance)
                logger.info(f"  {len(balance)} balance sheet rows")

            if cashflows:
                await conn.executemany("""
                    INSERT INTO cashflow (ticker, year, operating_cf, capex, free_cf)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (ticker, year) DO UPDATE SET
                        operating_cf=EXCLUDED.operating_cf, capex=EXCLUDED.capex, free_cf=EXCLUDED.free_cf
                """, cashflows)
                logger.info(f"  {len(cashflows)} cashflow rows")

            time.sleep(1)

        logger.info("Backfill complete.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(backfill())
