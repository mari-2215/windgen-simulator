from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class WindReading:
    wind_mps: float
    source: str
    timestamp_s: float


class WindSensor(Protocol):
    def read(self) -> WindReading: ...
    def close(self) -> None: ...


class SimulatedWindSensor:
    """First-order simulated wind feedback for dry runs without an external anemometer."""

    def __init__(self, response_gain: float = 18.0, alpha: float = 0.25) -> None:
        self.response_gain = response_gain
        self.alpha = alpha
        self._wind_mps = 0.0
        self._throttle = 0.0

    def update_throttle(self, throttle: float) -> None:
        self._throttle = min(max(float(throttle), 0.0), 1.0)

    def read(self) -> WindReading:
        target = self.response_gain * self._throttle
        self._wind_mps = (1.0 - self.alpha) * self._wind_mps + self.alpha * target
        return WindReading(self._wind_mps, "simulated", time.monotonic())

    def close(self) -> None:
        return None


class SerialAnemometer:
    """Read wind speed from a serial line containing one numeric value in m/s."""

    def __init__(self, port: str, baudrate: int = 9600, timeout_s: float = 0.2) -> None:
        import serial

        self.serial = serial.Serial(port, baudrate=baudrate, timeout=timeout_s)

    def read(self) -> WindReading:
        line = self.serial.readline().decode("utf-8", errors="ignore").strip()
        match = re.search(r"[-+]?\d+(?:[.,]\d+)?", line)
        if not match:
            raise RuntimeError(f"invalid anemometer line: {line!r}")
        wind_mps = float(match.group(0).replace(",", "."))
        return WindReading(wind_mps, "serial-anemometer", time.monotonic())

    def close(self) -> None:
        self.serial.close()
