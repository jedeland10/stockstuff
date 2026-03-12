from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from app.database import get_db
from app.models import CompanyDetail, AnnualFinancial

router = APIRouter(prefix="/api")


@router.get("/company/{ticker}", response_model=CompanyDetail)
async def get_company(ticker: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("""
        SELECT s.*, f.price, f.change_pct, f.pe, f.pb, f.ps, f.ev_ebitda,
               f.div_yield, f.roe, f.margin, f.eps, f.revenue, f.revenue_growth
        FROM stocks s
        LEFT JOIN fundamentals f ON s.ticker = f.ticker
        WHERE s.ticker = ?
    """, (ticker,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Stock not found")

    # Fetch annual financials
    cursor2 = await db.execute(
        "SELECT year, revenue, net_income, eps, profit_margin FROM financials_annual WHERE ticker = ? ORDER BY year DESC",
        (ticker,),
    )
    fin_rows = await cursor2.fetchall()
    financials = [
        AnnualFinancial(year=r[0], revenue=r[1], net_income=r[2], eps=r[3], profit_margin=r[4])
        for r in fin_rows
    ]

    return CompanyDetail(
        ticker=row[0], name=row[1], exchange=row[2], country=row[3],
        sector=row[4], industry=row[5], market_cap=row[6], description=row[7],
        price=row[8], change_pct=row[9], pe=row[10], pb=row[11],
        ps=row[12], ev_ebitda=row[13], div_yield=row[14], roe=row[15],
        margin=row[16], eps=row[17], revenue=row[18], revenue_growth=row[19],
        financials=financials,
    )
