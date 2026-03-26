from fastapi import APIRouter, Query
from typing import Optional
from app.database import get_pool
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
    idx = 1

    if country:
        where.append(f"s.country = ${idx}")
        params.append(country)
        idx += 1
    if sector:
        where.append(f"s.sector = ${idx}")
        params.append(sector)
        idx += 1
    if search:
        where.append(f"(s.ticker ILIKE ${idx} OR s.name ILIKE ${idx + 1})")
        params.extend([f"%{search}%", f"%{search}%"])
        idx += 2

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    pool = get_pool()
    async with pool.acquire() as conn:
        # Count total
        count_sql = f"SELECT COUNT(*) FROM stocks s LEFT JOIN fundamentals f ON s.ticker = f.ticker {where_clause}"
        total = await conn.fetchval(count_sql, *params)

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
            LIMIT ${idx} OFFSET ${idx + 1}
        """
        params.extend([limit, offset])
        rows = await conn.fetch(sql, *params)

    stocks = []
    for r in rows:
        stocks.append(StockRow(
            ticker=r["ticker"], name=r["name"], country=r["country"], sector=r["sector"],
            market_cap=r["market_cap"], price=r["price"], change_pct=r["change_pct"],
            pe=r["pe"], pb=r["pb"], ps=r["ps"], ev_ebitda=r["ev_ebitda"],
            div_yield=r["div_yield"], roe=r["roe"], margin=r["margin"],
            perf_1y=r["perf_1y"], report_quarter=r["report_quarter"], industry=r["industry"],
        ))

    return ScreenerResponse(stocks=stocks, total=total)


@router.get("/meta/sectors")
async def get_sectors():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT DISTINCT sector FROM stocks WHERE sector != '' ORDER BY sector"
        )
    return [r["sector"] for r in rows]


@router.get("/meta/countries")
async def get_countries():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT DISTINCT country FROM stocks WHERE country != '' ORDER BY country"
        )
    return [r["country"] for r in rows]


@router.get("/meta/last-updated")
async def get_last_updated():
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT MAX(updated_at) AS last_updated FROM fundamentals")
    ts = row["last_updated"] if row else None
    return {"last_updated": ts.isoformat() if ts else None}


@router.get("/meta/sector-averages")
async def get_sector_averages():
    """Return average valuation/quality metrics per sector."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT s.sector,
                   AVG(f.pe) FILTER (WHERE f.pe IS NOT NULL AND f.pe > 0 AND f.pe < 200) AS pe,
                   AVG(f.pb) FILTER (WHERE f.pb IS NOT NULL AND f.pb > 0) AS pb,
                   AVG(f.ps) FILTER (WHERE f.ps IS NOT NULL AND f.ps > 0) AS ps,
                   AVG(f.ev_ebitda) FILTER (WHERE f.ev_ebitda IS NOT NULL AND f.ev_ebitda > 0 AND f.ev_ebitda < 100) AS ev_ebitda,
                   AVG(f.div_yield) FILTER (WHERE f.div_yield IS NOT NULL) AS div_yield,
                   AVG(f.roe) FILTER (WHERE f.roe IS NOT NULL AND f.roe > -100 AND f.roe < 200) AS roe,
                   AVG(f.margin) FILTER (WHERE f.margin IS NOT NULL AND f.margin > -100) AS margin,
                   AVG(f.eps) FILTER (WHERE f.eps IS NOT NULL) AS eps,
                   COUNT(*) AS count
            FROM stocks s
            JOIN fundamentals f ON s.ticker = f.ticker
            WHERE s.sector IS NOT NULL AND s.sector != ''
            GROUP BY s.sector
            ORDER BY s.sector
        """)
    return {r["sector"]: {
        "pe": round(r["pe"], 1) if r["pe"] else None,
        "pb": round(r["pb"], 1) if r["pb"] else None,
        "ps": round(r["ps"], 1) if r["ps"] else None,
        "ev_ebitda": round(r["ev_ebitda"], 1) if r["ev_ebitda"] else None,
        "div_yield": round(r["div_yield"], 1) if r["div_yield"] else None,
        "roe": round(r["roe"], 1) if r["roe"] else None,
        "margin": round(r["margin"], 1) if r["margin"] else None,
        "eps": round(r["eps"], 2) if r["eps"] else None,
        "count": r["count"],
    } for r in rows}
