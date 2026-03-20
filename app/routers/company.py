from fastapi import APIRouter, HTTPException
from app.database import get_pool
from app.models import CompanyDetail, AnnualFinancial, QuarterlyFinancial, BalanceSheetEntry, CashflowEntry

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
            "SELECT year, revenue, operating_income, ebitda, net_income, eps, profit_margin FROM financials_annual WHERE ticker = $1 ORDER BY year DESC",
            ticker,
        )

        # Quarterly financials
        q_rows = await conn.fetch(
            "SELECT period, revenue, operating_income, ebitda, net_income, eps, profit_margin FROM financials_quarterly WHERE ticker = $1 ORDER BY period DESC",
            ticker,
        )

        # Balance sheet
        bs_rows = await conn.fetch(
            "SELECT year, total_assets, total_debt, net_debt, cash, total_equity, intangible_assets FROM balance_sheet WHERE ticker = $1 ORDER BY year DESC",
            ticker,
        )

        # Cash flow
        cf_rows = await conn.fetch(
            "SELECT year, operating_cf, capex, free_cf FROM cashflow WHERE ticker = $1 ORDER BY year DESC",
            ticker,
        )

    financials = [
        AnnualFinancial(year=r["year"], revenue=r["revenue"], operating_income=r["operating_income"], ebitda=r["ebitda"], net_income=r["net_income"], eps=r["eps"], profit_margin=r["profit_margin"])
        for r in fin_rows
    ]
    quarterly_financials = [
        QuarterlyFinancial(period=r["period"], revenue=r["revenue"], operating_income=r["operating_income"], ebitda=r["ebitda"], net_income=r["net_income"], eps=r["eps"], profit_margin=r["profit_margin"])
        for r in q_rows
    ]
    balance_sheet = [
        BalanceSheetEntry(year=r["year"], total_assets=r["total_assets"], total_debt=r["total_debt"], net_debt=r["net_debt"], cash=r["cash"], total_equity=r["total_equity"], intangible_assets=r["intangible_assets"])
        for r in bs_rows
    ]
    cashflow = [
        CashflowEntry(year=r["year"], operating_cf=r["operating_cf"], capex=r["capex"], free_cf=r["free_cf"])
        for r in cf_rows
    ]

    return CompanyDetail(
        ticker=row["ticker"], name=row["name"], exchange=row["exchange"], country=row["country"],
        sector=row["sector"], industry=row["industry"], market_cap=row["market_cap"], description=row["description"],
        price=row["price"], change_pct=row["change_pct"], pe=row["pe"], pb=row["pb"],
        ps=row["ps"], ev_ebitda=row["ev_ebitda"], div_yield=row["div_yield"], roe=row["roe"],
        margin=row["margin"], eps=row["eps"], revenue=row["revenue"], revenue_growth=row["revenue_growth"],
        financials=financials, quarterly_financials=quarterly_financials,
        balance_sheet=balance_sheet, cashflow=cashflow,
    )
