from __future__ import annotations

import numpy as np
import pandas as pd

from .models.mlp import TinyMLP
from .models.weibull import generate_weibull_series
from .prompt import WindRequest


def simulate(request: WindRequest, model: TinyMLP, sampling_hz: float = 5.0, seed: int = 42) -> pd.DataFrame:
    time_s, wind = generate_weibull_series(
        request.mean_mps, request.shape, request.duration_s, sampling_hz, seed,
        gust_mps=request.gust_mps,
    )
    inputs = np.column_stack((wind, np.full_like(wind, request.distance_m)))
    throttle = np.clip(model.predict(inputs), 0.0, 1.0)
    return pd.DataFrame(
        {"time_s": time_s, "wind_target_mps": wind, "distance_m": request.distance_m,
         "throttle_model": throttle}
    )

