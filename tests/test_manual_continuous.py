import pytest

from scripts.manual_continuous import ramp_value, requested_throttle


class FixedModel:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, inputs):
        return [self.value]


def test_requested_throttle_respects_ceiling() -> None:
    assert requested_throttle(FixedModel(0.8), 5.0, 1.0, 0.6) == pytest.approx(0.6)


def test_requested_throttle_validates_physical_inputs() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        requested_throttle(FixedModel(0.5), -1.0, 1.0, 1.0)
    with pytest.raises(ValueError, match="positive"):
        requested_throttle(FixedModel(0.5), 1.0, 0.0, 1.0)


def test_ramp_value_moves_both_directions_without_overshoot() -> None:
    assert ramp_value(0.2, 0.8, 0.1, 2.0) == pytest.approx(0.4)
    assert ramp_value(0.8, 0.2, 0.1, 2.0) == pytest.approx(0.6)
    assert ramp_value(0.2, 0.25, 0.1, 2.0) == pytest.approx(0.25)
