"""API endpoint tests — verify response shapes and status codes."""
import pytest


@pytest.mark.anyio
async def test_screener_returns_stocks(client):
    r = await client.get("/api/screener?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "stocks" in data
    assert "total" in data
    assert isinstance(data["stocks"], list)
    assert isinstance(data["total"], int)


@pytest.mark.anyio
async def test_screener_has_required_fields(client):
    r = await client.get("/api/screener?limit=1")
    data = r.json()
    if data["stocks"]:
        stock = data["stocks"][0]
        required = ["ticker", "name", "country", "sector", "price", "pe", "pb", "ps", "market_cap"]
        for field in required:
            assert field in stock, f"Missing field: {field}"


@pytest.mark.anyio
async def test_screener_country_filter(client):
    r = await client.get("/api/screener?country=SE&limit=5")
    assert r.status_code == 200
    data = r.json()
    for stock in data["stocks"]:
        assert stock["country"] == "SE"


@pytest.mark.anyio
async def test_screener_search(client):
    r = await client.get("/api/screener?search=volvo&limit=5")
    assert r.status_code == 200


@pytest.mark.anyio
async def test_screener_pagination(client):
    r1 = await client.get("/api/screener?limit=2&offset=0")
    r2 = await client.get("/api/screener?limit=2&offset=2")
    assert r1.status_code == 200
    assert r2.status_code == 200
    stocks1 = r1.json()["stocks"]
    stocks2 = r2.json()["stocks"]
    if stocks1 and stocks2:
        assert stocks1[0]["ticker"] != stocks2[0]["ticker"]


@pytest.mark.anyio
async def test_meta_sectors(client):
    r = await client.get("/api/meta/sectors")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_meta_countries(client):
    r = await client.get("/api/meta/countries")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_company_detail(client):
    # First get a ticker from screener
    r = await client.get("/api/screener?limit=1")
    stocks = r.json()["stocks"]
    if not stocks:
        pytest.skip("No stocks in database")

    ticker = stocks[0]["ticker"]
    r = await client.get(f"/api/company/{ticker}")
    assert r.status_code == 200
    data = r.json()
    assert data["ticker"] == ticker
    required = ["name", "sector", "price", "pe", "financials", "quarterly_financials", "balance_sheet", "cashflow"]
    for field in required:
        assert field in data, f"Missing field: {field}"
    assert isinstance(data["financials"], list)
    assert isinstance(data["quarterly_financials"], list)
    assert isinstance(data["balance_sheet"], list)
    assert isinstance(data["cashflow"], list)


@pytest.mark.anyio
async def test_company_not_found(client):
    r = await client.get("/api/company/FAKE_TICKER_XYZ")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_chart_data(client):
    r = await client.get("/api/screener?limit=1")
    stocks = r.json()["stocks"]
    if not stocks:
        pytest.skip("No stocks in database")

    ticker = stocks[0]["ticker"]
    r = await client.get(f"/api/chart/{ticker}?period=1y")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        point = data[0]
        assert "date" in point
        assert "close" in point
        assert "volume" in point


@pytest.mark.anyio
async def test_scores(client):
    r = await client.get("/api/screener?limit=1")
    stocks = r.json()["stocks"]
    if not stocks:
        pytest.skip("No stocks in database")

    ticker = stocks[0]["ticker"]
    r = await client.get(f"/api/scores/{ticker}")
    assert r.status_code == 200
    data = r.json()
    assert data["ticker"] == ticker
    assert "graham_number" in data
    assert "f_score" in data
    assert "magic_rank" in data


@pytest.mark.anyio
async def test_index_returns_html(client):
    from pathlib import Path
    build = Path(__file__).resolve().parent.parent / "frontend" / "build" / "index.html"
    if not build.exists():
        pytest.skip("Frontend not built")
    r = await client.get("/")
    assert r.status_code == 200
    assert "html" in r.headers.get("content-type", "").lower()
