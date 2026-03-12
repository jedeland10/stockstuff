from fastapi import APIRouter, Depends, Query
from typing import Optional
import aiosqlite
from app.database import get_db
from app.models import ScreenerResponse, StockRow

router = APIRouter(prefix="/api")


@router.get("/screener", response_model=ScreenerResponse)
async def get_screener(
    country: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    sort_by: str = Query("market_cap"),
    sort_dir: str = Query("desc"),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: aiosqlite.Connection = Depends(get_db),
):
    allowed_sort = {
        "ticker", "name", "country", "sector", "price", "change_pct",
        "pe", "pb", "ps", "ev_ebitda", "div_yield", "roe", "margin", "market_cap",
        "perf_1y", "report_quarter", "industry"
    }
    if sort_by not in allowed_sort:
        sort_by = "market_cap"
    direction = "ASC" if sort_dir.lower() == "asc" else "DESC"

    where = []
    params = []

    if country:
        where.append("s.country = ?")
        params.append(country)
    if sector:
        where.append("s.sector = ?")
        params.append(sector)
    if search:
        where.append("(s.ticker LIKE ? OR s.name LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    # Count total
    count_sql = f"SELECT COUNT(*) FROM stocks s LEFT JOIN fundamentals f ON s.ticker = f.ticker {where_clause}"
    cursor = await db.execute(count_sql, params)
    row = await cursor.fetchone()
    total = row[0]

    # Determine which table has the sort column
    fund_cols = {"price", "change_pct", "pe", "pb", "ps", "ev_ebitda", "div_yield", "roe", "margin", "perf_1y", "report_quarter"}
    sort_prefix = "f" if sort_by in fund_cols else "s"

    sql = f"""
        SELECT s.ticker, s.name, s.country, s.sector, s.market_cap,
               f.price, f.change_pct, f.pe, f.pb, f.ps, f.ev_ebitda,
               f.div_yield, f.roe, f.margin, f.perf_1y, f.report_quarter,
               s.industry
        FROM stocks s
        LEFT JOIN fundamentals f ON s.ticker = f.ticker
        {where_clause}
        ORDER BY {sort_prefix}.{sort_by} {direction} NULLS LAST
        LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])
    cursor = await db.execute(sql, params)
    rows = await cursor.fetchall()

    stocks = []
    for r in rows:
        stocks.append(StockRow(
            ticker=r[0], name=r[1], country=r[2], sector=r[3],
            market_cap=r[4], price=r[5], change_pct=r[6],
            pe=r[7], pb=r[8], ps=r[9], ev_ebitda=r[10],
            div_yield=r[11], roe=r[12], margin=r[13],
            perf_1y=r[14], report_quarter=r[15], industry=r[16],
        ))

    return ScreenerResponse(stocks=stocks, total=total)


@router.get("/meta/sectors")
async def get_sectors(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "SELECT DISTINCT sector FROM stocks WHERE sector != '' ORDER BY sector"
    )
    rows = await cursor.fetchall()
    return [r[0] for r in rows]


@router.get("/meta/countries")
async def get_countries(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "SELECT DISTINCT country FROM stocks WHERE country != '' ORDER BY country"
    )
    rows = await cursor.fetchall()
    return [r[0] for r in rows]
