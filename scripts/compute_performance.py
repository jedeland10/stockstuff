#!/usr/bin/env python3
"""Compute 1W, 1M, 1Y performance from price history and update fundamentals."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncpg
from app.config import DATABASE_URL
from app.database import init_db
from app.services.updater import compute_performance
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)
        await compute_performance(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
