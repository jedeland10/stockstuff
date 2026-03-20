import os

# Nordic exchanges
EXCHANGES = {
    "SE": ".ST",  # Stockholm
    "FI": ".HE",  # Helsinki
    "DK": ".CO",  # Copenhagen
    "NO": ".OL",  # Oslo
}

UPDATE_INTERVAL_HOURS = int(os.getenv("UPDATE_INTERVAL_HOURS", "6"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://stockdata:stockdata@localhost:5432/stockdata",
)
