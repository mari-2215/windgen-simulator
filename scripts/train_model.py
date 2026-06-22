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
    args = parser.parse_args()
    x, y = load_calibration_csv(args.data) if args.data else synthetic_calibration_data()
    model = TinyMLP()
    history = model.fit(x, y, epochs=args.epochs)
    model.save(Path(args.output))
    print(f"Modelo salvo em {args.output}; perda final={history.losses[-1]:.6f}")


if __name__ == "__main__":
    main()

