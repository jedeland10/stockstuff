"""Scheduled data refresh using APScheduler."""
import asyncio
import logging
from datetime import datetime, timedelta, date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import UPDATE_INTERVAL_HOURS
from app.services.fetcher import fetch_stock_info, fetch_price_history
from app.database import get_pool

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def compute_performance(conn=None):
    """Compute 1W, 1M, 1Y performance from price history and update fundamentals.

    For each ticker, finds the closing price on (or nearest before) the reference
    dates and calculates percentage change vs the most recent close.
    """
    should_release = conn is None
    if conn is None:
        pool = get_pool()
        conn = await pool.acquire()

    try:
        today = date.today()
        cutoff_1w = (today - timedelta(days=7)).isoformat()
        cutoff_1m = (today - timedelta(days=30)).isoformat()
        cutoff_1y = (today - timedelta(days=365)).isoformat()

        rows = await conn.fetch("""
            WITH latest AS (
                SELECT DISTINCT ON (ticker) ticker, close AS latest_close, date AS latest_date
                FROM prices
                ORDER BY ticker, date DESC
            ),
            ref_1w AS (
                SELECT DISTINCT ON (ticker) ticker, close AS close_1w
                FROM prices
                WHERE date <= $1
                ORDER BY ticker, date DESC
            ),
            ref_1m AS (
                SELECT DISTINCT ON (ticker) ticker, close AS close_1m
                FROM prices
                WHERE date <= $2
                ORDER BY ticker, date DESC
            ),
            ref_1y AS (
                SELECT DISTINCT ON (ticker) ticker, close AS close_1y
                FROM prices
                WHERE date <= $3
                ORDER BY ticker, date DESC
            )
            SELECT
                l.ticker,
                CASE WHEN w.close_1w IS NOT NULL AND w.close_1w > 0
                     THEN ROUND(((l.latest_close - w.close_1w) / w.close_1w * 100)::numeric, 2)
                     ELSE NULL END AS perf_1w,
                CASE WHEN m.close_1m IS NOT NULL AND m.close_1m > 0
                     THEN ROUND(((l.latest_close - m.close_1m) / m.close_1m * 100)::numeric, 2)
                     ELSE NULL END AS perf_1m,
                CASE WHEN y.close_1y IS NOT NULL AND y.close_1y > 0
                     THEN ROUND(((l.latest_close - y.close_1y) / y.close_1y * 100)::numeric, 2)
                     ELSE NULL END AS perf_1y
            FROM latest l
            LEFT JOIN ref_1w w ON l.ticker = w.ticker
            LEFT JOIN ref_1m m ON l.ticker = m.ticker
            LEFT JOIN ref_1y y ON l.ticker = y.ticker
        """, cutoff_1w, cutoff_1m, cutoff_1y)

        if rows:
            await conn.executemany("""
                UPDATE fundamentals
                SET perf_1w = $2, perf_1m = $3, perf_1y = $4
                WHERE ticker = $1
            """, [
                (r["ticker"], float(r["perf_1w"]) if r["perf_1w"] is not None else None,
                 float(r["perf_1m"]) if r["perf_1m"] is not None else None,
                 float(r["perf_1y"]) if r["perf_1y"] is not None else None)
                for r in rows
            ])

        logger.info(f"Performance computed for {len(rows)} tickers (1W/1M/1Y)")
    finally:
        if should_release:
            await get_pool().release(conn)


async def refresh_fundamentals():
    """Update fundamentals for all stocks."""
    logger.info("Starting scheduled fundamentals refresh...")
    pool = get_pool()
    async with pool.acquire() as conn:
        tickers = [r["ticker"] for r in await conn.fetch("SELECT ticker FROM stocks")]

        updated = 0
        for ticker in tickers:
            info = fetch_stock_info(ticker)
            if info is None:
                continue
            await conn.execute("""
                UPDATE fundamentals SET
                    price=$1, change_pct=$2, pe=$3, pb=$4, ps=$5, ev_ebitda=$6,
                    div_yield=$7, roe=$8, margin=$9, eps=$10, revenue=$11,
                    revenue_growth=$12, shares_outstanding=$13, enterprise_value=$14,
                    book_value_per_share=$15, updated_at=NOW()::text
                WHERE ticker=$16
            """,
                info["price"], info["change_pct"], info["pe"], info["pb"],
                info["ps"], info["ev_ebitda"], info["div_yield"], info["roe"],
                info["margin"], info["eps"], info["revenue"],
                info["revenue_growth"], info["shares_outstanding"],
                info["enterprise_value"], info["book_value_per_share"], ticker,
            )
            updated += 1

        logger.info(f"Refreshed {updated}/{len(tickers)} stocks.")


async def refresh_prices():
    """Incremental price catch-up — fetch only missing dates for each ticker."""
    logger.info("Starting scheduled price catch-up...")
    pool = get_pool()
    async with pool.acquire() as conn:
        tickers = [r["ticker"] for r in await conn.fetch("SELECT ticker FROM stocks")]

        updated = 0
        for ticker in tickers:
            last_date = await conn.fetchval(
                "SELECT MAX(date) FROM prices WHERE ticker = $1", ticker
            )
            if last_date is None:
                # No price data at all — fetch 2 years
                period = "2y"
            else:
                # Calculate days since last date
                last_dt = datetime.strptime(last_date, "%Y-%m-%d")
                gap = (datetime.now() - last_dt).days
                if gap <= 1:
                    continue  # Already up to date
                elif gap <= 7:
                    period = "5d"
                elif gap <= 35:
                    period = "1mo"
                elif gap <= 100:
                    period = "3mo"
                elif gap <= 370:
                    period = "1y"
                else:
                    period = "2y"

            prices = fetch_price_history(ticker, period=period)
            if not prices:
                continue

            # Filter to only new dates
            if last_date:
                prices = [p for p in prices if p["date"] > last_date]

            if not prices:
                continue

            # Bulk upsert
            await conn.executemany("""
                INSERT INTO prices (ticker, date, open, high, low, close, volume)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (ticker, date) DO NOTHING
            """, [
                (p["ticker"], p["date"], p["open"], p["high"], p["low"], p["close"], p["volume"])
                for p in prices
            ])
            updated += 1

        logger.info(f"Price catch-up done — updated {updated}/{len(tickers)} tickers.")

    # Recompute performance metrics from updated price history
    await compute_performance()


def start_scheduler():
    tz = "Europe/Stockholm"
    # Fundamentals: every 3 hours during market-relevant hours (9-21)
    scheduler.add_job(
        refresh_fundamentals,
        "cron",
        hour="9,12,15,18",
        minute=0,
        timezone=tz,
        id="refresh_fundamentals",
        replace_existing=True,
    )
    # Prices: during market hours + after close
    scheduler.add_job(
        refresh_prices,
        "cron",
        hour="9,12,15,18",
        minute=5,
        timezone=tz,
        id="refresh_prices",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — fundamentals + prices at 09/12/15/18 (Europe/Stockholm)")
