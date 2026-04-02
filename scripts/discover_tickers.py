#!/usr/bin/env python3
"""Discover all valid Nordic tickers using multiple strategies:

1. Yahoo Finance search/autocomplete API — queries by prefix to find tickers
   on Nordic exchanges. Fast and catches long tickers with digits/hyphens.
2. Brute-force chart API — scans 2-4 letter combos as a fallback to catch
   anything the search API missed.

Progress is saved in PostgreSQL so it survives restarts.
"""
import asyncio
import json
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
SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search?q={}&quotesCount=50&newsCount=0&enableFuzzyQuery=false&quotesQueryId=tss_match_phrase_query"

EXCHANGES = {
    ".OL": "NO",
    ".ST": "SE",
    ".HE": "FI",
    ".CO": "DK",
}

# Yahoo exchange codes that map to our suffixes
YAHOO_EXCHANGE_MAP = {
    "OSL": ".OL",   # Oslo
    "STO": ".ST",   # Stockholm
    "HEL": ".HE",   # Helsinki
    "CPH": ".CO",   # Copenhagen
}


def check_ticker(session: Session, ticker: str) -> dict | None:
    """Verify a ticker exists via the chart API."""
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


def search_tickers(session: Session, query: str) -> list[dict]:
    """Use Yahoo Finance search API to find tickers matching a query."""
    try:
        r = session.get(SEARCH_URL.format(query), timeout=8)
        if r.status_code == 200:
            data = r.json()
            results = []
            for quote in data.get("quotes", []):
                exchange = quote.get("exchange", "")
                suffix = YAHOO_EXCHANGE_MAP.get(exchange)
                if suffix and quote.get("quoteType") == "EQUITY":
                    symbol = quote.get("symbol", "")
                    if symbol.endswith(suffix):
                        results.append({
                            "ticker": symbol,
                            "name": quote.get("shortname", "") or quote.get("longname", ""),
                            "exchange": exchange,
                            "currency": "",
                        })
            return results
    except Exception as e:
        logger.debug(f"Search error for '{query}': {e}")
    return []


def generate_search_prefixes() -> list[str]:
    """Generate search prefixes to query the Yahoo search API.

    We search with 1-letter and 2-letter prefixes. Yahoo returns up to 50
    results per query, so short prefixes cast a wide net and catch long
    tickers that brute-force would miss.
    """
    letters = string.ascii_uppercase
    digits = string.digits
    chars = letters + digits
    prefixes = []

    # Single letter
    for a in letters:
        prefixes.append(a)

    # Two-letter prefixes (AA, AB, ..., AZ, A0, ..., A9, BA, ...)
    for a in letters:
        for b in chars:
            prefixes.append(f"{a}{b}")

    return prefixes


def generate_brute_candidates(suffix: str) -> list[str]:
    """Generate brute-force candidates for 4-letter tickers and
    variants not covered by the search API."""
    letters = string.ascii_uppercase
    digits = string.digits
    candidates = []

    # 4-letter pure alpha (MOWI, EQNR, AKER, etc.)
    for a in letters:
        for b in letters:
            for c in letters:
                for d in letters:
                    candidates.append(f"{a}{b}{c}{d}{suffix}")

    # 4-letter with -A, -B, -R variants (all exchanges)
    for a in letters:
        for b in letters:
            for c in letters:
                for d in letters:
                    for var in ["-A", "-B", "-R"]:
                        candidates.append(f"{a}{b}{c}{d}{var}{suffix}")

    # 3-letter with -A, -B, -R for exchanges that didn't have them before (.OL, .HE)
    if suffix in [".OL", ".HE"]:
        for a in letters:
            for b in letters:
                for var in ["-A", "-B", "-R"]:
                    candidates.append(f"{a}{b}{var}{suffix}")
                for c in letters:
                    for var in ["-A", "-B", "-R"]:
                        candidates.append(f"{a}{b}{c}{var}{suffix}")

    # Finnish patterns with digits: XXX1V, XXXX1V (e.g., WRT1V, HUH1V, OUT1V)
    if suffix == ".HE":
        for a in letters:
            for b in letters:
                for c in letters:
                    for d in digits:
                        for e in letters:
                            candidates.append(f"{a}{b}{c}{d}{e}{suffix}")
                    for d in letters:
                        for e in digits:
                            for f in letters:
                                candidates.append(f"{a}{b}{c}{d}{e}{f}{suffix}")

    # -SDB variant for .ST (e.g., TIGO-SDB.ST)
    if suffix == ".ST":
        for a in letters:
            for b in letters:
                for c in letters:
                    candidates.append(f"{a}{b}{c}-SDB{suffix}")
                    for d in letters:
                        candidates.append(f"{a}{b}{c}{d}-SDB{suffix}")

    return candidates


async def save_batch(conn, batch_checked, batch_found):
    """Save progress to database."""
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


