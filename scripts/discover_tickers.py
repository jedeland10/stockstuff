#!/usr/bin/env python3
"""Discover all valid Nordic tickers by scanning Yahoo Finance.
Runs sequentially to avoid rate-limiting. Takes ~1-2 hours for a full scan.
Progress is saved in PostgreSQL so it survives container restarts.
"""
import asyncio
import string
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncpg
from curl_cffi.requests import Session
from app.config import DATABASE_URL
from app.database import init_db
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1d&interval=1d"

EXCHANGES = {
    ".OL": "NO",
    ".ST": "SE",
    ".HE": "FI",
    ".CO": "DK",
}


def check_ticker(session: Session, ticker: str) -> dict | None:
    try:
        r = session.get(CHART_URL.format(ticker), timeout=5)
        if r.status_code == 200:
            data = r.json()
            result = data.get("chart", {}).get("result")
            if result:
                meta = result[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                if price and price > 0:
                    return {
                        "ticker": ticker,
                        "name": meta.get("shortName", ""),
                        "exchange": meta.get("exchangeName", ""),
                        "currency": meta.get("currency", ""),
                    }
    except Exception:
        pass
    return None


def generate_candidates(suffix: str) -> list[str]:
    letters = string.ascii_uppercase
    candidates = []

    # 2-letter
    for a in letters:
        for b in letters:
            candidates.append(f"{a}{b}{suffix}")

    # 3-letter
    for a in letters:
        for b in letters:
            for c in letters:
                candidates.append(f"{a}{b}{c}{suffix}")

    # -A and -B variants (common in SE/DK)
    if suffix in [".ST", ".CO"]:
        extras = []
        for a in letters:
            for b in letters:
                for var in ["-A", "-B"]:
                    extras.append(f"{a}{b}{var}{suffix}")
                for c in letters:
                    for var in ["-A", "-B"]:
                        extras.append(f"{a}{b}{c}{var}{suffix}")
        candidates.extend(extras)

    return candidates


async def discover():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)

        # Create discovery tracking table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _discovery_checked (
                ticker TEXT PRIMARY KEY
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _discovery_found (
                ticker TEXT PRIMARY KEY,
                name TEXT,
                exchange TEXT,
                currency TEXT
            )
        """)

        # Load already-checked tickers
        checked = set(r["ticker"] for r in await conn.fetch("SELECT ticker FROM _discovery_checked"))
        found_count = await conn.fetchval("SELECT COUNT(*) FROM _discovery_found")
        logger.info(f"Resuming: {found_count} found, {len(checked)} already checked")

        session = Session(impersonate="chrome120")
        request_count = 0
        new_found = 0
        batch_checked = []
        batch_found = []

        for suffix, country in EXCHANGES.items():
            candidates = generate_candidates(suffix)
            # Filter out already checked
            candidates = [c for c in candidates if c not in checked]
            logger.info(f"{suffix} ({country}): {len(candidates)} candidates to check")

            for ticker in candidates:
                result = check_ticker(session, ticker)

                batch_checked.append((ticker,))
                if result:
                    batch_found.append((ticker, result["name"], result["exchange"], result["currency"]))
                    new_found += 1
                    logger.info(f"  FOUND: {ticker} ({result['name']})")

                request_count += 1

                # Rotate session every 500 requests
                if request_count % 500 == 0:
                    session = Session(impersonate="chrome120")

                # Save progress every 500 checks
                if request_count % 500 == 0:
                    await conn.executemany(
                        "INSERT INTO _discovery_checked (ticker) VALUES ($1) ON CONFLICT DO NOTHING",
                        batch_checked,
                    )
                    if batch_found:
                        await conn.executemany(
                            "INSERT INTO _discovery_found (ticker, name, exchange, currency) VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING",
                            batch_found,
                        )
                    batch_checked = []
                    batch_found = []
                    total_found = await conn.fetchval("SELECT COUNT(*) FROM _discovery_found")
                    logger.info(f"  Progress: {request_count} checked, {total_found} total found, {new_found} new this run")

        # Final save
        if batch_checked:
            await conn.executemany(
                "INSERT INTO _discovery_checked (ticker) VALUES ($1) ON CONFLICT DO NOTHING",
                batch_checked,
            )
        if batch_found:
            await conn.executemany(
                "INSERT INTO _discovery_found (ticker, name, exchange, currency) VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING",
                batch_found,
            )

        total_found = await conn.fetchval("SELECT COUNT(*) FROM _discovery_found")
        logger.info(f"\nDiscovery complete:")
        logger.info(f"  Total valid tickers: {total_found}")
        logger.info(f"  New this run: {new_found}")
        for suffix, country in EXCHANGES.items():
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM _discovery_found WHERE ticker LIKE $1", f"%{suffix}"
            )
            logger.info(f"  {country} ({suffix}): {count}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(discover())
