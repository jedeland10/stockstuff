"""Scheduled data refresh using APScheduler."""
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import UPDATE_INTERVAL_HOURS, DB_PATH
from app.services.fetcher import fetch_stock_info
import aiosqlite

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def refresh_fundamentals():
    """Update fundamentals for all stocks."""
    logger.info("Starting scheduled fundamentals refresh...")
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT ticker FROM stocks")
        tickers = [row["ticker"] async for row in cursor]

        updated = 0
        for ticker in tickers:
            info = fetch_stock_info(ticker)
            if info is None:
                continue
            await db.execute("""
                UPDATE fundamentals SET
                    price=?, change_pct=?, pe=?, pb=?, ps=?, ev_ebitda=?,
                    div_yield=?, roe=?, margin=?, eps=?, revenue=?,
                    revenue_growth=?, updated_at=datetime('now')
                WHERE ticker=?
            """, (
                info["price"], info["change_pct"], info["pe"], info["pb"],
                info["ps"], info["ev_ebitda"], info["div_yield"], info["roe"],
                info["margin"], info["eps"], info["revenue"],
                info["revenue_growth"], ticker,
            ))
            updated += 1

        await db.commit()
        logger.info(f"Refreshed {updated}/{len(tickers)} stocks.")


def start_scheduler():
    scheduler.add_job(
        lambda: asyncio.create_task(refresh_fundamentals()),
        "interval",
        hours=UPDATE_INTERVAL_HOURS,
        id="refresh_fundamentals",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started — refresh every {UPDATE_INTERVAL_HOURS}h")
