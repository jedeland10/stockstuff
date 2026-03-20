#!/usr/bin/env python3
"""Backfill price history and annual financials for all seeded stocks."""
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
from app.services.fetcher import _safe_float
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
                continue  # skip days with no close price
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


def _fetch_financials(ticker: str, session: CffiSession) -> list[tuple]:
    """Fetch annual financials via yfinance (lightweight, rarely rate-limited)."""
    try:
        t = yf.Ticker(ticker, session=session)
        inc = t.income_stmt
        if inc is None or inc.empty:
            return []
        rows = []
        for col in inc.columns:
            year = col.year
            revenue = _safe_float(inc.loc["Total Revenue", col]) if "Total Revenue" in inc.index else None
            net_income = _safe_float(inc.loc["Net Income", col]) if "Net Income" in inc.index else None
            eps = None
            for name in ("Basic EPS", "Diluted EPS"):
                if name in inc.index:
                    eps = _safe_float(inc.loc[name, col])
                    if eps is not None:
                        break
            margin = None
            if revenue and net_income and revenue != 0:
                margin = round(net_income / revenue * 100, 2)
            rows.append((ticker, year, revenue, net_income, eps, margin))
        return rows
    except Exception as e:
        logger.warning(f"  Failed financials for {ticker}: {e}")
        return []


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
                logger.info(f"  prices already exist, skipping")

            fins = _fetch_financials(ticker, session)
            if fins:
                await conn.executemany("""
                    INSERT INTO financials_annual (ticker, year, revenue, net_income, eps, profit_margin)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (ticker, year) DO UPDATE SET
                        revenue=EXCLUDED.revenue, net_income=EXCLUDED.net_income,
                        eps=EXCLUDED.eps, profit_margin=EXCLUDED.profit_margin
                """, fins)
                logger.info(f"  {len(fins)} annual rows")

            time.sleep(1)

        logger.info("Backfill complete.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(backfill())
