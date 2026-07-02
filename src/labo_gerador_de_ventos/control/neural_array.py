from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from ..prompt import parse_prompt


class ThrottleModel(Protocol):
    def predict(self, x: np.ndarray) -> np.ndarray: ...


@dataclass(frozen=True)
class MotorThrottle:
    motor: int
    position: str
    throttle: float


LAYOUTS: dict[str, tuple[str, ...]] = {
    "cross": ("front", "right", "back", "left"),
    "x": ("front-right", "back-right", "back-left", "front-left"),
}


def infer_motor_throttles(
    prompt: str,
    model: ThrottleModel,
    *,
    motor_count: int = 1,
    layout: str = "cross",
    safety_ceiling: float = 1.0,
) -> list[MotorThrottle]:
    if motor_count not in range(1, 5):
        raise ValueError("motor_count must be in 1..4")
    if layout not in LAYOUTS:
        raise ValueError("layout must be 'cross' or 'x'")
    if not 0.0 < safety_ceiling <= 1.0:
        raise ValueError("safety_ceiling must stay within (0, 1]")

    request = parse_prompt(prompt)
    inputs = np.array([[request.mean_mps, request.distance_m]], dtype=float)
    base = float(np.clip(model.predict(inputs)[0], 0.0, safety_ceiling))
    positions = LAYOUTS[layout][:motor_count]
    factors = directional_factors(prompt, positions)
    peak = max(factors) if factors else 1.0
    return [
        MotorThrottle(index + 1, position, float(np.clip(base * factor / peak, 0.0, safety_ceiling)))
        for index, (position, factor) in enumerate(zip(positions, factors))
    ]


def directional_factors(prompt: str, positions: tuple[str, ...]) -> list[float]:
    text = prompt.lower()
    factors = [1.0 for _ in positions]
    direction_keywords = {
        "front": ("front", "frente", "norte"),
        "right": ("right", "direita", "leste"),
        "back": ("back", "trás", "tras", "sul"),
        "left": ("left", "esquerda", "oeste"),
        "front-right": ("front-right", "frente direita", "nordeste"),
        "back-right": ("back-right", "trás direita", "tras direita", "sudeste"),
        "back-left": ("back-left", "trás esquerda", "tras esquerda", "sudoeste"),
        "front-left": ("front-left", "frente esquerda", "noroeste"),
    }
    for index, position in enumerate(positions):
        if any(keyword in text for keyword in direction_keywords.get(position, ())):
            factors[index] = 1.15
    return factors
