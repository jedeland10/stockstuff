#!/usr/bin/env python3
"""One-time migration: convert all existing monetary data from local currencies to EUR.

Finnish stocks (.HE) are already in EUR and will be skipped.
Run this once after deploying the EUR conversion changes to the fetcher.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncpg
from app.config import DATABASE_URL
from app.database import init_db
from app.services.fetcher import get_fx_rates, _SUFFIX_CURRENCY
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


def get_rate_for_ticker(ticker: str, rates: dict) -> float:
    """Return the EUR conversion rate for a ticker. 1.0 for EUR stocks."""
    for suffix, currency in _SUFFIX_CURRENCY.items():
        if ticker.endswith(suffix):
            return rates.get(currency, 1.0)
    return 1.0


async def migrate():
    rates = get_fx_rates()
    logger.info(f"Exchange rates: {rates}")

    if not rates or len(rates) < 3:
        logger.error("Could not fetch exchange rates. Aborting.")
        return

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await init_db(conn)

        # Get all tickers with their suffixes
        tickers = [r["ticker"] for r in await conn.fetch("SELECT ticker FROM stocks")]
        logger.info(f"Total tickers: {len(tickers)}")

        # Group by currency
        by_currency: dict[str, list[str]] = {}
        for t in tickers:
            for suffix, currency in _SUFFIX_CURRENCY.items():
                if t.endswith(suffix):
                    by_currency.setdefault(currency, []).append(t)
                    break

        for currency, ticker_list in by_currency.items():
            rate = rates.get(currency, 1.0)
            if currency == "EUR":
                logger.info(f"  {currency}: {len(ticker_list)} tickers — already EUR, skipping")
                continue
            logger.info(f"  {currency}: {len(ticker_list)} tickers — rate {rate:.6f}")

            placeholders = ", ".join(f"${i+1}" for i in range(len(ticker_list)))
            rate_param = len(ticker_list) + 1

            # 1. fundamentals: price, eps, revenue, enterprise_value, book_value_per_share
            await conn.execute(f"""
                UPDATE fundamentals SET
                    price = price * ${rate_param},
                    eps = eps * ${rate_param},
                    revenue = revenue * ${rate_param},
                    enterprise_value = enterprise_value * ${rate_param},
                    book_value_per_share = book_value_per_share * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            # 2. stocks: market_cap
            await conn.execute(f"""
                UPDATE stocks SET market_cap = market_cap * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            # 3. prices: open, high, low, close
            await conn.execute(f"""
                UPDATE prices SET
                    open = open * ${rate_param},
                    high = high * ${rate_param},
                    low = low * ${rate_param},
                    close = close * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            # 4. financials_annual: revenue, operating_income, ebitda, net_income, eps, gross_profit
            await conn.execute(f"""
                UPDATE financials_annual SET
                    revenue = revenue * ${rate_param},
                    operating_income = operating_income * ${rate_param},
                    ebitda = ebitda * ${rate_param},
                    net_income = net_income * ${rate_param},
                    eps = eps * ${rate_param},
                    gross_profit = gross_profit * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            # 5. financials_quarterly
            await conn.execute(f"""
                UPDATE financials_quarterly SET
                    revenue = revenue * ${rate_param},
                    operating_income = operating_income * ${rate_param},
                    ebitda = ebitda * ${rate_param},
                    net_income = net_income * ${rate_param},
                    eps = eps * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            # 6. balance_sheet
            await conn.execute(f"""
                UPDATE balance_sheet SET
                    total_assets = total_assets * ${rate_param},
                    total_debt = total_debt * ${rate_param},
                    net_debt = net_debt * ${rate_param},
                    cash = cash * ${rate_param},
                    total_equity = total_equity * ${rate_param},
                    intangible_assets = intangible_assets * ${rate_param},
                    current_assets = current_assets * ${rate_param},
                    current_liabilities = current_liabilities * ${rate_param},
                    net_fixed_assets = net_fixed_assets * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            # 7. cashflow
            await conn.execute(f"""
                UPDATE cashflow SET
                    operating_cf = operating_cf * ${rate_param},
                    capex = capex * ${rate_param},
                    free_cf = free_cf * ${rate_param}
                WHERE ticker IN ({placeholders})
            """, *ticker_list, rate)

            logger.info(f"  {currency}: converted {len(ticker_list)} tickers")

        # Recompute performance since prices changed
        logger.info("Recomputing performance metrics...")
        from app.services.updater import compute_performance
        await compute_performance(conn)

        logger.info("Migration complete! All monetary values are now in EUR.")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate())
