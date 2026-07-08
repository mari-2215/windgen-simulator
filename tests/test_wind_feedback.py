import pytest

from labo_gerador_de_ventos.control.feedback import corrected_throttle
from labo_gerador_de_ventos.sensors import SimulatedWindSensor


def test_corrected_throttle_increases_when_wind_is_below_target() -> None:
    value = corrected_throttle(
        base_throttle=0.4,
        target_wind_mps=12.0,
        measured_wind_mps=8.0,
        kp=0.05,
        ceiling=1.0,
    )
    assert value == pytest.approx(0.6)


def test_corrected_throttle_respects_ceiling() -> None:
    value = corrected_throttle(
        base_throttle=0.9,
        target_wind_mps=20.0,
        measured_wind_mps=0.0,
        kp=0.05,
        ceiling=1.0,
    )
    assert value == 1.0


def test_simulated_wind_sensor_tracks_throttle() -> None:
    sensor = SimulatedWindSensor(response_gain=10.0, alpha=1.0)
    sensor.update_throttle(0.6)
    reading = sensor.read()
    assert reading.wind_mps == pytest.approx(6.0)
    assert reading.source == "simulated"
