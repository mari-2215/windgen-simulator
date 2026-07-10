from __future__ import annotations

import time


def ramp_down_multimotor(
    actuator: object,
    current_values: dict[int, float],
    *,
    duration_s: float,
    sample_period_s: float,
    real_time: bool,
    label: str = "STOP RAMP",
) -> None:
    """Ramp a multi-motor actuator from the last command to zero.

    The function is intentionally small and deterministic in mock mode, so the same
    logic can be exercised by automated tests and reused by real bench scripts.
    """
    duration_s = max(float(duration_s), float(sample_period_s))
    sample_period_s = max(float(sample_period_s), 0.01)
    current_values = {int(motor): max(float(value), 0.0) for motor, value in current_values.items()}

    start = time.monotonic()
    step = 0
    while True:
        elapsed = time.monotonic() - start if real_time else step * sample_period_s
        factor = max(0.0, 1.0 - elapsed / duration_s)
        values = {motor: value * factor for motor, value in current_values.items()}
        actuator.set_throttles(values)
        values_text = " ".join(f"M{motor}={value:5.1%}" for motor, value in sorted(values.items()))
        print(f"{label} t={elapsed:6.2f}s factor={factor:4.2f} {values_text}")
        if factor <= 0.0:
            break
        step += 1
        if real_time:
            next_time = step * sample_period_s
            delay = next_time - (time.monotonic() - start)
            if delay > 0:
                time.sleep(delay)
    actuator.stop()
