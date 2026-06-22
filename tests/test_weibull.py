import numpy as np
import pytest

from labo_gerador_de_ventos.models.weibull import generate_weibull_series, scale_from_mean


def test_scale_matches_mean() -> None:
    rng = np.random.default_rng(10)
    samples = rng.weibull(2.0, 200_000) * scale_from_mean(12.0, 2.0)
    assert samples.mean() == pytest.approx(12.0, rel=0.01)


def test_series_is_reproducible_and_bounded() -> None:
    t1, v1 = generate_weibull_series(10, 2, 10, 5, seed=7, gust_mps=14)
    t2, v2 = generate_weibull_series(10, 2, 10, 5, seed=7, gust_mps=14)
    assert np.array_equal(t1, t2)
    assert np.array_equal(v1, v2)
    assert len(v1) == 50
    assert v1.max() <= 14

