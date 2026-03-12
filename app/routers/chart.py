from fastapi import APIRouter, Depends, Query
import aiosqlite
from app.database import get_db
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
    db: aiosqlite.Connection = Depends(get_db),
):
    days = PERIOD_DAYS.get(period, 365)
    cursor = await db.execute("""
        SELECT date, open, high, low, close, volume
        FROM prices
        WHERE ticker = ? AND date >= date('now', ?)
        ORDER BY date ASC
    """, (ticker, f"-{days} days"))
    rows = await cursor.fetchall()
    return [
        PricePoint(date=r[0], open=r[1], high=r[2], low=r[3], close=r[4], volume=r[5])
        for r in rows
    ]
