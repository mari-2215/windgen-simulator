import pytest

from labo_gerador_de_ventos.control import BENCH_TEST_2_PROFILE, interpolate_profile


def test_bench_test_2_profile_contains_requested_gradient() -> None:
    throttles = [point.throttle for point in BENCH_TEST_2_PROFILE]
    assert 0.10 in throttles
    assert 0.60 in throttles
    assert 0.25 in throttles
    assert throttles[-1] == 0.0


def test_interpolate_profile_samples_endpoints() -> None:
    samples = interpolate_profile(BENCH_TEST_2_PROFILE, sample_period_s=1.0)
    assert samples[0].time_s == 0.0
    assert samples[0].throttle == 0.0
    assert samples[-1] == BENCH_TEST_2_PROFILE[-1]
    assert max(point.throttle for point in samples) == pytest.approx(0.60)
