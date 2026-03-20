import asyncpg
from app.config import DATABASE_URL

pool: asyncpg.Pool | None = None


async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    await init_db()


async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None


def get_pool() -> asyncpg.Pool:
    assert pool is not None, "Database pool not initialized"
    return pool


async def init_db(conn: asyncpg.Connection | None = None):
    """Create tables/indexes. Pass a connection directly, or uses the pool."""
    if conn is not None:
        await _run_schema(conn)
        return
    assert pool is not None
    async with pool.acquire() as c:
        await _run_schema(c)


async def _run_schema(conn: asyncpg.Connection):
    await conn.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                ticker TEXT PRIMARY KEY,
                name TEXT,
                exchange TEXT,
                country TEXT,
                sector TEXT,
                industry TEXT,
                market_cap DOUBLE PRECISION,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS prices (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume BIGINT,
                PRIMARY KEY (ticker, date)
            );

            CREATE TABLE IF NOT EXISTS fundamentals (
                ticker TEXT PRIMARY KEY,
                price DOUBLE PRECISION,
                change_pct DOUBLE PRECISION,
                pe DOUBLE PRECISION,
                pb DOUBLE PRECISION,
                ps DOUBLE PRECISION,
                ev_ebitda DOUBLE PRECISION,
                div_yield DOUBLE PRECISION,
                roe DOUBLE PRECISION,
                margin DOUBLE PRECISION,
                eps DOUBLE PRECISION,
                revenue DOUBLE PRECISION,
                revenue_growth DOUBLE PRECISION,
                perf_1y DOUBLE PRECISION,
                report_quarter TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS financials_annual (
                ticker TEXT NOT NULL,
                year INTEGER NOT NULL,
                revenue DOUBLE PRECISION,
                net_income DOUBLE PRECISION,
                eps DOUBLE PRECISION,
                profit_margin DOUBLE PRECISION,
                PRIMARY KEY (ticker, year)
            );
    """)

    # Indexes — CREATE INDEX IF NOT EXISTS must be separate statements in PG
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_prices_ticker_date ON prices(ticker, date DESC)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_stocks_country ON stocks(country)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_financials_ticker ON financials_annual(ticker, year DESC)")
