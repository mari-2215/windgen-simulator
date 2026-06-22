from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_csv(frame: pd.DataFrame, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False, float_format="%.6f")
    return target


def load_calibration_csv(path: str | Path) -> tuple[object, object]:
    frame = pd.read_csv(path)
    required = {"wind_mps", "distance_m", "throttle"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"colunas ausentes: {sorted(missing)}")
    return frame[["wind_mps", "distance_m"]].to_numpy(), frame["throttle"].to_numpy()

