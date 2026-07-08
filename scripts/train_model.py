from __future__ import annotations

import argparse
from pathlib import Path

from labo_gerador_de_ventos.io import load_calibration_csv
from labo_gerador_de_ventos.models.mlp import TinyMLP, synthetic_calibration_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="CSV com wind_mps,distance_m,throttle")
    parser.add_argument("--output", default="artifacts/mlp_model.npz")
    parser.add_argument("--epochs", type=int, default=1500)
    parser.add_argument("--hidden-layers", default="32,24,12")
    parser.add_argument("--learning-rate", type=float, default=0.008)
    args = parser.parse_args()
    x, y = load_calibration_csv(args.data) if args.data else synthetic_calibration_data()
    hidden_layers = tuple(int(item.strip()) for item in args.hidden_layers.split(",") if item.strip())
    model = TinyMLP(hidden_layers=hidden_layers)
    history = model.fit(x, y, epochs=args.epochs, learning_rate=args.learning_rate)
    model.save(Path(args.output))
    print(
        f"Modelo salvo em {args.output}; "
        f"perda final={history.losses[-1]:.6f}; "
        f"validação={history.validation_losses[-1]:.6f}"
    )


if __name__ == "__main__":
    main()
