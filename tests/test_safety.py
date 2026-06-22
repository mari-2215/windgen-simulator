import pytest

from labo_gerador_de_ventos.control import MockActuator, SafetyController


def test_controller_starts_at_minimum_and_limits_ramp() -> None:
    actuator = MockActuator()
    controller = SafetyController(actuator, maximum=0.3, max_delta_per_second=0.1)
    assert controller.command(0.3, now=0.0) == 0.0
    assert controller.command(0.3, now=1.0) == pytest.approx(0.1)
    assert controller.command(0.8, now=2.0) == pytest.approx(0.2)
    controller.emergency_stop()
    assert actuator.commands[-1] == 0.0

