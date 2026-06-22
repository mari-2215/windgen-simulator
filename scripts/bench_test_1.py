"""Bench Test 1 for Raspberry Pi + SpeedyBee F405 V4, safe by default.

Run mock first, then serial-check with ESC power disconnected. Motor mode is experimental and
requires three typed confirmations. Never run the initial test with a propeller installed.
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
    infer_safe_throttle,
    probe_betaflight,
)
from labo_gerador_de_ventos.models.mlp import build_default_model


def available_ports() -> list[str]:
    try:
        from serial.tools import list_ports
    except ImportError:
        return []
    return [port.device for port in list_ports.comports()]


def require_port(value: str | None) -> str:
    if value:
        return value
    ports = available_ports()
    if len(ports) == 1:
        print(f"Using detected serial port: {ports[0]}")
        return ports[0]
    visible = ", ".join(ports) if ports else "none"
    raise SystemExit(f"Specify --port. Detected ports: {visible}")


def run_mock() -> None:
    actuator = MockActuator()
    controller = SafetyController(actuator, maximum=0.10, max_delta_per_second=0.05)
    print("MOCK: checking ramp 0% -> 10% -> 0% (no hardware output)")
    for second, target in enumerate((0.0, 0.05, 0.10, 0.10, 0.05, 0.0)):
        applied = controller.command(target, now=float(second))
        print(f"t={second}s target={target:5.1%} applied={applied:5.1%}")
    controller.emergency_stop()
    print("MOCK PASS: safety ramp and emergency stop executed.")


def run_serial_check(port: str, baudrate: int) -> None:
    print("READ-ONLY CHECK: keep ESC power disconnected; USB to the F405 is enough.")
    protocol, major, minor = probe_betaflight(port, baudrate)
    print(f"SERIAL PASS: MSP protocol={protocol}, API={major}.{minor}, port={port}")


def calculate_neural_command(prompt: str, safety_ceiling: float):
    print("Loading the lightweight MLP and interpreting the prompt...")
    model = build_default_model(seed=42, epochs=600)
    command = infer_safe_throttle(prompt, model, safety_ceiling=safety_ceiling)
    print(
        "NEURAL COMMAND: "
        f"wind={command.request.mean_mps:.2f} m/s, "
        f"distance={command.request.distance_m:.2f} m, "
        f"raw MLP={command.raw_throttle:.1%}, "
        f"Bench Test 1 limit={command.limited_throttle:.1%}"
    )
    return command


def typed_confirmation(prompt: str, expected: str) -> None:
    answer = input(f"{prompt}\nType exactly {expected}: ").strip()
    if answer != expected:
        raise SystemExit("Cancelled safely: confirmation did not match.")


def run_motor(port: str, baudrate: int, motor: int, maximum: float, duration_s: float) -> None:
    if maximum > 0.10 or duration_s > 10:
        raise SystemExit("Phase 1 limits: maximum throttle 10% and duration 10 seconds.")
    print("\nDANGER: experimental physical output. The software cannot verify the bench visually.")
    typed_confirmation("The propeller is physically removed.", "PROPELLER_REMOVED")
    typed_confirmation("The motor is fixed and cannot jump or rotate its mount.", "MOTOR_SECURED")
    typed_confirmation("Power limiting and a physical emergency disconnect are ready.", "ESTOP_READY")

    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPActuator.ENABLE_TOKEN
    actuator = BetaflightMSPActuator(port, baudrate=baudrate, motor_index=motor - 1)
    controller = SafetyController(actuator, maximum=maximum, max_delta_per_second=0.04)
    start = time.monotonic()
    print(f"Starting motor {motor}: ramping to {maximum:.1%} for at most {duration_s:.1f}s")
    try:
        actuator.stop()
        while True:
            elapsed = time.monotonic() - start
            if elapsed >= duration_s:
                break
            applied = controller.command(maximum)
            print(f"\rElapsed {elapsed:4.1f}s | command {applied:5.1%}", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nInterrupted by operator.")
    finally:
        controller.emergency_stop()
        time.sleep(0.2)
        actuator.stop()
        actuator.close()
        print("\nSTOP SENT. Disconnect motor power before approaching the bench.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - Bench Test 1")
    parser.add_argument(
        "--mode",
        choices=("mock", "neural-mock", "serial-check", "motor", "neural-motor"),
        default="mock",
    )
    parser.add_argument("--port", help="Linux example: /dev/ttyACM0; Windows example: COM5")
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--motor", type=int, choices=range(1, 9), default=1)
    parser.add_argument("--max-throttle", type=float, default=0.08)
    parser.add_argument("--duration", type=float, default=3.0)
    parser.add_argument(
        "--prompt",
        default="vento offshore de 6 m/s por 3 s a 1 m",
        help="wind scenario used by neural-mock and neural-motor",
    )
    args = parser.parse_args()

    if args.mode == "mock":
        run_mock()
        return
    if args.mode == "neural-mock":
        calculate_neural_command(args.prompt, min(args.max_throttle, 0.10))
        print("NEURAL MOCK PASS: no hardware output was generated.")
        return
    port = require_port(args.port)
    if args.mode == "serial-check":
        run_serial_check(port, args.baudrate)
    elif args.mode == "motor":
        run_motor(port, args.baudrate, args.motor, args.max_throttle, args.duration)
    else:
        command = calculate_neural_command(args.prompt, min(args.max_throttle, 0.10))
        run_motor(
            port,
            args.baudrate,
            args.motor,
            command.limited_throttle,
            args.duration,
        )


if __name__ == "__main__":
    try:
        main()
    except (PermissionError, TimeoutError, RuntimeError, OSError) as error:
        print(f"FAIL SAFE: {error}", file=sys.stderr)
        raise SystemExit(2) from error
