"""
Property-based tests for solution properties of calculate_efficiencies.

Tests that the returned intervals are the shortest possible (HPD intervals).
"""

import pytest
from conftest import k_n_pair_strategy
from hypothesis import given
from hypothesis import strategies as st

from pycalceff.core.cli_utils import calculate_efficiencies
from pycalceff.core.effic import (
    beta_ab,
    effic,
    interval,
    posterior_density,
    searchlower,
    searchupper,
)

# We test a wide range of confidence levels, but we have
# to exclude values too close to 0 or 1, because the search
# functions may fail for cases too close to the edges.
SMALL_CONFLEVEL = 1e-3
LARGE_CONFLEVEL = 1.0 - SMALL_CONFLEVEL


@given(k_n_pair_strategy(), st.floats(SMALL_CONFLEVEL, LARGE_CONFLEVEL))
def test_shortest_interval_property(
    k_n_pair: tuple[int, int], conflevel: float
) -> None:
    """Test that the returned interval is shorter than intervals
    obtained by shifting one end."""
    k, N = k_n_pair

    # Get the solution
    results = calculate_efficiencies([(k, N)], conflevel)
    assert len(results) == 1
    result = results[0]
    low, high = result.low, result.high
    assert 0.0 <= low < high <= 1.0
    original_width = result.width

    # Test shifting the lower end down
    if low > 0:
        delta_low = 0.05 * low  # 5% of the way toward zero
        new_low = max(0.0, low - delta_low)
        try:
            new_high = searchupper(new_low, k, N, conflevel)
            new_width = new_high - new_low
            assert new_width > original_width, (
                "Shifting low end should produce longer interval"
            )
        except ValueError:
            # No solution, which is fine
            pass

    # Test shifting the upper end up
    if high < 1.0:
        delta_high = 0.05 * (1.0 - high)  # 5% of the way toward one
        new_high = min(1.0, high + delta_high)
        try:
            new_low = searchlower(new_high, k, N, conflevel)
            new_width = new_high - new_low
            assert new_width > original_width, (
                "Shifting high end should produce longer interval"
            )
        except ValueError:
            # No solution, which is fine
            pass


@given(st.floats(0, 1), st.floats(0, 1), k_n_pair_strategy())
def test_beta_ab_properties(
    a: float, b: float, k_n_pair: tuple[int, int]
) -> None:
    """Test beta_ab properties with hypothesis."""
    if a > b:
        a, b = b, a
    k, N = k_n_pair

    result = beta_ab(a, b, k, N)

    # Area should be between 0 and 1
    assert 0 <= result <= 1

    # Area from a to a should be 0
    assert beta_ab(a, a, k, N) == 0.0

    # Area from 0 to 1 should be 1
    assert beta_ab(0.0, 1.0, k, N) == pytest.approx(1.0, abs=1e-10)


@given(
    st.floats(0, 0.9),
    k_n_pair_strategy(nmax=50),
    st.floats(SMALL_CONFLEVEL, LARGE_CONFLEVEL),
)
def test_searchupper_properties(
    low: float, k_n_pair: tuple[int, int], c: float
) -> None:
    """Test searchupper properties."""
    k, N = k_n_pair

    try:
        result = searchupper(low, k, N, c)
        assert low <= result <= 1.0
        integral = beta_ab(low, result, k, N)
        assert integral == pytest.approx(c, abs=1e-10)
    except ValueError:
        # Integral from low to 1 didn't reach c, meaning c is too large
        integral = beta_ab(low, 1.0, k, N)
        assert integral < c


@given(
    st.floats(0.1, 1),
    k_n_pair_strategy(nmax=50),
    st.floats(SMALL_CONFLEVEL, LARGE_CONFLEVEL),
)
def test_searchlower_properties(
    high: float, k_n_pair: tuple[int, int], c: float
) -> None:
    """Test searchlower properties."""
    k, N = k_n_pair

    try:
        result = searchlower(high, k, N, c)
        assert 0.0 <= result <= high
        integral = beta_ab(result, high, k, N)
        assert integral == pytest.approx(c, abs=1e-10)
    except ValueError:
        # Integral from 0 to high didn't reach c, meaning c is too large
        integral = beta_ab(0.0, high, k, N)
        assert integral < c


@given(
    st.floats(0, 0.9),
    k_n_pair_strategy(nmax=50),
    st.floats(SMALL_CONFLEVEL, LARGE_CONFLEVEL),
)
def test_interval_properties(
    low: float, k_n_pair: tuple[int, int], conflevel: float
) -> None:
    """Test interval properties."""
    k, N = k_n_pair

    try:
        result = interval(low, k, N, conflevel)
        high = low + result
        assert 0 <= high <= 1.0
        integral = beta_ab(low, high, k, N)
        assert integral == pytest.approx(conflevel, abs=1e-9)
    except ValueError:
        # Search failed, conflevel too large for this low
        pass


@given(k_n_pair_strategy(), st.floats(SMALL_CONFLEVEL, LARGE_CONFLEVEL))
def test_effic_properties(k_n_pair: tuple[int, int], conflevel: float) -> None:
    """Test effic properties with hypothesis."""
    k, N = k_n_pair

    mode, low, high = effic(k, N, conflevel)

    # Basic properties
    assert 0 <= mode <= 1
    assert 0 <= low <= high <= 1
    assert mode == k / N

    # For edge cases
    if k == 0:
        assert low == 0.0
    elif k == N:
        assert high == 1.0

    # Check that the interval contains the required mass
    integral = beta_ab(low, high, k, N)
    assert integral == pytest.approx(conflevel, abs=1e-9)


@given(k_n_pair_strategy(), st.floats(0.1, LARGE_CONFLEVEL))
def test_hpd_interval_properties(
    k_n_pair: tuple[int, int], conflevel: float
) -> None:
    """Test HPD interval properties: equal density at endpoints and exact integral."""
    k, N = k_n_pair
    _, low, high = effic(k, N, conflevel)

    # For k > 0 and k < N, posterior density should be equal at endpoints
    if 0 < k < N:
        assert posterior_density(low, k, N) == pytest.approx(
            posterior_density(high, k, N), rel=1e-6
        )

    # The integral over the interval should equal the confidence level
    integral = beta_ab(low, high, k, N)
    assert integral == pytest.approx(conflevel, abs=1e-9)
