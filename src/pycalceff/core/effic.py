"""
Bayesian efficiency calculation module.

This module provides functions for calculating exact binomial efficiency
confidence intervals using Bayesian methods with beta distributions.
Functions are translated from C++ implementations for numerical accuracy.
"""

from collections.abc import Callable
from functools import partial
from typing import Any, Protocol, cast

from scipy import stats
from scipy.optimize import bisect, brenth, brentq, ridder, toms748
from scipy.special import betainc


class RootFinder(Protocol):
    """
    Protocol for root-finding functions like scipy.optimize.brentq,
    bisect, brenth, ridder, and toms748.
    """

    def __call__(
        self,
        f: Callable[[float], float],
        a: float,
        b: float,
        args: tuple[Any, ...] = (),
        xtol: float = 2e-12,
        rtol: float = 4.4408920985006262e-16,
        maxiter: int = 100,
        full_output: bool = False,
        disp: bool = True,
    ) -> float: ...


DEFAULT_ROOT_FINDER_BRENTQ = cast(RootFinder, brentq)
DEFAULT_ROOT_FINDER_BISECT = cast(RootFinder, bisect)
DEFAULT_ROOT_FINDER_BRENTH = cast(RootFinder, brenth)
DEFAULT_ROOT_FINDER_RIDDER = cast(RootFinder, ridder)
DEFAULT_ROOT_FINDER_TOMS748 = cast(RootFinder, partial(toms748, k=1))
DEFAULT_ROOT_FINDER = DEFAULT_ROOT_FINDER_BRENTQ


def posterior_density(x: float, k: int, ntrials: int) -> float:
    """
    Compute the posterior density of the beta distribution
    Beta(k+1, N-k+1) at point x.

    :param x: Point at which to evaluate the density (0 < x < 1)
    :param k: Number of successes
    :param ntrials: Number of trials
    :returns: The density value at x
    """
    if not (0 < x < 1):
        return 0.0
    alpha = k + 1
    beta = ntrials - k + 1
    return float(stats.beta.pdf(x, alpha, beta))


def probability_mass(k: int, ntrials: int, low: float, high: float) -> float:
    """
    Calculate the probability mass (integrated density) of the posterior
    beta distribution Beta(k+1, N-k+1) between low and high.

    :param k: Number of successes
    :param ntrials: Number of trials
    :param low: Lower bound of the interval (0 ≤ low < high ≤ 1)
    :param high: Upper bound of the interval (0 < low < high ≤ 1)
    :returns: Probability mass between low and high
    """
    alpha = k + 1
    beta = ntrials - k + 1
    return float(
        stats.beta.cdf(high, alpha, beta) - stats.beta.cdf(low, alpha, beta)
    )


def compute_hpd_interval_k_zero(
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
) -> tuple[float, float]:
    """
    Compute the highest posterior density (HPD) interval for the case k=0.

    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :returns: Tuple of (low, high) bounds of the HPD interval
    """
    low = 0.0
    high = searchupper(low, 0, ntrials, conflevel, root_finder)
    return low, high


def compute_hpd_interval_k_ntrials(
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
) -> tuple[float, float]:
    """
    Compute the highest posterior density (HPD) interval
    for the case k=ntrials.

    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :returns: Tuple of (low, high) bounds of the HPD interval
    """
    high = 1.0
    low = searchlower(high, ntrials, ntrials, conflevel, root_finder)
    return low, high


def compute_hpd_interval_general(
    k: int,
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
) -> tuple[float, float]:
    """
    Compute the highest posterior density (HPD) interval
    for 0 < k < ntrials.

    :param k: Number of successes
    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :returns: Tuple of (low, high) bounds of the HPD interval
    """
    assert 0 < k < ntrials, "k must be between 0 and ntrials"
    # Find the mode
    mode = k / ntrials

    # Use root_finder to find h such that the mass above h equals conflevel
    def mass_diff(h: float) -> float:
        def f(x: float) -> float:
            return posterior_density(x, k, ntrials) - h

        a = root_finder(f, 0, mode, xtol=1e-14)
        b = root_finder(f, mode, 1, xtol=1e-14)
        mass = beta_ab(a, b, k, ntrials)
        return mass - conflevel

    h = float(root_finder(mass_diff, 0.0, posterior_density(mode, k, ntrials)))

    # Find the roots with the converged h
    def g(x: float) -> float:
        return posterior_density(x, k, ntrials) - h

    a = root_finder(g, 0, mode, xtol=1e-14)
    b = root_finder(g, mode, 1, xtol=1e-14)
    return a, b


