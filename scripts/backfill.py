#!/usr/bin/env python3
"""Backfill price history and annual financials for all seeded stocks."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db, DB_PATH
from app.services.fetcher import fetch_price_history, fetch_annual_financials
import aiosqlite
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


async def backfill():
    await init_db()
    async with aiosqlite.connect(str(DB_PATH)) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT ticker FROM stocks")
        tickers = [row["ticker"] async for row in cursor]

        total = len(tickers)
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"[{i}/{total}] Backfilling {ticker}...")

            # Prices — 10 years of history
            prices = fetch_price_history(ticker, period="10y")
            if prices:
                await db.executemany("""
                    INSERT OR REPLACE INTO prices (ticker, date, open, high, low, close, volume)
                    VALUES (:ticker, :date, :open, :high, :low, :close, :volume)
                """, prices)
                logger.info(f"  {len(prices)} price rows")

            # Annual financials
            fins = fetch_annual_financials(ticker)
            if fins:
                await db.executemany("""
                    INSERT OR REPLACE INTO financials_annual (ticker, year, revenue, net_income, eps, profit_margin)
                    VALUES (:ticker, :year, :revenue, :net_income, :eps, :profit_margin)
                """, fins)
                logger.info(f"  {len(fins)} annual rows")

            # Commit every 10 tickers
            if i % 10 == 0:
                await db.commit()

        await db.commit()
        logger.info("Backfill complete.")


if __name__ == "__main__":
    asyncio.run(backfill())
