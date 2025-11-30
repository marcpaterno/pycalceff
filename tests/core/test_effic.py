"""
Tests for core efficiency calculation functions.

Tests the mathematical functions in effic.py using unit tests and hypothesis.
"""

import pytest
import scipy.stats as stats

from pycalceff.core.effic import (
    BoundDirection,
    beta_ab,
    beta_logpdf,
    beta_pdf,
    effic,
    posterior_density,
    probability_mass,
    search_bound,
    shortest_hpd_beta,
)


def test_beta_ab() -> None:
    """Test beta_ab function with known values."""
    # For k=1, N=2, this is beta(2,1) from 0 to 1, which should be 1
    result = beta_ab(0.0, 1.0, 1, 2)
    assert result == pytest.approx(1.0, abs=1e-10)

    # Area from 0 to 0.5 for k=1, N=2
    result = beta_ab(0.0, 0.5, 1, 2)
    expected = 0.5  # Since beta(2,1) pdf integrates to 0.5 from 0 to 0.5
    assert result == pytest.approx(expected, abs=1e-6)


def test_search_bound_upper() -> None:
    """Test search_bound for upper bound."""
    # For k=10, N=20, low=0.4, c=0.8
    result = search_bound(0.4, 10, 20, 0.8, BoundDirection.UPPER)
    assert result > 0.4
    assert result <= 1.0


def test_search_bound_upper_integral_too_small() -> None:
    """Test search_bound raises ValueError when integral < c for upper."""
    # Use parameters where the upper tail has very little probability mass
    low = 0.8
    k = 5
    ntrials = 10
    c = 0.9  # Require 90% confidence, but upper 20% tail has much less

    with pytest.raises(
        ValueError, match="Cannot find upper bound: insufficient mass"
    ):
        search_bound(low, k, ntrials, c, BoundDirection.UPPER)


def test_search_bound_upper_exact_integral() -> None:
    """Test search_bound when integral from low to 1.0 exactly equals c."""
    # For k=1, N=2, beta_ab(0.5, 1.0, 1, 2) = 0.5
    result = search_bound(0.5, 1, 2, 0.5, BoundDirection.UPPER)
    assert result == 1.0


def test_search_bound_lower_integral_too_small() -> None:
    """Test search_bound raises ValueError when integral < c for lower."""
    # Use parameters where the lower tail has very little probability mass
    high = 0.05
    k = 99
    ntrials = 100
    c = 0.5  # Require 50% confidence, but lower 5% tail has much less

    with pytest.raises(
        ValueError, match="Cannot find lower bound: insufficient mass"
    ):
        search_bound(high, k, ntrials, c, BoundDirection.LOWER)

    # Verify the condition
    integral = beta_ab(0.0, high, k, ntrials)
    assert integral < c


def test_search_bound_lower_exact_integral() -> None:
    """Test search_bound when integral from 0.0 to high exactly equals c."""
    # For k=1, N=2, beta_ab(0.0, 0.5, 1, 2) = 0.5
    result = search_bound(0.5, 1, 2, 0.5, BoundDirection.LOWER)
    assert result == 0.0


def test_search_bound_lower() -> None:
    """Test search_bound for lower bound."""
    # For k=10, N=20, high=0.6, c=0.8
    result = search_bound(0.6, 10, 20, 0.8, BoundDirection.LOWER)
    assert result < 0.6
    assert result >= 0.0


def test_beta_logpdf() -> None:
    """Test beta_logpdf against scipy.stats.beta.logpdf."""
    k, ntrials = 5, 10
    x = 0.5
    result = beta_logpdf(x, k, ntrials)
    expected = stats.beta.logpdf(x, k + 1, ntrials - k + 1)
    assert result == pytest.approx(expected, abs=1e-10)


def test_beta_pdf() -> None:
    """Test beta_pdf against scipy.stats.beta.pdf."""
    k, ntrials = 3, 8
    x = 0.4
    result = beta_pdf(x, k, ntrials)
    expected = stats.beta.pdf(x, k + 1, ntrials - k + 1)
    assert result == pytest.approx(expected, abs=1e-10)


def test_shortest_hpd_beta() -> None:
    """Test shortest_hpd_beta for correctness."""
    k, ntrials, C = 5, 10, 0.95
    a, b = shortest_hpd_beta(k, ntrials, C)

    # Check bounds
    assert 0 <= a < b <= 1

    # Check mass containment
    from scipy.special import betainc

    alpha = k + 1
    beta_param = ntrials - k + 1
    mass = betainc(alpha, beta_param, b) - betainc(alpha, beta_param, a)
    assert mass == pytest.approx(C, abs=1e-6)

    # Check equal heights (approximately)
    pdf_a = beta_pdf(a, k, ntrials)
    pdf_b = beta_pdf(b, k, ntrials)
    assert pdf_a == pytest.approx(pdf_b, rel=1e-3)


