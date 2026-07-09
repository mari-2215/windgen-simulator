"""Bench Test 5: neural command with current wind-speed feedback."""

from __future__ import annotations

import argparse
import os
import sys
import time

from labo_gerador_de_ventos.control import BetaflightMSPMultiMotorActuator, MockMultiMotorActuator
from labo_gerador_de_ventos.control.feedback import corrected_throttle
from labo_gerador_de_ventos.control.neural_array import infer_motor_throttles
from labo_gerador_de_ventos.models.mlp import build_default_model
from labo_gerador_de_ventos.prompt import parse_prompt
from labo_gerador_de_ventos.sensors import SerialAnemometer, SimulatedWindSensor


def typed_confirmation(prompt: str, expected: str) -> None:
    answer = input(f"{prompt}\nType exactly {expected}: ").strip()
    if answer != expected:
        raise SystemExit("Cancelled safely: confirmation did not match.")


def require_motor_confirmations(args: argparse.Namespace) -> None:
    ready = args.confirm_secured and args.confirm_supervision and args.confirm_estop
    if ready:
        return
    print("\nDANGER: Bench Test 5 sends feedback-corrected motor commands.")
    typed_confirmation("The motor array is fixed, shielded, and supervised.", "MOTOR_ARRAY_SECURED")
    typed_confirmation("Laboratory supervision is active.", "SUPERVISION_READY")
    typed_confirmation("A physical emergency disconnect is ready.", "ESTOP_READY")


def build_sensor(args: argparse.Namespace):
    if args.wind_source == "serial":
        if not args.wind_port:
            raise SystemExit("--wind-port is required when --wind-source serial")
        return SerialAnemometer(args.wind_port, baudrate=args.wind_baudrate)
    return SimulatedWindSensor(response_gain=args.simulated_wind_gain)


def run_loop(args: argparse.Namespace, *, actuator: object, real_time: bool) -> None:
    request = parse_prompt(args.prompt)
    if request.mean_mps > args.motor_wind_limit:
        raise SystemExit(
            f"Target wind {request.mean_mps:.2f} m/s exceeds motor bench limit "
            f"{args.motor_wind_limit:.2f} m/s."
        )
    model = build_default_model(seed=args.seed, epochs=args.epochs)
    base_commands = infer_motor_throttles(
        args.prompt,
        model,
        motor_count=args.motor_count,
        layout=args.layout,
        safety_ceiling=args.max_throttle,
    )
    target_wind = request.mean_mps
    base_mean = sum(command.throttle for command in base_commands) / len(base_commands)
    sensor = build_sensor(args)
    print("Bench Test 5 neural feedback")
    print(
        f"target_wind={target_wind:.2f} m/s wind_source={args.wind_source} "
        f"base_mean_throttle={base_mean:.1%}"
    )
    try:
        start = time.monotonic()
        step = 0
        total_s = args.ramp + args.duration + args.ramp
        while True:
            elapsed = time.monotonic() - start if real_time else step * args.sample_period
            if elapsed > total_s:
                break
            if elapsed < args.ramp:
                ramp_factor = elapsed / args.ramp
            elif elapsed < args.ramp + args.duration:
                ramp_factor = 1.0
            else:
                ramp_factor = max(0.0, 1.0 - (elapsed - args.ramp - args.duration) / args.ramp)
            reading = sensor.read()
            corrected_mean = corrected_throttle(
                base_throttle=base_mean,
                target_wind_mps=target_wind,
                measured_wind_mps=reading.wind_mps,
                kp=args.kp,
                ceiling=args.max_throttle,
            )
            scale = 0.0 if base_mean <= 0 else corrected_mean / base_mean
            values = {
                command.motor: min(command.throttle * scale * ramp_factor, args.max_throttle)
                for command in base_commands
            }
            actuator.set_throttles(values)
            if hasattr(sensor, "update_throttle"):
                sensor.update_throttle(sum(values.values()) / len(values))
            values_text = " ".join(f"M{motor}={value:5.1%}" for motor, value in sorted(values.items()))
            print(
                f"t={elapsed:7.2f}s wind={reading.wind_mps:6.2f} m/s ramp={ramp_factor:4.2f} "
                f"target={target_wind:5.2f} m/s corrected={corrected_mean:5.1%} {values_text}"
            )
            step += 1
            if real_time:
                next_time = step * args.sample_period
                delay = next_time - (time.monotonic() - start)
                if delay > 0:
                    time.sleep(delay)
    finally:
        actuator.stop()
        sensor.close()


def run_mock(args: argparse.Namespace) -> None:
    actuator = MockMultiMotorActuator()
    run_loop(args, actuator=actuator, real_time=False)
    print("MOCK PASS: feedback loop simulated without hardware output.")


def run_motor(args: argparse.Namespace) -> None:
    if not args.port:
        raise SystemExit("Specify --port for motor mode.")
    require_motor_confirmations(args)
    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPMultiMotorActuator.ENABLE_TOKEN
    actuator = BetaflightMSPMultiMotorActuator(args.port, baudrate=args.baudrate)
    try:
        actuator.stop()
        run_loop(args, actuator=actuator, real_time=True)
    except KeyboardInterrupt:
        print("\nInterrupted by operator.")
        actuator.stop()
    finally:
        time.sleep(0.2)
        actuator.stop()
        actuator.close()
        print("STOP SENT. Feedback test finished.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - Bench Test 5")
    parser.add_argument("--mode", choices=("mock", "motor"), default="mock")
    parser.add_argument("--prompt", default="vento offshore de 12 m/s por 60 s a 1 m")
    parser.add_argument("--layout", choices=("cross", "x"), default="cross")
    parser.add_argument("--motor-count", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--max-throttle", type=float, default=1.0)
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--ramp", type=float, default=2.0)
    parser.add_argument("--sample-period", type=float, default=0.05)
    parser.add_argument("--kp", type=float, default=0.035)
    parser.add_argument("--motor-wind-limit", type=float, default=19.0)
    parser.add_argument("--wind-source", choices=("simulated", "serial"), default="simulated")
    parser.add_argument("--wind-port")
    parser.add_argument("--wind-baudrate", type=int, default=9600)
    parser.add_argument("--simulated-wind-gain", type=float, default=18.0)
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
