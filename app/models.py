from pydantic import BaseModel
from typing import Optional


class StockRow(BaseModel):
    ticker: str
    name: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    ps: Optional[float] = None
    ev_ebitda: Optional[float] = None
    div_yield: Optional[float] = None
    roe: Optional[float] = None
    margin: Optional[float] = None
    market_cap: Optional[float] = None
    perf_1y: Optional[float] = None
    report_quarter: Optional[str] = None
    industry: Optional[str] = None


class ScreenerResponse(BaseModel):
    stocks: list[StockRow]
    total: int


class PricePoint(BaseModel):
    date: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None


class AnnualFinancial(BaseModel):
    year: int
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    profit_margin: Optional[float] = None


class CompanyDetail(BaseModel):
    ticker: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    description: Optional[str] = None
    price: Optional[float] = None
    change_pct: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    ps: Optional[float] = None
    ev_ebitda: Optional[float] = None
    div_yield: Optional[float] = None
    roe: Optional[float] = None
    margin: Optional[float] = None
    eps: Optional[float] = None
    revenue: Optional[float] = None
    revenue_growth: Optional[float] = None
    financials: list[AnnualFinancial] = []
