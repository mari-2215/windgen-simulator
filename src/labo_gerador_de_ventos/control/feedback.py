from __future__ import annotations


def corrected_throttle(
    *,
    base_throttle: float,
    target_wind_mps: float,
    measured_wind_mps: float,
    kp: float = 0.035,
    ceiling: float = 1.0,
) -> float:
    """Apply a proportional correction using measured wind feedback."""
    if not 0.0 < ceiling <= 1.0:
        raise ValueError("ceiling must stay within (0, 1]")
    error = target_wind_mps - measured_wind_mps
    return min(max(base_throttle + kp * error, 0.0), ceiling)
