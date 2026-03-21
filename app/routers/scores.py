from fastapi import APIRouter
from app.database import get_pool
from app.services.scores import graham_number, piotroski_f_score

router = APIRouter(prefix="/api")


@router.get("/scores/{ticker}")
async def get_scores(ticker: str):
    """Compute Graham Number and Piotroski F-Score for a stock."""
    pool = get_pool()
    async with pool.acquire() as conn:
        # Get fundamentals
        fund = await conn.fetchrow(
            "SELECT eps, book_value_per_share, shares_outstanding, enterprise_value FROM fundamentals WHERE ticker = $1",
            ticker,
        )
        if not fund:
            return {"ticker": ticker, "graham_number": None, "f_score": None}

        # Graham Number
        gn = graham_number(fund["eps"], fund["book_value_per_share"])

        # For F-Score, get the two most recent years of data
        fin_rows = await conn.fetch(
            "SELECT year, revenue, net_income, gross_profit FROM financials_annual WHERE ticker = $1 ORDER BY year DESC LIMIT 2",
            ticker,
        )
        bs_rows = await conn.fetch(
            "SELECT year, total_assets, total_debt, current_assets, current_liabilities FROM balance_sheet WHERE ticker = $1 ORDER BY year DESC LIMIT 2",
            ticker,
        )
        cf_rows = await conn.fetch(
            "SELECT year, operating_cf FROM cashflow WHERE ticker = $1 ORDER BY year DESC LIMIT 1",
            ticker,
        )

        f_score = None
        if len(fin_rows) >= 2 and len(bs_rows) >= 2 and cf_rows:
            curr_fin = fin_rows[0]
            prev_fin = fin_rows[1]
            curr_bs = bs_rows[0]
            prev_bs = bs_rows[1]
            curr_cf = cf_rows[0]

            f_score = piotroski_f_score(
                net_income=curr_fin["net_income"],
                operating_cf=curr_cf["operating_cf"],
                total_assets=curr_bs["total_assets"],
                total_assets_prev=prev_bs["total_assets"],
                total_debt=curr_bs["total_debt"],
                total_debt_prev=prev_bs["total_debt"],
                current_assets=curr_bs["current_assets"],
                current_liabilities=curr_bs["current_liabilities"],
                current_assets_prev=prev_bs["current_assets"],
                current_liabilities_prev=prev_bs["current_liabilities"],
                shares_outstanding=fund["shares_outstanding"],
                shares_outstanding_prev=None,  # Would need historical data
                gross_profit=curr_fin["gross_profit"],
                revenue=curr_fin["revenue"],
                gross_profit_prev=prev_fin["gross_profit"],
                revenue_prev=prev_fin["revenue"],
                net_income_prev=prev_fin["net_income"],
            )

    return {
        "ticker": ticker,
        "graham_number": gn,
        "f_score": f_score,
    }