def test_effic_known_values() -> None:
    """Test effic with known values."""
    # Test edge cases
    mode, low, high = effic(0, 10, 0.8)
    assert mode == 0.0
    assert low == 0.0
    assert high > 0

    mode, low, high = effic(10, 10, 0.8)
    assert mode == 1.0
    assert low < 1.0
    assert high == 1.0

    # Normal case with working algorithm
    mode, low, high = effic(8, 10, 0.8)
    assert mode == 0.8
    assert 0 <= low <= mode <= high <= 1


def test_effic_invalid_conflevel() -> None:
    """Test effic with invalid confidence level."""
    with pytest.raises(ValueError):
        effic(5, 10, 0.0)

    with pytest.raises(ValueError):
        effic(5, 10, 1.0)


def test_posterior_density() -> None:
    """Test posterior_density function with known values."""
    # Test Beta(1,2) for k=0, N=1
    # Density f(x) = 2(1-x) for x in [0,1]
    assert posterior_density(0.5, 0, 1) == pytest.approx(1.0, abs=1e-10)
    assert posterior_density(0.25, 0, 1) == pytest.approx(1.5, abs=1e-10)

    # Test Beta(2,1) for k=1, N=1
    # Density f(x) = 2x for x in [0,1]
    assert posterior_density(0.5, 1, 1) == pytest.approx(1.0, abs=1e-10)
    assert posterior_density(0.25, 1, 1) == pytest.approx(0.5, abs=1e-10)

    # Test Beta(1,3) for k=0, N=2
    # Density f(x) = 3(1-x)^2 for x in [0,1]
    assert posterior_density(0.5, 0, 2) == pytest.approx(0.75, abs=1e-10)
    assert posterior_density(0.25, 0, 2) == pytest.approx(
        3 * (0.75) ** 2, abs=1e-10
    )

    # Test Beta(2,2) for k=1, N=2, symmetric
    # Mode at 0.5, density should be maximum there
    density_at_mode = posterior_density(0.5, 1, 2)
    density_at_25 = posterior_density(0.25, 1, 2)
    density_at_75 = posterior_density(0.75, 1, 2)
    assert density_at_mode > density_at_25
    assert density_at_mode > density_at_75
    assert density_at_25 == pytest.approx(density_at_75, abs=1e-10)

    # Test edge cases
    assert posterior_density(0.0, 1, 2) == 0.0
    assert posterior_density(1.0, 1, 2) == 0.0
    assert posterior_density(-0.1, 1, 2) == 0.0
    assert posterior_density(1.1, 1, 2) == 0.0


def test_probability_mass() -> None:
    """Test probability_mass function with edge cases."""
    # Full interval [0, 1] should always be 1
    assert probability_mass(0, 1, 0.0, 1.0) == pytest.approx(1.0, abs=1e-10)
    assert probability_mass(1, 2, 0.0, 1.0) == pytest.approx(1.0, abs=1e-10)
    assert probability_mass(100, 100, 0.0, 1.0) == pytest.approx(
        1.0, abs=1e-10
    )

    # Zero-length interval should be 0
    assert probability_mass(1, 2, 0.4, 0.4) == pytest.approx(0.0, abs=1e-10)
    assert probability_mass(0, 1, 0.0, 0.0) == pytest.approx(0.0, abs=1e-10)
    assert probability_mass(10, 20, 1.0, 1.0) == pytest.approx(0.0, abs=1e-10)

    # Edge case: k=0 (beta distribution with alpha=1)
    result = probability_mass(0, 5, 0.0, 0.5)
    expected = 0.984375  # For beta(1,6), cdf(0.5) = 1 - 0.5^6 = 0.984375
    assert result == pytest.approx(expected, abs=1e-6)

    # Edge case: k=ntrials (beta distribution with beta=1)
    result = probability_mass(5, 5, 0.5, 1.0)
    # For beta(6,1), cdf(0.5) ≈ 0.015625, so mass = 1 - 0.015625 = 0.984375
    expected = 0.984375
    assert result == pytest.approx(expected, abs=1e-6)

    # Test with low=0
    result = probability_mass(1, 2, 0.0, 0.5)
    expected = 0.5  # For beta(2,2), symmetric, cdf(0.5) = 0.5
    assert result == pytest.approx(expected, abs=1e-6)

    # Test with high=1
    result = probability_mass(1, 2, 0.5, 1.0)
    assert result == pytest.approx(0.5, abs=1e-6)

    # Test small interval
    result = probability_mass(1, 2, 0.4, 0.6)
    expected = stats.beta.cdf(0.6, 2, 2) - stats.beta.cdf(0.4, 2, 2)
    assert result == pytest.approx(expected, abs=1e-10)
