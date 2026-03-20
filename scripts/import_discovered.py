#!/usr/bin/env python3
"""Import discovered tickers into the database (seed + initial fundamentals)."""
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncpg
from app.config import DATABASE_URL
from app.database import init_db
from app.services.fetcher import fetch_stock_info
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

DISCOVERED = Path(__file__).resolve().parent.parent / "data" / "discovered_tickers.json"

COUNTRY_MAP = {
    ".ST": "SE",
    ".HE": "FI",
    ".CO": "DK",
    ".OL": "NO",
}


async def import_tickers():
    if not DISCOVERED.exists():
        logger.error(f"No discovered tickers file at {DISCOVERED}. Run discover_tickers.py first.")
        return

    with open(DISCOVERED) as f:
        data = json.load(f)

    tickers = list(data.get("tickers", {}).keys())
    logger.info(f"Found {len(tickers)} discovered tickers")

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)

        # Check which ones are already in the database
        existing = set(
            r["ticker"]
            for r in await conn.fetch("SELECT ticker FROM stocks")
        )
        new_tickers = [t for t in tickers if t not in existing]
        logger.info(f"{len(new_tickers)} new tickers to import ({len(existing)} already exist)")

        success = 0
        for i, ticker in enumerate(new_tickers, 1):
            logger.info(f"[{i}/{len(new_tickers)}] Fetching {ticker}...")
            info = fetch_stock_info(ticker)
            if info is None:
                logger.warning(f"  Skipped {ticker}")
                continue

            country = ""
            for suffix, code in COUNTRY_MAP.items():
                if ticker.endswith(suffix):
                    country = code
                    break

            await conn.execute(
                """INSERT INTO stocks (ticker, name, exchange, country, sector, industry, market_cap, description)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (ticker) DO UPDATE SET
                    name=EXCLUDED.name, exchange=EXCLUDED.exchange, country=EXCLUDED.country,
                    sector=EXCLUDED.sector, industry=EXCLUDED.industry,
                    market_cap=EXCLUDED.market_cap, description=EXCLUDED.description""",
                ticker, info["name"], info["exchange"], country,
                info["sector"], info["industry"], info["market_cap"],
                info["description"],
            )

            await conn.execute(
                """INSERT INTO fundamentals
                (ticker, price, change_pct, pe, pb, ps, ev_ebitda,
                 div_yield, roe, margin, eps, revenue, revenue_growth,
                 perf_1y, report_quarter, updated_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,NOW()::text)
                ON CONFLICT (ticker) DO UPDATE SET
                    price=EXCLUDED.price, change_pct=EXCLUDED.change_pct,
                    pe=EXCLUDED.pe, pb=EXCLUDED.pb, ps=EXCLUDED.ps, ev_ebitda=EXCLUDED.ev_ebitda,
                    div_yield=EXCLUDED.div_yield, roe=EXCLUDED.roe, margin=EXCLUDED.margin,
                    eps=EXCLUDED.eps, revenue=EXCLUDED.revenue, revenue_growth=EXCLUDED.revenue_growth,
                    perf_1y=EXCLUDED.perf_1y, report_quarter=EXCLUDED.report_quarter,
                    updated_at=EXCLUDED.updated_at""",
                ticker, info["price"], info["change_pct"],
                info["pe"], info["pb"], info["ps"], info["ev_ebitda"],
                info["div_yield"], info["roe"], info["margin"],
                info["eps"], info["revenue"], info["revenue_growth"],
                info["perf_1y"], info["report_quarter"],
            )
            success += 1
            time.sleep(1.5)

        logger.info(f"Imported {success}/{len(new_tickers)} new stocks")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(import_tickers())
