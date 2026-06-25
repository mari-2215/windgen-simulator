"""Bench Test 2 gradient profile for one brushless motor.

The default mode is mock. Physical output is intentionally guarded because the planned profile
contains a 60% throttle plateau.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from labo_gerador_de_ventos.control import (
    BENCH_TEST_2_PROFILE,
    BetaflightMSPActuator,
    ControlPoint,
    MockActuator,
    SafetyController,
    interpolate_profile,
)


def typed_confirmation(prompt: str, expected: str) -> None:
    answer = input(f"{prompt}\nType exactly {expected}: ").strip()
    if answer != expected:
        raise SystemExit("Cancelled safely: confirmation did not match.")


def run_profile(
    points: list[ControlPoint],
    controller: SafetyController,
    *,
    real_time: bool,
    sample_period_s: float,
) -> None:
    start = time.monotonic()
    for point in points:
        if real_time:
            delay = point.time_s - (time.monotonic() - start)
            if delay > 0:
                time.sleep(delay)
            applied = controller.command(point.throttle)
        else:
            applied = controller.command(point.throttle, now=point.time_s)
        print(f"t={point.time_s:5.2f}s target={point.throttle:6.1%} applied={applied:6.1%}")
    if real_time:
        controller.ramp_to(0.0, step_interval_s=sample_period_s, timeout_s=10.0)
    else:
        controller.command(0.0, now=points[-1].time_s + sample_period_s)


def run_mock(sample_period_s: float) -> None:
    actuator = MockActuator()
    controller = SafetyController(actuator, maximum=0.60, max_delta_per_second=0.20)
    points = interpolate_profile(BENCH_TEST_2_PROFILE, sample_period_s=sample_period_s)
    print("MOCK: Bench Test 2 gradient profile 0% -> 10% -> 60% -> 25% -> 0%")
    run_profile(points, controller, real_time=False, sample_period_s=sample_period_s)
    controller.emergency_stop()
    print("MOCK PASS: gradient profile and final stop were simulated.")


def run_motor(port: str, baudrate: int, motor: int, sample_period_s: float, allow_high_throttle: bool) -> None:
    if not allow_high_throttle:
        raise SystemExit("Bench Test 2 hardware mode requires --allow-high-throttle.")

    print("\nDANGER: Bench Test 2 reaches 60% throttle. This is not a first-spin procedure.")
    typed_confirmation("The propeller is physically removed.", "PROPELLER_REMOVED")
    typed_confirmation("The motor is fixed, shielded, and cannot move its mount.", "MOTOR_SECURED")
    typed_confirmation("Power limiting and a physical emergency disconnect are ready.", "ESTOP_READY")
    typed_confirmation("Bench Test 1 has already passed and the 60% plateau was approved.", "BENCH_TEST_2_APPROVED")

    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPActuator.ENABLE_TOKEN
    actuator = BetaflightMSPActuator(port, baudrate=baudrate, motor_index=motor - 1)
    controller = SafetyController(actuator, maximum=0.60, max_delta_per_second=0.20)
    points = interpolate_profile(BENCH_TEST_2_PROFILE, sample_period_s=sample_period_s)
    try:
        actuator.stop()
        run_profile(points, controller, real_time=True, sample_period_s=sample_period_s)
    except KeyboardInterrupt:
        print("\nInterrupted by operator.")
        controller.emergency_stop()
    finally:
        actuator.stop()
        actuator.close()
        print("STOP SENT. Disconnect motor power before approaching the bench.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - Bench Test 2 gradient")
    parser.add_argument("--mode", choices=("mock", "motor"), default="mock")
    parser.add_argument("--port", help="Linux example: /dev/ttyACM0; Windows example: COM5")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--motor", type=int, choices=range(1, 9), default=1)
    parser.add_argument("--sample-period", type=float, default=0.25)
    parser.add_argument("--allow-high-throttle", action="store_true")
    args = parser.parse_args()

    if args.mode == "mock":
        run_mock(args.sample_period)
        return
    if not args.port:
        raise SystemExit("Specify --port for motor mode.")
    run_motor(args.port, args.baudrate, args.motor, args.sample_period, args.allow_high_throttle)


if __name__ == "__main__":
    try:
        main()
    except (PermissionError, TimeoutError, RuntimeError, OSError) as error:
        print(f"FAIL SAFE: {error}", file=sys.stderr)
        raise SystemExit(2) from error
