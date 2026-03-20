from fastapi import APIRouter, HTTPException
from app.database import get_pool
from app.models import CompanyDetail, AnnualFinancial

router = APIRouter(prefix="/api")


@router.get("/company/{ticker}", response_model=CompanyDetail)
async def get_company(ticker: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT s.ticker, s.name, s.exchange, s.country, s.sector, s.industry,
                   s.market_cap, s.description,
                   f.price, f.change_pct, f.pe, f.pb, f.ps, f.ev_ebitda,
                   f.div_yield, f.roe, f.margin, f.eps, f.revenue, f.revenue_growth
            FROM stocks s
            LEFT JOIN fundamentals f ON s.ticker = f.ticker
            WHERE s.ticker = $1
        """, ticker)
        if not row:
            raise HTTPException(status_code=404, detail="Stock not found")

        fin_rows = await conn.fetch(
            "SELECT year, revenue, net_income, eps, profit_margin FROM financials_annual WHERE ticker = $1 ORDER BY year DESC",
            ticker,
        )

    financials = [
        AnnualFinancial(year=r["year"], revenue=r["revenue"], net_income=r["net_income"], eps=r["eps"], profit_margin=r["profit_margin"])
        for r in fin_rows
    ]

    return CompanyDetail(
        ticker=row["ticker"], name=row["name"], exchange=row["exchange"], country=row["country"],
        sector=row["sector"], industry=row["industry"], market_cap=row["market_cap"], description=row["description"],
        price=row["price"], change_pct=row["change_pct"], pe=row["pe"], pb=row["pb"],
        ps=row["ps"], ev_ebitda=row["ev_ebitda"], div_yield=row["div_yield"], roe=row["roe"],
        margin=row["margin"], eps=row["eps"], revenue=row["revenue"], revenue_growth=row["revenue_growth"],
        financials=financials,
    )
