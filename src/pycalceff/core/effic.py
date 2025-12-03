"""
Bayesian efficiency calculation module.

This module provides functions for calculating exact binomial efficiency
confidence intervals using Bayesian methods with beta distributions.
"""

from collections.abc import Callable
from enum import Enum
from functools import partial
from typing import Any, Protocol, cast

import numpy as np
from scipy import stats
from scipy.optimize import bisect, brenth, brentq, ridder, toms748
from scipy.special import betainc, betaincinv, betaln


class BoundDirection(Enum):
    UPPER = "upper"
    LOWER = "lower"


class HPDAlgorithm(Enum):
    ROOT_FINDING = "root_finding"
    BINARY_SEARCH = "binary_search"


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

    :param x: Point at which to evaluate the density (0 ≤ x ≤ 1)
    :param k: Number of successes
    :param ntrials: Number of trials
    :returns: The density value at x
    """
    if not (0 <= x <= 1):
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
    :param low: Lower bound of the interval (0 ≤ low < high ≤<1)
    :param high: Upper bound of the interval (0 ≤ low < high ≤ 1)
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
    high = search_bound(
        low, 0, ntrials, conflevel, BoundDirection.UPPER, root_finder
    )
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
    low = search_bound(
        high, ntrials, ntrials, conflevel, BoundDirection.LOWER, root_finder
    )
    return low, high


def compute_hpd_interval_general(
    k: int,
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
) -> tuple[float, float]:
    """
    Compute the highest posterior density (HPD) interval
    for 0 < k < ntrials. Note the strict inequality.

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
    algorithm: HPDAlgorithm = HPDAlgorithm.BINARY_SEARCH,
) -> tuple[float, float]:
    """
    Compute the highest posterior density (HPD) interval
    for the beta posterior.

    :param k: Number of successes
    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :param algorithm: HPD interval algorithm to use
        (default: BINARY_SEARCH)
    :returns: Tuple of (low, high) bounds of the HPD interval
    """
    if k == 0:
        return compute_hpd_interval_k_zero(ntrials, conflevel, root_finder)
    elif k == ntrials:
        return compute_hpd_interval_k_ntrials(ntrials, conflevel, root_finder)
    else:
        if algorithm == HPDAlgorithm.ROOT_FINDING:
            return compute_hpd_interval_general(
                k, ntrials, conflevel, root_finder
            )
        else:  # BINARY_SEARCH
            a, b = shortest_hpd_beta(k, ntrials, conflevel)
            return a, b


def beta_ab(a: float, b: float, k: int, ntrials: int) -> float:
    """
    Calculate the fraction of the area under the beta distribution
    x^k * (1-x)^(N-k) between x=a and x=b.

    :param a: Lower bound of the interval
    :param b: Upper bound of the interval
    :param k: Number of successes
    :param ntrials: Number of trials
    :returns: The fraction of the area under the beta distribution
    """
    if a == b:
        return 0.0
    c1 = k + 1
    c2 = ntrials - k + 1
    return float(betainc(c1, c2, b) - betainc(c1, c2, a))


def search_bound(
    bound: float,
    k: int,
    ntrials: int,
    conflevel: float,
    direction: BoundDirection,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER_BISECT,
) -> float:
    """
    Find the boundary (upper or lower) of the integration region that contains
    probability content conflevel, starting/ending at the given bound.

    :param bound: The fixed bound (low for upper search, high for lower search)
    :param k: Number of successes
    :param ntrials: Number of trials
    :param conflevel: Probability content
    :param direction: Direction of search (UPPER or LOWER)
    :param root_finder: Root-finding algorithm to use (default: bisect)
    :returns: The boundary value
    """
    if direction == BoundDirection.UPPER:
        integral = beta_ab(bound, 1.0, k, ntrials)
        if integral == conflevel:
            return 1.0
        if integral < conflevel:
            raise ValueError(
                "Cannot find upper bound: insufficient mass from "
                f"{bound} to 1.0 (integral={integral}, required={conflevel})"
            )

        def func(x: float) -> float:
            return beta_ab(bound, x, k, ntrials) - conflevel

        a, b = bound, 1.0
        error_msg = (
            f"Bisection failed for upper bound search from {bound} to 1.0"
        )
    elif direction == BoundDirection.LOWER:
        integral = beta_ab(0.0, bound, k, ntrials)
        if integral == conflevel:
            return 0.0
        if integral < conflevel:
            raise ValueError(
                "Cannot find lower bound: insufficient mass from "
                f"0.0 to {bound} (integral={integral}, required={conflevel})"
            )

        def func(x: float) -> float:
            return beta_ab(x, bound, k, ntrials) - conflevel

        a, b = 0.0, bound
        error_msg = (
            f"Bisection failed for lower bound search from 0.0 to {bound}"
        )
    else:
        raise ValueError("Invalid direction")

    try:
        return float(root_finder(func, a, b, xtol=1e-12))
    except ValueError:
        raise ValueError(error_msg) from None


