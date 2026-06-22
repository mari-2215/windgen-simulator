from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_wind_plot(frame: pd.DataFrame, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(frame["time_s"], frame["wind_target_mps"], color="#007f86", linewidth=1.4)
    ax.axhline(frame["wind_target_mps"].mean(), color="#ef8354", linestyle="--", label="média")
    ax.set(title="Série temporal de vento", xlabel="Tempo (s)", ylabel="Velocidade (m/s)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(target, dpi=160)
    plt.close(fig)
    return target

