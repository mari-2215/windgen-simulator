from __future__ import annotations

from pathlib import Path

from .io import export_csv
from .models.mlp import TinyMLP, build_default_model
from .prompt import parse_prompt
from .simulation import simulate
from .visualization import save_wind_plot


def run_prompt(
    prompt: str,
    output_dir: str | Path = "artifacts",
    model: TinyMLP | None = None,
    sampling_hz: float = 5.0,
    seed: int = 42,
) -> dict[str, object]:
    request = parse_prompt(prompt)
    model = model or build_default_model(seed=seed)
    frame = simulate(request, model, sampling_hz=sampling_hz, seed=seed)
    output_dir = Path(output_dir)
    csv_path = export_csv(frame, output_dir / "wind_series.csv")
    plot_path = save_wind_plot(frame, output_dir / "wind_series.png")
    return {"request": request, "frame": frame, "csv": csv_path, "plot": plot_path}