def beta_logpdf(x: float, k: int, ntrials: int) -> float:
    """
    Compute the log probability density function of the Beta distribution.

    This is numerically stable for small x or 1-x.

    :param x: Point at which to evaluate the PDF (0 < x < 1)
    :param k: Number of successes (k >= 0)
    :param ntrials: Number of trials (ntrials >= max(1,k))
    :returns: The log PDF value at x
    """
    alpha = k + 1
    beta_param = ntrials - k + 1
    log_pdf = (
        (alpha - 1) * np.log(x)
        + (beta_param - 1) * np.log(1 - x)
        - betaln(alpha, beta_param)
    )
    return float(log_pdf)


def beta_pdf(x: float, k: int, ntrials: int) -> float:
    """
    Compute the probability density function of the Beta distribution.

    :param x: Point at which to evaluate the PDF (0 < x < 1)
    :param k: Number of successes (k >= 0)
    :param ntrials: Number of trials (ntrials >= max(1,k))
    :returns: The PDF value at x
    """
    return float(np.exp(beta_logpdf(x, k, ntrials)))


def shortest_hpd_beta(
    k: int, ntrials: int, conflevel: float, tol: float = 2e-12
) -> tuple[float, float]:
    """
    Find the shortest HPD interval for the posterior Beta distribution
    given k successes in ntrials.

    The HPD interval is the shortest interval containing a specified
    probability mass conflevel. It uses the equal-height condition where the PDF
    values at both endpoints are equal.

    Based on: Hyndman, R. J. (1996). Computing and graphing highest density
    regions.
    The American Statistician, 50(2), 120-126.

    :param k: Number of successes (k >= 0)
    :param ntrials: Number of trials (ntrials >= max(1,k))(
    :param conflevel: Probability mass to contain in the interval (0 < conflevel < 1)
    :param tol: Tolerance for the binary search convergence
    :returns: Tuple (a, b) where a, b are the bounds of the HPD interval
    """
    alpha = k + 1
    beta_param = ntrials - k + 1

    # Mode of the posterior Beta distribution
    mode = k / ntrials

    def equal_height_equation(a: float) -> float:
        """
        Equation for equal height: solve beta_pdf(a) = beta_pdf(b)
        where F(b) = F(a) + conflevel.

        :param a: Lower bound candidate
        :returns: Difference in log PDF values (should be 0 for equal height)
        """
        # b such that CDF(b) - CDF(a) = conflevel
        Fa = betainc(alpha, beta_param, a)
        Fb_target = Fa + conflevel
        if Fb_target > 1:
            return 1.0  # Boundary case

        # Invert CDF to find b
        b = float(betaincinv(alpha, beta_param, Fb_target))

        # Equal height condition: pdf(a) = pdf(b)
        return beta_logpdf(a, k, ntrials) - beta_logpdf(b, k, ntrials)

    # Binary search for a in [0, mode]
    a_left, a_right = 0.0, mode
    while a_right - a_left > tol:
        a_mid = (a_left + a_right) / 2
        if equal_height_equation(a_mid) > 0:
            a_right = a_mid
        else:
            a_left = a_mid

    a_opt = (a_left + a_right) / 2
    Fa = betainc(alpha, beta_param, a_opt)
    b_opt = float(betaincinv(alpha, beta_param, Fa + conflevel))

    return a_opt, b_opt


def effic(
    k: int,
    ntrials: int,
    conflevel: float,
    root_finder: RootFinder = DEFAULT_ROOT_FINDER,
    algorithm: HPDAlgorithm = HPDAlgorithm.BINARY_SEARCH,
) -> tuple[float, float, float]:
    """
    Calculate the Bayesian efficiency: mode and confidence interval.

    :param k: Number of successes
    :param ntrials: Number of trials
    :param conflevel: Confidence level (0 < conflevel < 1)
    :param root_finder: Root-finding algorithm to use (default: brentq)
    :param algorithm: HPD interval algorithm to use
        (default: BINARY_SEARCH)
    :returns: A tuple of (mode, low, high) where mode is the most probable
        efficiency, low and high are the bounds of the confidence interval
    :raises ValueError: If conflevel is not between 0 and 1
    """
    if not (0 < conflevel < 1):
        raise ValueError("conflevel must be between 0 and 1")

    # Most probable value
    mode = k / ntrials

    # Highest posterior density interval
    low, high = compute_hpd_interval(
        k, ntrials, conflevel, root_finder, algorithm
    )

    return mode, low, high
