"""Scheduled data refresh using APScheduler."""
import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import UPDATE_INTERVAL_HOURS
from app.services.fetcher import fetch_stock_info, fetch_price_history
from app.database import get_pool

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


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
