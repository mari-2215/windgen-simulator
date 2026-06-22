from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from ..prompt import WindRequest, parse_prompt


class ThrottleModel(Protocol):
    def predict(self, x: np.ndarray) -> np.ndarray: ...


@dataclass(frozen=True)
class NeuralThrottleCommand:
    request: WindRequest
    raw_throttle: float
    limited_throttle: float
    safety_ceiling: float


def infer_safe_throttle(
    prompt: str, model: ThrottleModel, safety_ceiling: float = 0.10
) -> NeuralThrottleCommand:
    """Converts a prompt into an MLP command and applies the independent bench ceiling."""
    if not 0 < safety_ceiling <= 0.10:
        raise ValueError("Bench Test 1 safety ceiling must be in (0, 0.10]")
    request = parse_prompt(prompt)
    inputs = np.array([[request.mean_mps, request.distance_m]], dtype=float)
    raw = float(np.clip(model.predict(inputs)[0], 0.0, 1.0))
    return NeuralThrottleCommand(request, raw, min(raw, safety_ceiling), safety_ceiling)

