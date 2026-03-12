"""Derived ratio computations — placeholder for future calculated metrics."""


def earnings_yield(pe: float | None) -> float | None:
    if pe and pe > 0:
        return round(1 / pe * 100, 2)
    return None
