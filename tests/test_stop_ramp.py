import pytest

from labo_gerador_de_ventos.control import MockMultiMotorActuator, ramp_down_multimotor


def test_multimotor_stop_ramp_descends_to_zero() -> None:
    actuator = MockMultiMotorActuator()
    ramp_down_multimotor(
        actuator,
        {1: 0.6, 2: 0.3},
        duration_s=1.0,
        sample_period_s=0.5,
        real_time=False,
    )

    assert actuator.commands[0] == {1: pytest.approx(0.6), 2: pytest.approx(0.3)}
    assert actuator.commands[1] == {1: pytest.approx(0.3), 2: pytest.approx(0.15)}
    assert actuator.commands[2] == {1: pytest.approx(0.0), 2: pytest.approx(0.0)}
    assert actuator.commands[-1] == {}
