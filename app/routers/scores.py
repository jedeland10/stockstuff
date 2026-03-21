from fastapi import APIRouter, Query
from app.database import get_pool
from app.services.scores import graham_number, piotroski_f_score, magic_formula_ranks

router = APIRouter(prefix="/api")


@router.get("/scores/{ticker}")
async def get_scores(ticker: str):
    """Compute Graham Number, Piotroski F-Score, and Magic Formula rank for a stock."""
    pool = get_pool()
    async with pool.acquire() as conn:
        # Get fundamentals
        fund = await conn.fetchrow(
            "SELECT eps, book_value_per_share, shares_outstanding, enterprise_value FROM fundamentals WHERE ticker = $1",
            ticker,
        )
        if not fund:
            return {"ticker": ticker, "graham_number": None, "f_score": None, "magic_rank": None}

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
                shares_outstanding_prev=None,
                gross_profit=curr_fin["gross_profit"],
                revenue=curr_fin["revenue"],
                gross_profit_prev=prev_fin["gross_profit"],
                revenue_prev=prev_fin["revenue"],
                net_income_prev=prev_fin["net_income"],
            )

        # Magic Formula rank — compute for this ticker among all stocks
        magic_rank = None
        all_stocks = await conn.fetch("""
            SELECT fun.ticker, fa.operating_income, fun.enterprise_value,
                   bs.net_fixed_assets, bs.current_assets, bs.current_liabilities
            FROM fundamentals fun
            JOIN stocks s ON s.ticker = fun.ticker
            LEFT JOIN LATERAL (
                SELECT operating_income FROM financials_annual
                WHERE ticker = fun.ticker ORDER BY year DESC LIMIT 1
            ) fa ON true
            LEFT JOIN LATERAL (
                SELECT net_fixed_assets, current_assets, current_liabilities FROM balance_sheet
                WHERE ticker = fun.ticker ORDER BY year DESC LIMIT 1
            ) bs ON true
            WHERE fa.operating_income IS NOT NULL
              AND fun.enterprise_value IS NOT NULL
        """)

        if all_stocks:
            stock_list = [dict(r) for r in all_stocks]
            ranked = magic_formula_ranks(stock_list)
            for r in ranked:
                if r["ticker"] == ticker:
                    magic_rank = r["magic_rank"]
                    break

    return {
        "ticker": ticker,
        "graham_number": gn,
        "f_score": f_score,
        "magic_rank": magic_rank,
        "magic_total": len(all_stocks) if all_stocks else 0,
    }


@router.get("/scores/magic-formula/ranking")
async def get_magic_formula_ranking(limit: int = Query(50, le=200)):
    """Get top stocks ranked by Magic Formula."""
    pool = get_pool()
    async with pool.acquire() as conn:
        all_stocks = await conn.fetch("""
            SELECT s.ticker, s.name, s.country, s.sector,
                   fun.pe, fun.price, fun.enterprise_value,
                   fa.operating_income,
                   bs.net_fixed_assets, bs.current_assets, bs.current_liabilities
            FROM fundamentals fun
            JOIN stocks s ON s.ticker = fun.ticker
            LEFT JOIN LATERAL (
                SELECT operating_income FROM financials_annual
                WHERE ticker = fun.ticker ORDER BY year DESC LIMIT 1
            ) fa ON true
            LEFT JOIN LATERAL (
                SELECT net_fixed_assets, current_assets, current_liabilities FROM balance_sheet
                WHERE ticker = fun.ticker ORDER BY year DESC LIMIT 1
            ) bs ON true
            WHERE fa.operating_income IS NOT NULL
              AND fun.enterprise_value IS NOT NULL
              AND fun.enterprise_value > 0
        """)

        stock_list = [dict(r) for r in all_stocks]
        ranked = magic_formula_ranks(stock_list)

    return ranked[:limit]
