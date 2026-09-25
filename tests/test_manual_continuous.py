import pytest

from scripts.manual_continuous import (
    motor_commands,
    parse_motor_outputs,
    ramp_value,
    requested_throttle,
)


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


def test_four_motor_outputs_receive_the_same_throttle() -> None:
    outputs = parse_motor_outputs("1,2,3,4")
    assert outputs == (1, 2, 3, 4)
    assert motor_commands(outputs, 0.35) == {1: 0.35, 2: 0.35, 3: 0.35, 4: 0.35}


@pytest.mark.parametrize("value", ["", "1,1", "0,1", "1,9", "one,two"])
def test_invalid_motor_outputs_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        parse_motor_outputs(value)
