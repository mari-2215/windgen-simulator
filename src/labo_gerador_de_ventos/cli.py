from __future__ import annotations

import argparse

from .service import run_prompt


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab")
    sub = parser.add_subparsers(dest="command", required=True)
    simulate = sub.add_parser("simulate", help="gera série, CSV e gráfico")
    simulate.add_argument("--prompt", required=True)
    simulate.add_argument("--output", default="artifacts")
    simulate.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.command == "simulate":
        result = run_prompt(args.prompt, args.output, seed=args.seed)
        print(f"CSV: {result['csv']}")
        print(f"Gráfico: {result['plot']}")


if __name__ == "__main__":
    main()