async def phase_search(conn, checked: set, found_tickers: set):
    """Phase 1: Use Yahoo search API to discover tickers by prefix."""
    logger.info("=" * 60)
    logger.info("PHASE 1: Yahoo Finance search API")
    logger.info("=" * 60)

    prefixes = generate_search_prefixes()

    # Filter out already-searched prefixes
    searched = set()
    try:
        rows = await conn.fetch("SELECT prefix FROM _discovery_search_done")
        searched = set(r["prefix"] for r in rows)
    except Exception:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _discovery_search_done (
                prefix TEXT PRIMARY KEY
            )
        """)

    prefixes = [p for p in prefixes if p not in searched]
    logger.info(f"{len(prefixes)} prefixes to search ({len(searched)} already done)")

    session = Session(impersonate="chrome120")
    request_count = 0
    new_found = 0
    batch_found = []
    batch_prefixes = []

    for i, prefix in enumerate(prefixes, 1):
        results = search_tickers(session, prefix)

        for r in results:
            ticker = r["ticker"]
            if ticker not in found_tickers:
                # Verify via chart API to confirm it's real
                verified = check_ticker(session, ticker)
                request_count += 1
                if verified:
                    batch_found.append((ticker, verified["name"], verified["exchange"], verified["currency"]))
                    found_tickers.add(ticker)
                    checked.add(ticker)
                    new_found += 1
                    logger.info(f"  FOUND: {ticker} ({verified['name']})")

                # Rotate session periodically
                if request_count % 100 == 0:
                    session = Session(impersonate="chrome120")

        batch_prefixes.append((prefix,))
        request_count += 1

        # Rotate session every 200 requests
        if request_count % 200 == 0:
            session = Session(impersonate="chrome120")

        # Save progress every 50 prefixes
        if i % 50 == 0 or i == len(prefixes):
            await save_batch(conn, [], batch_found)
            if batch_prefixes:
                await conn.executemany(
                    "INSERT INTO _discovery_search_done (prefix) VALUES ($1) ON CONFLICT DO NOTHING",
                    batch_prefixes,
                )
            batch_found = []
            batch_prefixes = []
            total = await conn.fetchval("SELECT COUNT(*) FROM _discovery_found")
            logger.info(f"  Search progress: {i}/{len(prefixes)} prefixes, {total} total found, {new_found} new")

        # Small delay to avoid rate limiting
        time.sleep(0.3)

    # Final save
    await save_batch(conn, [], batch_found)
    if batch_prefixes:
        await conn.executemany(
            "INSERT INTO _discovery_search_done (prefix) VALUES ($1) ON CONFLICT DO NOTHING",
            batch_prefixes,
        )

    logger.info(f"Phase 1 complete: {new_found} new tickers found via search")
    return new_found


async def phase_brute(conn, checked: set):
    """Phase 2: Brute-force scan for remaining candidates."""
    logger.info("=" * 60)
    logger.info("PHASE 2: Brute-force verification (4-letter + variants)")
    logger.info("=" * 60)

    session = Session(impersonate="chrome120")
    request_count = 0
    new_found = 0
    batch_checked = []
    batch_found = []

    for suffix, country in EXCHANGES.items():
        candidates = generate_brute_candidates(suffix)
        candidates = [c for c in candidates if c not in checked]
        logger.info(f"{suffix} ({country}): {len(candidates)} new candidates to check")

        for ticker in candidates:
            result = check_ticker(session, ticker)

            batch_checked.append((ticker,))
            if result:
                batch_found.append((ticker, result["name"], result["exchange"], result["currency"]))
                new_found += 1
                logger.info(f"  FOUND: {ticker} ({result['name']})")

            request_count += 1

            if request_count % 500 == 0:
                session = Session(impersonate="chrome120")

            if request_count % 500 == 0:
                await save_batch(conn, batch_checked, batch_found)
                batch_checked = []
                batch_found = []
                total_found = await conn.fetchval("SELECT COUNT(*) FROM _discovery_found")
                logger.info(f"  Brute progress: {request_count} checked, {total_found} total found, {new_found} new")

    await save_batch(conn, batch_checked, batch_found)

    logger.info(f"Phase 2 complete: {new_found} new tickers found via brute-force")
    return new_found


async def discover():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)

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
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _discovery_search_done (
                prefix TEXT PRIMARY KEY
            )
        """)

        checked = set(r["ticker"] for r in await conn.fetch("SELECT ticker FROM _discovery_checked"))
        found_tickers = set(r["ticker"] for r in await conn.fetch("SELECT ticker FROM _discovery_found"))
        logger.info(f"Resuming: {len(found_tickers)} found, {len(checked)} already checked")

        # Phase 1: Search API (fast, catches long tickers)
        search_found = await phase_search(conn, checked, found_tickers)

        # Phase 2: Brute-force (4-letter + variants, catches anything search missed)
        brute_found = await phase_brute(conn, checked)

        # Summary
        total_found = await conn.fetchval("SELECT COUNT(*) FROM _discovery_found")
        logger.info("")
        logger.info("=" * 60)
        logger.info("DISCOVERY COMPLETE")
        logger.info("=" * 60)
        logger.info(f"  Total valid tickers: {total_found}")
        logger.info(f"  New from search API: {search_found}")
        logger.info(f"  New from brute-force: {brute_found}")
        for suffix, country in EXCHANGES.items():
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM _discovery_found WHERE ticker LIKE $1", f"%{suffix}"
            )
            logger.info(f"  {country} ({suffix}): {count}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(discover())