def compute_hpd_interval(
    k: int,
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
) -> tuple[float, float]:
    """
    Compute the highest posterior density (HPD) interval
    for the beta posterior.

    :param k: Number of successes
    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :returns: Tuple of (low, high) bounds of the HPD interval
    """
    if k == 0:
        return compute_hpd_interval_k_zero(ntrials, conflevel, root_finder)
    elif k == ntrials:
        return compute_hpd_interval_k_ntrials(ntrials, conflevel, root_finder)
    else:
        return compute_hpd_interval_general(k, ntrials, conflevel, root_finder)


def beta_ab(a: float, b: float, k: int, N: int) -> float:
    """
    Calculate the fraction of the area under the beta distribution
    x^k * (1-x)^(N-k) between x=a and x=b.

    :param a: Lower bound of the interval
    :param b: Upper bound of the interval
    :param k: Number of successes
    :param N: Number of trials
    :returns: The fraction of the area under the beta distribution
    """
    if a == b:
        return 0.0
    c1 = k + 1
    c2 = N - k + 1
    return float(betainc(c1, c2, b) - betainc(c1, c2, a))


def searchupper(
    low: float,
    k: int,
    numtrials: int,
    c: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER_BISECT,
) -> float:
    """
    Find the upper edge of the integration region starting at low
    that contains probability content c.

    :param low: Lower bound of the search interval
    :param k: Number of successes
    :param numtrials: Number of trials
    :param c: Probability content
    :param root_finder: Root-finding algorithm to use (default: bisect)
    :returns: The upper edge of the interval
    """
    integral = beta_ab(low, 1.0, k, numtrials)
    if integral == c:
        return 1.0
    if integral < c:
        raise ValueError(
            f"Cannot find upper bound: insufficient mass from {low} to 1.0 "
            f"(integral={integral}, required={c})"
        )

    # Use root_finder for root finding
    def func(x: float) -> float:
        return beta_ab(low, x, k, numtrials) - c

    try:
        return float(root_finder(func, low, 1.0, xtol=1e-12))
    except ValueError:
        raise ValueError(
            f"Bisection failed for upper bound search from {low} to 1.0"
        ) from None


def searchlower(
    high: float,
    k: int,
    ntrials: int,
    c: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER_BISECT,
) -> float:
    """
    Find the lower edge of the integration region ending at high
    that contains probability content c.

    :param high: Upper bound of the search interval
    :param k: Number of successes
    :param ntrials: Number of trials
    :param c: Probability content
    :param root_finder: Root-finding algorithm to use (default: bisect)
    :returns: The lower edge of the interval
    """
    integral = beta_ab(0.0, high, k, ntrials)
    if integral == c:
        return 0.0
    if integral < c:
        raise ValueError(
            f"Cannot find lower bound: insufficient mass from 0.0 to {high} "
            f"(integral={integral}, required={c})"
        )

    # Use root_finder for root finding
    def func(x: float) -> float:
        return beta_ab(x, high, k, ntrials) - c

    try:
        return float(root_finder(func, 0.0, high, xtol=1e-12))
    except ValueError:
        raise ValueError(
            f"Bisection failed for lower bound search from 0.0 to {high}"
        ) from None


def interval(low: float, k: int, N: int, conflevel: float) -> float:
    """
    Return the length of the interval starting at low that contains
    conflevel of the beta distribution.

    :param low: Starting point of the interval
    :param k: Number of successes
    :param N: Number of trials
    :param conflevel: Confidence level
    :returns: The length of the interval
    """
    high = searchupper(low, k, N, conflevel, DEFAULT_ROOT_FINDER_BISECT)
    return high - low


def effic(
    k: int,
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
) -> tuple[float, float, float]:
    """
    Calculate the Bayesian efficiency: mode and confidence interval.

    :param k: Number of successes
    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :returns: A tuple of (mode, low, high) where mode is the most probable
        efficiency, low and high are the bounds of the confidence interval
    :raises ValueError: If conflevel is not between 0 and 1
    """
    if not (0 < conflevel < 1):
        raise ValueError("conflevel must be between 0 and 1")

    # Most probable value
    mode = k / ntrials

    # Highest posterior density interval
    if k == 0:
        low, high = compute_hpd_interval(k, ntrials, conflevel, root_finder)
    elif k == ntrials:
        low, high = compute_hpd_interval(k, ntrials, conflevel, root_finder)
    else:
        low, high = compute_hpd_interval(k, ntrials, conflevel, root_finder)

    # Clamp bounds to [0, 1] (should not be necessary)
    low = max(0.0, low)
    high = min(1.0, high)

    return mode, low, high
