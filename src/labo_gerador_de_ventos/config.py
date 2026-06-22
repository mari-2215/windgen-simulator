from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    sampling_hz: float = 5.0
    duration_s: float = 60.0
    weibull_shape: float = 2.0
    mean_wind_mps: float = 12.0
    gust_mps: float = 18.0
    distance_m: float = 1.5
    seed: int = 42
    throttle_min: float = 0.0
    throttle_max: float = 0.30
    max_delta_per_second: float = 0.08
    actuator_backend: str = "mock"

    def validate(self) -> "Settings":
        if self.sampling_hz <= 0 or self.duration_s <= 0:
            raise ValueError("sampling_hz e duration_s devem ser positivos")
        if self.weibull_shape <= 0 or self.mean_wind_mps < 0 or self.gust_mps < 0:
            raise ValueError("parametros de vento invalidos")
        if not 0 <= self.throttle_min < self.throttle_max <= 1:
            raise ValueError("limites de throttle devem estar em [0, 1]")
        return self

    @classmethod
    def load(cls, path: str | Path) -> "Settings":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8"))).validate()

    def with_overrides(self, **changes: object) -> "Settings":
        values = asdict(self)
        values.update({k: v for k, v in changes.items() if v is not None})
        return Settings(**values).validate()

