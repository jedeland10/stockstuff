# Plan: Börsdata-Style Feature Expansion

## Reference
Börsdata.se has four main tabs per stock: Overview, Report, Key Numbers, Technical.
Goal: replicate the most valuable features using yfinance data.

---

## 1. Fetch More Financial Data

### What we have now
- `yf.income_stmt` → revenue, net income, EPS, profit margin (annual only)
- `yf.info` → PE, PB, PS, EV/EBITDA, div yield, ROE, market cap

### What we need to add
- **`yf.balance_sheet`** → total assets, total debt, cash, equity, intangible assets
- **`yf.cashflow`** → operating cash flow, capex, free cash flow
- **`yf.quarterly_income_stmt`** → quarterly revenue, earnings, margins
- **`yf.quarterly_balance_sheet`** → quarterly balance sheet snapshots
- **`yf.quarterly_cashflow`** → quarterly cash flow

### New DB tables
```
financials_quarterly (ticker, period, revenue, operating_income, ebitda, net_income, eps, profit_margin)
balance_sheet_annual (ticker, year, total_assets, total_debt, net_debt, cash, equity, intangible_assets)
balance_sheet_quarterly (ticker, period, ...)
cashflow_annual (ticker, year, operating_cf, capex, free_cf)
cashflow_quarterly (ticker, period, ...)
```

---

## 2. Overview Tab Enhancements

### Already working
- Price line chart with period selector
- Net sales, earnings/share, profit margin bar charts
- Company info sidebar with key ratios

### To add
- **MA50 / MA200 overlays** on price chart — compute from price data client-side
- **Revenue growth bar chart** — compute YoY % change from annual data
- **Operating income bar chart** — needs income_stmt `Operating Income` field
- **Operating margin trend** — compute from operating income / revenue

---

## 3. Report Tab (New)

### Financial detail charts (bar charts, 5-year history)
Row 1:
- Net Sales — already have
- Operating Income — from `yf.income_stmt`
- EBITDA — from `yf.income_stmt`
- Earnings — already have (net income)

Row 2:
- Revenue growth % — computed YoY
- EBIT growth % — computed YoY
- Earnings growth % — computed YoY
- Profit margin % — already have

### Quarterly breakdown
- Same metrics but per quarter (Q1-Q4 grouped by year)
- Requires `yf.quarterly_income_stmt`

---

## 4. Key Numbers Tab (New)

### Valuation section (top row, current values)
- Net Sales, EBIT, Earnings, P/E — mostly have
- Market Cap, EV — have via `yf.info`
- EBITDA margin, Profit margin, FCF margin — computable
- ROE, ROA — partially have

### Valuation history sparklines (5-year mini charts)
- P/E over time, P/S over time, EV/EBIT over time, Market Cap over time
- **Requires**: storing quarterly/annual snapshots of these ratios, or computing from price + fundamentals

### Balance sheet charts
- Equity ratio (equity / total assets)
- Net debt
- Cash
- Intangible assets %
- **Source**: `yf.balance_sheet`

### Cash flow charts
- Operating cash flow
- Capex
- Free cash flow (OCF - Capex)
- Earnings/FCF ratio
- **Source**: `yf.cashflow`

### Scoring models (sidebar)
- **Graham Number** — sqrt(22.5 × EPS × Book Value per Share) — computable
- **Piotroski F-Score** (0-9) — computable from income stmt + balance sheet + cash flow
- **FS&G Dividend Score** — needs dividend history

---

## 5. Technical Tab (New)

### Performance metrics (top row)
- 1d, 1w, 1m, 3m, 6m, 1y, 3y, 5y, YTD returns — **all computable** from price data

### Price chart enhancements
- Candlestick view (OHLC data already stored)
- MA50, MA200 overlays
- Volume bars with SMA
- Report date markers (Q1-Q4)

### Technical indicators (compute client-side or via API)
- **RSI(14)** — relative strength index
- **MACD** — 12/26/9 EMA crossover
- **Bollinger Bands** — 20-day SMA ± 2 std dev
- **VPVR** — volume profile (advanced, lower priority)

### Technical stats sidebar
- Price vs MA 20d/50d/200d
- ADR (average daily range)
- Volatility (20d, 30d)
- RSI current value
- Volume vs 20d average

---

## 6. Data we CAN'T get from yfinance
- Insider transactions (Börsdata has this)
- Short interest data
- Buyback history
- Board composition
- Brokerage recommendations detail

These would need additional data sources later.

---

## 7. Implementation Priority

### Phase 1 — More data, same UI structure
1. Extend fetcher to pull balance sheet + cash flow + quarterly data
2. Add new DB tables + migration
3. Extend backfill script
4. New API endpoints for the extra data

### Phase 2 — Overview tab polish
5. MA50/MA200 on price chart
6. More financial bar charts (operating income, EBITDA)
7. Growth rate charts

### Phase 3 — Report tab
8. Quarterly financial charts
9. Growth trend charts

### Phase 4 — Key Numbers tab
10. Balance sheet charts
11. Cash flow charts
12. Valuation history sparklines
13. Graham/F-Score computations

### Phase 5 — Technical tab
14. Candlestick chart
15. RSI, MACD, Bollinger overlays
16. Performance metrics row
17. Technical stats sidebar
