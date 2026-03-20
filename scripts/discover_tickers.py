#!/usr/bin/env python3
"""Discover all valid Nordic tickers by scanning Yahoo Finance.
Runs sequentially to avoid rate-limiting. Takes ~2-3 hours for a full scan.
Results are written to data/discovered_tickers.json incrementally.
"""
import asyncio
import json
import string
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from curl_cffi.requests import Session
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1d&interval=1d"
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "discovered_tickers.json"

EXCHANGES = {
    ".OL": "NO",
    ".ST": "SE",
    ".HE": "FI",
    ".CO": "DK",
}


def check_ticker(session: Session, ticker: str) -> dict | None:
    """Check if a ticker is valid on Yahoo Finance. Returns metadata or None."""
    try:
        r = session.get(CHART_URL.format(ticker), timeout=5)
        if r.status_code == 200:
            data = r.json()
            result = data.get("chart", {}).get("result")
            if result:
                meta = result[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                if price and price > 0:
                    return {
                        "ticker": ticker,
                        "name": meta.get("shortName", ""),
                        "exchange": meta.get("exchangeName", ""),
                        "currency": meta.get("currency", ""),
                    }
    except Exception:
        pass
    return None


def generate_candidates(suffix: str) -> list[str]:
    """Generate all plausible ticker patterns for a Nordic exchange."""
    letters = string.ascii_uppercase
    candidates = set()

    # 2-letter: AA.XX through ZZ.XX
    for a in letters:
        for b in letters:
            candidates.add(f"{a}{b}{suffix}")

    # 3-letter: AAA.XX through ZZZ.XX
    for a in letters:
        for b in letters:
            for c in letters:
                candidates.add(f"{a}{b}{c}{suffix}")

    # 4-letter: common patterns (not all 456k combos)
    # Use vowel + consonant patterns
    consonants = "BCDFGHJKLMNPQRSTVWXYZ"
    vowels = "AEIOU"
    for a in letters:
        for b in letters:
            for c in letters:
                for d in vowels:
                    candidates.add(f"{a}{b}{c}{d}{suffix}")
                for d in consonants[:10]:  # Limit to common consonants
                    candidates.add(f"{a}{b}{c}{d}{suffix}")

    # Add -A and -B variants for Swedish/Danish
    if suffix in [".ST", ".CO"]:
        base_tickers = list(candidates)
        for t in base_tickers:
            base = t.replace(suffix, "")
            if len(base) <= 5:
                candidates.add(f"{base}-A{suffix}")
                candidates.add(f"{base}-B{suffix}")

    # Also add known 5+ letter patterns
    for a in letters:
        for b in letters:
            for c in letters:
                for d in letters:
                    for e in letters:
                        # Only check CVCVC and CVCCV patterns to limit scope
                        if (b in vowels or d in vowels):
                            candidates.add(f"{a}{b}{c}{d}{e}{suffix}")

    return sorted(candidates)


def load_existing() -> dict:
    """Load previously discovered tickers."""
    if OUTPUT.exists():
        with open(OUTPUT) as f:
            return json.load(f)
    return {}


def save_results(results: dict):
    """Save discovered tickers incrementally."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)


def discover():
    existing = load_existing()
    checked = set(existing.get("_checked", []))
    tickers = existing.get("tickers", {})

    logger.info(f"Loaded {len(tickers)} previously discovered tickers, {len(checked)} already checked")

    session = Session(impersonate="chrome120")
    request_count = 0
    new_found = 0

    for suffix, country in EXCHANGES.items():
        # Generate candidates — for speed, start with 2-3 letter combos only
        candidates = []

        # 2-letter
        for a in string.ascii_uppercase:
            for b in string.ascii_uppercase:
                t = f"{a}{b}{suffix}"
                if t not in checked:
                    candidates.append(t)

        # 3-letter
        for a in string.ascii_uppercase:
            for b in string.ascii_uppercase:
                for c in string.ascii_uppercase:
                    t = f"{a}{b}{c}{suffix}"
                    if t not in checked:
                        candidates.append(t)

        # -B variants for 2-4 letter bases (SE/DK)
        if suffix in [".ST", ".CO"]:
            extras = []
            for a in string.ascii_uppercase:
                for b in string.ascii_uppercase:
                    for var in ["-A", "-B"]:
                        t = f"{a}{b}{var}{suffix}"
                        if t not in checked:
                            extras.append(t)
                        for c in string.ascii_uppercase:
                            t = f"{a}{b}{c}{var}{suffix}"
                            if t not in checked:
                                extras.append(t)
            candidates.extend(extras)

        logger.info(f"{suffix} ({country}): {len(candidates)} candidates to check")

        for i, ticker in enumerate(candidates):
            result = check_ticker(session, ticker)
            checked.add(ticker)

            if result:
                tickers[ticker] = result
                new_found += 1
                logger.info(f"  FOUND: {ticker} ({result['name']})")

            request_count += 1

            # Rotate session every 500 requests
            if request_count % 500 == 0:
                session = Session(impersonate="chrome120")

            # Save progress every 1000 checks
            if request_count % 1000 == 0:
                existing["tickers"] = tickers
                existing["_checked"] = list(checked)
                save_results(existing)
                logger.info(f"  Progress: {request_count} checked, {len(tickers)} found, {new_found} new")

    # Final save
    existing["tickers"] = tickers
    existing["_checked"] = list(checked)
    save_results(existing)

    logger.info(f"\nDiscovery complete:")
    logger.info(f"  Total valid tickers: {len(tickers)}")
    logger.info(f"  New this run: {new_found}")
    for suffix, country in EXCHANGES.items():
        count = len([t for t in tickers if t.endswith(suffix)])
        logger.info(f"  {country} ({suffix}): {count}")


if __name__ == "__main__":
    discover()
