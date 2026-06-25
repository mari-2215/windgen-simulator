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


def test_controller_limits_downward_ramp_before_stop() -> None:
    actuator = MockActuator()
    controller = SafetyController(actuator, maximum=0.3, max_delta_per_second=0.1)
    controller.command(0.3, now=0.0)
    controller.command(0.3, now=3.0)
    assert controller.current == pytest.approx(0.3)
    assert controller.command(0.0, now=4.0) == pytest.approx(0.2)
    assert controller.command(0.0, now=5.0) == pytest.approx(0.1)
    assert controller.command(0.0, now=6.0) == pytest.approx(0.0)
