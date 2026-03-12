import aiosqlite
from app.config import DB_PATH, DATA_DIR


async def get_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(DB_PATH))
    await db.execute("PRAGMA journal_mode=WAL")
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        # WAL mode for better concurrent read/write
        await db.execute("PRAGMA journal_mode=WAL")

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS stocks (
                ticker TEXT PRIMARY KEY,
                name TEXT,
                exchange TEXT,
                country TEXT,
                sector TEXT,
                industry TEXT,
                market_cap REAL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS prices (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                PRIMARY KEY (ticker, date)
            );

            CREATE TABLE IF NOT EXISTS fundamentals (
                ticker TEXT PRIMARY KEY,
                price REAL,
                change_pct REAL,
                pe REAL,
                pb REAL,
                ps REAL,
                ev_ebitda REAL,
                div_yield REAL,
                roe REAL,
                margin REAL,
                eps REAL,
                revenue REAL,
                revenue_growth REAL,
                perf_1y REAL,
                report_quarter TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS financials_annual (
                ticker TEXT NOT NULL,
                year INTEGER NOT NULL,
                revenue REAL,
                net_income REAL,
                eps REAL,
                profit_margin REAL,
                PRIMARY KEY (ticker, year)
            );

            -- Indexes for chart/screener queries
            CREATE INDEX IF NOT EXISTS idx_prices_ticker_date ON prices(ticker, date DESC);
            CREATE INDEX IF NOT EXISTS idx_stocks_country ON stocks(country);
            CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);
            CREATE INDEX IF NOT EXISTS idx_financials_ticker ON financials_annual(ticker, year DESC);
        """)
        await db.commit()
