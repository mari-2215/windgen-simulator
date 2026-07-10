"""Bench Test 4: neural prompt command, endurance run, and multi-motor layout planning."""

from __future__ import annotations

import argparse
import os
import sys
import time

from labo_gerador_de_ventos.control import (
    BetaflightMSPMultiMotorActuator,
    MockMultiMotorActuator,
    clear_stop_request,
    infer_motor_throttles,
    stop_requested,
)
from labo_gerador_de_ventos.models.mlp import build_default_model


def typed_confirmation(prompt: str, expected: str) -> None:
    answer = input(f"{prompt}\nType exactly {expected}: ").strip()
    if answer != expected:
        raise SystemExit("Cancelled safely: confirmation did not match.")


def target_map(args: argparse.Namespace) -> dict[int, float]:
    model = build_default_model(seed=args.seed, epochs=args.epochs)
    commands = infer_motor_throttles(
        args.prompt,
        model,
        motor_count=args.motor_count,
        layout=args.layout,
        safety_ceiling=args.max_throttle,
    )
    print("Neural motor allocation")
    for command in commands:
        print(f"M{command.motor} position={command.position:>11} target={command.throttle:6.1%}")
    return {command.motor: command.throttle for command in commands}


def scaled_targets(targets: dict[int, float], factor: float) -> dict[int, float]:
    return {motor: throttle * factor for motor, throttle in targets.items()}


def run_profile(actuator: object, targets: dict[int, float], args: argparse.Namespace, *, real_time: bool) -> None:
    total_s = args.ramp + args.duration + args.ramp
    start = time.monotonic()
    step = 0
    while True:
        elapsed = time.monotonic() - start if real_time else step * args.sample_period
        if elapsed > total_s:
            break
        if real_time and stop_requested():
            print("STOP REQUEST DETECTED. Leaving Bench Test 4 loop.")
            break
        if elapsed < args.ramp:
            factor = elapsed / args.ramp
        elif elapsed < args.ramp + args.duration:
            factor = 1.0
        else:
            factor = max(0.0, 1.0 - (elapsed - args.ramp - args.duration) / args.ramp)
        values = scaled_targets(targets, factor)
        actuator.set_throttles(values)
        values_text = " ".join(f"M{motor}={value:5.1%}" for motor, value in sorted(values.items()))
        print(f"t={elapsed:7.2f}s {values_text}")
        step += 1
        if real_time:
            next_time = step * args.sample_period
            delay = next_time - (time.monotonic() - start)
            if delay > 0:
                time.sleep(delay)
    actuator.stop()


def require_motor_confirmations(args: argparse.Namespace) -> None:
    ready = args.confirm_secured and args.confirm_supervision and args.confirm_estop
    if ready:
        return
    print("\nDANGER: Bench Test 4 is an endurance motor run.")
    typed_confirmation("The motor array is fixed, shielded, and supervised.", "MOTOR_ARRAY_SECURED")
    typed_confirmation("Laboratory supervision is active.", "SUPERVISION_READY")
    typed_confirmation("A physical emergency disconnect is ready.", "ESTOP_READY")


def run_mock(args: argparse.Namespace) -> None:
    actuator = MockMultiMotorActuator()
    targets = target_map(args)
    print(f"Bench Test 4 MOCK: duration={args.duration:.1f}s ramp={args.ramp:.1f}s")
    run_profile(actuator, targets, args, real_time=False)
    print("MOCK PASS: neural endurance profile simulated without hardware output.")


def run_motor(args: argparse.Namespace) -> None:
    if not args.port:
        raise SystemExit("Specify --port for motor mode.")
    require_motor_confirmations(args)
    clear_stop_request()
    targets = target_map(args)
    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPMultiMotorActuator.ENABLE_TOKEN
    actuator = BetaflightMSPMultiMotorActuator(args.port, baudrate=args.baudrate)
    print(f"Bench Test 4 MOTOR RUN: duration={args.duration:.1f}s ramp={args.ramp:.1f}s")
    try:
        actuator.stop()
        run_profile(actuator, targets, args, real_time=True)
    except KeyboardInterrupt:
        print("\nInterrupted by operator.")
        actuator.stop()
    finally:
        time.sleep(0.2)
        actuator.stop()
        actuator.close()
        print("STOP SENT. Record RPM/temperature notes and disconnect power when safe.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - Bench Test 4")
    parser.add_argument("--mode", choices=("mock", "motor"), default="mock")
    parser.add_argument("--prompt", default="vento offshore de 12 m/s por 10 min a 1 m")
    parser.add_argument("--layout", choices=("cross", "x"), default="cross")
    parser.add_argument("--motor-count", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--max-throttle", type=float, default=1.0)
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--ramp", type=float, default=2.0)
    parser.add_argument("--sample-period", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=600)
    parser.add_argument("--port")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--confirm-secured", action="store_true")
    parser.add_argument("--confirm-supervision", action="store_true")
    parser.add_argument("--confirm-estop", action="store_true")
    args = parser.parse_args()

    if not 0.0 < args.max_throttle <= 1.0:
        raise SystemExit("--max-throttle must stay within (0, 1].")
    if args.duration <= 0.0 or args.ramp <= 0.0 or args.sample_period <= 0.0:
        raise SystemExit("--duration, --ramp, and --sample-period must be positive.")

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
