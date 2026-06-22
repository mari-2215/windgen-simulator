from __future__ import annotations

from math import gamma

import numpy as np


def scale_from_mean(mean_mps: float, shape: float) -> float:
    if mean_mps < 0 or shape <= 0:
        raise ValueError("mean_mps deve ser >= 0 e shape > 0")
    return mean_mps / gamma(1.0 + 1.0 / shape) if mean_mps else 0.0


def generate_weibull_series(
    mean_mps: float,
    shape: float,
    duration_s: float,
    sampling_hz: float,
    seed: int = 42,
    correlation: float = 0.92,
    gust_mps: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Gera série Weibull com ordem temporal via cópula AR(1) aproximada."""
    if not 0 <= correlation < 1:
        raise ValueError("correlation deve estar em [0, 1)")
    if duration_s <= 0 or sampling_hz <= 0:
        raise ValueError("duração e frequência devem ser positivas")
    count = max(2, int(round(duration_s * sampling_hz)))
    rng = np.random.default_rng(seed)
    raw = rng.weibull(shape, count) * scale_from_mean(mean_mps, shape)
    values = np.empty(count, dtype=float)
    values[0] = raw[0]
    alpha = correlation
    for index in range(1, count):
        values[index] = alpha * values[index - 1] + (1 - alpha) * raw[index]
    current_mean = float(values.mean())
    if current_mean > 0:
        values *= mean_mps / current_mean
    if gust_mps is not None:
        values = np.minimum(values, max(gust_mps, mean_mps))
    time_s = np.arange(count, dtype=float) / sampling_hz
    return time_s, np.maximum(values, 0.0)

