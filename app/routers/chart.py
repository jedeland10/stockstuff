from fastapi import APIRouter, Query
from app.database import get_pool
from app.models import PricePoint

router = APIRouter(prefix="/api")

PERIOD_DAYS = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
    "2y": 730,
    "5y": 1825,
    "10y": 3650,
    "max": 99999,
}


@router.get("/chart/{ticker}", response_model=list[PricePoint])
async def get_chart(
    ticker: str,
    period: str = Query("1y"),
):
    days = PERIOD_DAYS.get(period, 365)
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT date, open, high, low, close, volume
            FROM prices
            WHERE ticker = $1 AND date >= (CURRENT_DATE - $2 * INTERVAL '1 day')::date::text
            ORDER BY date ASC
        """, ticker, days)
    return [
        PricePoint(date=r["date"], open=r["open"], high=r["high"], low=r["low"], close=r["close"], volume=r["volume"])
        for r in rows
    ]
