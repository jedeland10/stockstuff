#!/usr/bin/env python3
"""Import discovered tickers into the database (seed + initial fundamentals)."""
import asyncio
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

COUNTRY_MAP = {
    ".ST": "SE",
    ".HE": "FI",
    ".CO": "DK",
    ".OL": "NO",
}


async def import_tickers():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)

        # Get discovered tickers not yet in stocks table
        new_tickers = [
            r["ticker"]
            for r in await conn.fetch("""
                SELECT f.ticker FROM _discovery_found f
                LEFT JOIN stocks s ON f.ticker = s.ticker
                WHERE s.ticker IS NULL
            """)
        ]
        existing = await conn.fetchval("SELECT COUNT(*) FROM stocks")
        logger.info(f"{len(new_tickers)} new tickers to import ({existing} already exist)")

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
                 perf_1y, report_quarter, shares_outstanding, enterprise_value,
                 book_value_per_share, updated_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,NOW()::text)
                ON CONFLICT (ticker) DO UPDATE SET
                    price=EXCLUDED.price, change_pct=EXCLUDED.change_pct,
                    pe=EXCLUDED.pe, pb=EXCLUDED.pb, ps=EXCLUDED.ps, ev_ebitda=EXCLUDED.ev_ebitda,
                    div_yield=EXCLUDED.div_yield, roe=EXCLUDED.roe, margin=EXCLUDED.margin,
                    eps=EXCLUDED.eps, revenue=EXCLUDED.revenue, revenue_growth=EXCLUDED.revenue_growth,
                    perf_1y=EXCLUDED.perf_1y, report_quarter=EXCLUDED.report_quarter,
                    shares_outstanding=EXCLUDED.shares_outstanding, enterprise_value=EXCLUDED.enterprise_value,
                    book_value_per_share=EXCLUDED.book_value_per_share, updated_at=EXCLUDED.updated_at""",
                ticker, info["price"], info["change_pct"],
                info["pe"], info["pb"], info["ps"], info["ev_ebitda"],
                info["div_yield"], info["roe"], info["margin"],
                info["eps"], info["revenue"], info["revenue_growth"],
                info["perf_1y"], info["report_quarter"],
                info["shares_outstanding"], info["enterprise_value"],
                info["book_value_per_share"],
            )
            success += 1
            time.sleep(1.5)

        logger.info(f"Imported {success}/{len(new_tickers)} new stocks")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(import_tickers())
