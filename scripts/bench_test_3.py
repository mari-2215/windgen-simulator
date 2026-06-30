"""Bench Test 3 planning profile: 2 s ramp up, max-throttle hold, 2 s ramp down."""

from __future__ import annotations

import argparse

from labo_gerador_de_ventos.control import build_bench_test_3_profile, interpolate_profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - Bench Test 3 profile")
    parser.add_argument("--max-throttle", type=float, default=0.60)
    parser.add_argument("--ramp", type=float, default=2.0, help="ramp duration in seconds")
    parser.add_argument("--hold", type=float, default=3.0, help="max-throttle hold duration in seconds")
    parser.add_argument("--sample-period", type=float, default=0.25)
    args = parser.parse_args()

    profile = build_bench_test_3_profile(
        max_throttle=args.max_throttle,
        ramp_s=args.ramp,
        hold_s=args.hold,
    )
    samples = interpolate_profile(profile, sample_period_s=args.sample_period)

    print("Bench Test 3 planned profile")
    print(f"ramp={args.ramp:.2f}s hold={args.hold:.2f}s max_throttle={args.max_throttle:.1%}")
    for point in samples:
        print(f"t={point.time_s:5.2f}s target={point.throttle:6.1%}")


if __name__ == "__main__":
    main()
