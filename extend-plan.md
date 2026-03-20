# Plan: Extend Stock Coverage

## Current State
- 288 hand-picked Nordic large/mid-cap tickers hardcoded in `seed_tickers.py`
- All stock data (name, sector, price, fundamentals, history, financials) fetched from Yahoo Finance via `yfinance` — pure API fetching, no scraping
- The only bottleneck: we need to *know* which tickers exist before we can fetch data for them

## Terminology
- **Ticker** = unique stock identifier (e.g. `VOLV-B.ST` = Volvo B-share on Stockholm)
- Given a ticker, yfinance returns everything else — it's the lookup key

## Goal
Get all Nordic-listed stocks (~2000+) instead of a curated 288, using fetch-only approaches (no scraping).

## Available Exchanges
| Exchange | Suffix | Estimated listings |
|---|---|---|
| Nasdaq Stockholm | `.ST` | ~1000+ |
| Nasdaq Helsinki | `.HE` | ~150+ |
| Nasdaq Copenhagen | `.CO` | ~200+ |
| Oslo Børs | `.OL` | ~300+ |

## Approach: Dynamic Ticker Discovery (fetch-only)

### Option 1 — Nasdaq Nordic Instrument Lists
Nasdaq Nordic publishes downloadable CSVs/Excel of all listed instruments. Direct file download, not scraping. Covers Stockholm, Helsinki, Copenhagen. Oslo Børs has a separate equivalent.

### Option 2 — Yahoo Finance Screener API
Query Yahoo's screener for all stocks on exchanges `.ST`, `.HE`, `.CO`, `.OL`. Unofficial API but still pure fetching.

### Option 3 — Other Free Financial APIs
Some providers expose exchange listing endpoints.

## Recommended Path
1. Investigate what Nasdaq Nordic exposes as downloadable data (CSV/Excel)
2. Find Oslo Børs equivalent
3. Build a ticker discovery step that downloads these lists, parses tickers, and maps them to Yahoo Finance format (`{ticker}.{suffix}`)
4. Replace hardcoded `TICKERS` list in `seed_tickers.py` with dynamic fetch
5. Keep yfinance as the sole data source for all stock data — only the *ticker list* changes

## Open Questions
- What format does the Nasdaq Nordic instrument download use?
- Does Oslo Børs have an equivalent public download?
- Rate limiting considerations when seeding 2000+ stocks via yfinance?
