import numpy as np
import pytest

from labo_gerador_de_ventos.control import infer_motor_throttles


class FixedModel:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, x: np.ndarray) -> np.ndarray:
        return np.array([self.value])


def test_neural_array_allocates_four_cross_motors() -> None:
    commands = infer_motor_throttles(
        "vento offshore de 12 m/s por 10 min a 1 m",
        FixedModel(0.70),
        motor_count=4,
        layout="cross",
        safety_ceiling=1.0,
    )
    assert [command.motor for command in commands] == [1, 2, 3, 4]
    assert [command.position for command in commands] == ["front", "right", "back", "left"]
    assert all(command.throttle == pytest.approx(0.70) for command in commands)


def test_neural_array_respects_safety_ceiling() -> None:
    commands = infer_motor_throttles(
        "vento forte de frente por 10 min a 1 m",
        FixedModel(0.95),
        motor_count=1,
        layout="cross",
        safety_ceiling=0.50,
    )
    assert commands[0].throttle == pytest.approx(0.50)


def test_neural_array_rejects_invalid_layout() -> None:
    with pytest.raises(ValueError):
        infer_motor_throttles("vento de 8 m/s", FixedModel(0.3), layout="circle")
