from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ControlPoint:
    """Timestamped throttle target used by bench-test profiles."""

    time_s: float
    throttle: float


BENCH_TEST_2_PROFILE: tuple[ControlPoint, ...] = (
    ControlPoint(0.0, 0.00),
    ControlPoint(3.0, 0.10),
    ControlPoint(6.0, 0.10),
    ControlPoint(10.0, 0.60),
    ControlPoint(13.0, 0.60),
    ControlPoint(16.0, 0.25),
    ControlPoint(19.0, 0.25),
    ControlPoint(22.0, 0.00),
)


def interpolate_profile(
    points: tuple[ControlPoint, ...],
    *,
    sample_period_s: float = 0.25,
) -> list[ControlPoint]:
    """Sample a piecewise-linear throttle profile."""
    if len(points) < 2:
        raise ValueError("at least two control points are required")
    if sample_period_s <= 0:
        raise ValueError("sample_period_s must be positive")
    if any(next_point.time_s <= point.time_s for point, next_point in zip(points, points[1:])):
        raise ValueError("control points must be strictly increasing")
    if any(not 0.0 <= point.throttle <= 1.0 for point in points):
        raise ValueError("throttle values must stay within [0, 1]")

    samples: list[ControlPoint] = []
    for point, next_point in zip(points, points[1:]):
        duration = next_point.time_s - point.time_s
        steps = max(int(round(duration / sample_period_s)), 1)
        for index in range(steps):
            time_s = point.time_s + index * duration / steps
            fraction = (time_s - point.time_s) / duration
            throttle = point.throttle + fraction * (next_point.throttle - point.throttle)
            samples.append(ControlPoint(round(time_s, 6), throttle))
    samples.append(points[-1])
    return samples
