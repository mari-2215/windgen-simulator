"""Bench Test 3: 2 s ramp up, max-throttle hold, 2 s ramp down.

The script supports a mock mode and a guarded motor mode for the laboratory bench.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from labo_gerador_de_ventos.control import (
    BetaflightMSPActuator,
    MockActuator,
    SafetyController,
    build_bench_test_3_profile,
    clear_stop_request,
    interpolate_profile,
    stop_requested,
)


def typed_confirmation(prompt: str, expected: str) -> None:
    answer = input(f"{prompt}\nType exactly {expected}: ").strip()
    if answer != expected:
        raise SystemExit("Cancelled safely: confirmation did not match.")


def confirmations_ready(args: argparse.Namespace) -> bool:
    return bool(
        args.confirm_secured
        and args.confirm_supervision
        and args.confirm_estop
        and (args.max_throttle <= 0.60 or args.allow_full_throttle)
    )


def require_motor_confirmations(args: argparse.Namespace) -> None:
    if confirmations_ready(args):
        return
    print("\nDANGER: Bench Test 3 sends real motor commands.")
    typed_confirmation("The motor is fixed, shielded, and cannot move its mount.", "MOTOR_SECURED")
    typed_confirmation("Laboratory supervision is active.", "SUPERVISION_READY")
    typed_confirmation("A physical emergency disconnect is ready.", "ESTOP_READY")
    if args.max_throttle > 0.60:
        typed_confirmation("Full-throttle operation was approved for this bench.", "FULL_THROTTLE_APPROVED")


def run_profile(
    controller: SafetyController,
    *,
    max_throttle: float,
    ramp_s: float,
    hold_s: float,
    sample_period_s: float,
    real_time: bool,
) -> None:
    profile = build_bench_test_3_profile(
        max_throttle=max_throttle,
        ramp_s=ramp_s,
        hold_s=hold_s,
    )
    points = interpolate_profile(profile, sample_period_s=sample_period_s)
    start = time.monotonic()
    for point in points:
        if real_time and stop_requested():
            print("STOP REQUEST DETECTED. Leaving Bench Test 3 loop.")
            break
        if real_time:
            delay = point.time_s - (time.monotonic() - start)
            if delay > 0:
                time.sleep(delay)
            applied = controller.command(point.throttle)
        else:
            applied = controller.command(point.throttle, now=point.time_s)
        print(f"t={point.time_s:5.2f}s target={point.throttle:6.1%} applied={applied:6.1%}")


def run_mock(args: argparse.Namespace) -> None:
    actuator = MockActuator()
    controller = SafetyController(
        actuator,
        maximum=args.max_throttle,
        max_delta_per_second=args.max_throttle / args.ramp,
    )
    print("Bench Test 3 mock profile")
    print(f"ramp={args.ramp:.2f}s hold={args.hold:.2f}s max_throttle={args.max_throttle:.1%}")
    run_profile(
        controller,
        max_throttle=args.max_throttle,
        ramp_s=args.ramp,
        hold_s=args.hold,
        sample_period_s=args.sample_period,
        real_time=False,
    )
    controller.emergency_stop()
    print("MOCK PASS: profile simulated without hardware output.")


def run_motor(args: argparse.Namespace) -> None:
    if not args.port:
        raise SystemExit("Specify --port for motor mode.")
    if args.max_throttle > 0.60 and not args.allow_full_throttle:
        raise SystemExit("Throttle above 60% requires --allow-full-throttle.")
    require_motor_confirmations(args)
    clear_stop_request()

    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPActuator.ENABLE_TOKEN
    actuator = BetaflightMSPActuator(args.port, baudrate=args.baudrate, motor_index=args.motor - 1)
    controller = SafetyController(
        actuator,
        maximum=args.max_throttle,
        max_delta_per_second=args.max_throttle / args.ramp,
    )
    print("Bench Test 3 MOTOR RUN")
    print(
        f"motor={args.motor} port={args.port} ramp={args.ramp:.2f}s "
        f"hold={args.hold:.2f}s max_throttle={args.max_throttle:.1%}"
    )
    try:
        actuator.stop()
        run_profile(
            controller,
            max_throttle=args.max_throttle,
            ramp_s=args.ramp,
            hold_s=args.hold,
            sample_period_s=args.sample_period,
            real_time=True,
        )
        controller.ramp_to(0.0, step_interval_s=args.sample_period, timeout_s=max(args.ramp + 2.0, 4.0))
    except KeyboardInterrupt:
        print("\nInterrupted by operator.")
        controller.emergency_stop()
    finally:
        time.sleep(0.2)
        actuator.stop()
        actuator.close()
        print("STOP SENT. Disconnect motor power before approaching the bench.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - Bench Test 3")
    parser.add_argument("--mode", choices=("mock", "motor"), default="mock")
    parser.add_argument("--port", help="Linux example: /dev/ttyACM0; Windows example: COM5")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--motor", type=int, choices=range(1, 9), default=1)
    parser.add_argument("--max-throttle", type=float, default=0.60)
    parser.add_argument("--ramp", type=float, default=2.0, help="ramp duration in seconds")
    parser.add_argument("--hold", type=float, default=3.0, help="max-throttle hold duration in seconds")
    parser.add_argument("--sample-period", type=float, default=0.25)
    parser.add_argument("--allow-full-throttle", action="store_true")
    parser.add_argument("--confirm-secured", action="store_true")
    parser.add_argument("--confirm-supervision", action="store_true")
    parser.add_argument("--confirm-estop", action="store_true")
    args = parser.parse_args()

    if not 0.0 < args.max_throttle <= 1.0:
        raise SystemExit("--max-throttle must stay within (0, 1].")
    if args.ramp <= 0.0 or args.hold <= 0.0 or args.sample_period <= 0.0:
        raise SystemExit("--ramp, --hold, and --sample-period must be positive.")

    if args.mode == "mock":
        run_mock(args)
    else:
        run_motor(args)


if __name__ == "__main__":
    try:
        main()
    except (PermissionError, TimeoutError, RuntimeError, OSError) as error:
        print(f"FAIL SAFE: {error}", file=sys.stderr)
        raise SystemExit(2) from error
