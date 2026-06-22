import numpy as np
import pytest

from labo_gerador_de_ventos.control import infer_safe_throttle


class FixedModel:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, x: np.ndarray) -> np.ndarray:
        assert x.shape == (1, 2)
        return np.array([self.value])


def test_neural_command_parses_prompt_and_limits_output() -> None:
    command = infer_safe_throttle(
        "vento de 8 m/s por 3 s a 1.5 m", FixedModel(0.72), safety_ceiling=0.08
    )
    assert command.request.mean_mps == 8
    assert command.request.distance_m == pytest.approx(1.5)
    assert command.raw_throttle == pytest.approx(0.72)
    assert command.limited_throttle == pytest.approx(0.08)


def test_neural_command_rejects_unsafe_ceiling() -> None:
    with pytest.raises(ValueError):
        infer_safe_throttle("vento de 8 m/s", FixedModel(0.2), safety_ceiling=0.11)

