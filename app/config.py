from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "stocks.db"

# Nordic exchanges
EXCHANGES = {
    "SE": ".ST",    # Stockholm
    "FI": ".HE",    # Helsinki
    "DK": ".CO",    # Copenhagen
    "NO": ".OL",    # Oslo
}

UPDATE_INTERVAL_HOURS = 6
