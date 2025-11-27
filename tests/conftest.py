import hypothesis.strategies as st
from hypothesis.strategies import DrawFn


@st.composite
def k_n_pair_strategy(draw: DrawFn, nmax: int = 100) -> tuple[int, int]:
    """Generate pairs (k, N) where N is in [1, nmax] and k is in [0, N]."""
    N = draw(st.integers(min_value=1, max_value=nmax))
    k = draw(st.integers(min_value=0, max_value=N))
    return (k, N)
