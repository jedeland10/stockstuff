"""Unit tests for scoring models."""
from app.services.scores import graham_number, piotroski_f_score, magic_formula_ranks


def test_graham_number_valid():
    gn = graham_number(eps=10.0, book_value_per_share=50.0)
    assert gn is not None
    assert abs(gn - 106.07) < 0.1


def test_graham_number_negative_eps():
    assert graham_number(eps=-5.0, book_value_per_share=50.0) is None


def test_graham_number_none():
    assert graham_number(eps=None, book_value_per_share=50.0) is None
    assert graham_number(eps=10.0, book_value_per_share=None) is None


def test_piotroski_strong():
    score = piotroski_f_score(
        net_income=100, operating_cf=120,
        total_assets=1000, total_assets_prev=950,
        total_debt=200, total_debt_prev=250,
        current_assets=400, current_liabilities=200,
        current_assets_prev=350, current_liabilities_prev=200,
        shares_outstanding=100, shares_outstanding_prev=100,
        gross_profit=500, revenue=1000,
        gross_profit_prev=450, revenue_prev=900,
        net_income_prev=80,
    )
    assert score is not None
    assert score >= 7


def test_piotroski_weak():
    score = piotroski_f_score(
        net_income=-50, operating_cf=-20,
        total_assets=1000, total_assets_prev=900,
        total_debt=500, total_debt_prev=400,
        current_assets=200, current_liabilities=300,
        current_assets_prev=250, current_liabilities_prev=200,
        shares_outstanding=110, shares_outstanding_prev=100,
        gross_profit=300, revenue=1000,
        gross_profit_prev=350, revenue_prev=900,
        net_income_prev=50,
    )
    assert score is not None
    assert score <= 3


def test_piotroski_insufficient_data():
    score = piotroski_f_score(
        net_income=None, operating_cf=None,
        total_assets=None, total_assets_prev=None,
        total_debt=None, total_debt_prev=None,
        current_assets=None, current_liabilities=None,
        current_assets_prev=None, current_liabilities_prev=None,
        shares_outstanding=None, shares_outstanding_prev=None,
        gross_profit=None, revenue=None,
        gross_profit_prev=None, revenue_prev=None,
        net_income_prev=None,
    )
    assert score is None


def test_magic_formula_ranking():
    stocks = [
        {"ticker": "A", "operating_income": 100, "enterprise_value": 500, "net_fixed_assets": 200, "current_assets": 300, "current_liabilities": 100},
        {"ticker": "B", "operating_income": 50, "enterprise_value": 200, "net_fixed_assets": 100, "current_assets": 150, "current_liabilities": 50},
        {"ticker": "C", "operating_income": 10, "enterprise_value": 1000, "net_fixed_assets": 500, "current_assets": 200, "current_liabilities": 300},
    ]
    ranked = magic_formula_ranks(stocks)
    assert len(ranked) == 3
    # All should have magic_rank
    for s in ranked:
        assert s["magic_rank"] is not None
    # First should have lowest rank number
    assert ranked[0]["magic_rank"] <= ranked[1]["magic_rank"]


def test_magic_formula_missing_data():
    stocks = [
        {"ticker": "A", "operating_income": None, "enterprise_value": 500, "net_fixed_assets": 200, "current_assets": 300, "current_liabilities": 100},
    ]
    ranked = magic_formula_ranks(stocks)
    assert ranked[0]["magic_rank"] is None
