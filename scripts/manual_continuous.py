"""Continuous manual wind command controlled by the Streamlit app.

The app writes a small JSON command file.  This process owns the serial port and
stops the motors if the command is disabled or its heartbeat becomes stale.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

from labo_gerador_de_ventos.control import BetaflightMSPMultiMotorActuator
from labo_gerador_de_ventos.models.mlp import build_default_model


def read_command(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError) as error:
        raise RuntimeError(f"invalid manual-control command file: {error}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("manual-control command must be a JSON object")
    return payload


def requested_throttle(model: object, wind_mps: float, distance_m: float, ceiling: float) -> float:
    if wind_mps < 0.0:
        raise ValueError("wind_mps must be non-negative")
    if distance_m <= 0.0:
        raise ValueError("distance_m must be positive")
    predicted = float(model.predict(np.array([[wind_mps, distance_m]], dtype=float))[0])
    return min(max(predicted, 0.0), ceiling)


def ramp_value(current: float, target: float, rate_per_second: float, elapsed_s: float) -> float:
    step = max(rate_per_second, 0.0) * max(elapsed_s, 0.0)
    if target > current:
        return min(current + step, target)
    return max(current - step, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuous manual wind control")
    parser.add_argument("--port", required=True)
    parser.add_argument("--command-file", type=Path, required=True)
    parser.add_argument("--motor-count", type=int, choices=range(1, 5), default=1)
    parser.add_argument("--max-throttle", type=float, default=1.0)
    parser.add_argument("--sample-period", type=float, default=0.10)
    parser.add_argument("--ramp-seconds", type=float, default=3.0)
    parser.add_argument("--heartbeat-timeout", type=float, default=30.0)
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=600)
    args = parser.parse_args()

    if not 0.0 < args.max_throttle <= 1.0:
        raise SystemExit("--max-throttle must stay within (0, 1]")
    if args.sample_period <= 0.0 or args.ramp_seconds <= 0.0 or args.heartbeat_timeout <= 0.0:
        raise SystemExit("timing values must be positive")

    model = build_default_model(seed=args.seed, epochs=args.epochs)
    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPMultiMotorActuator.ENABLE_TOKEN
    actuator = BetaflightMSPMultiMotorActuator(args.port, baudrate=args.baudrate)
    throttle = 0.0
    ramp_rate = args.max_throttle / args.ramp_seconds
    previous = time.monotonic()

    print("Manual continuous control ready.", flush=True)
    try:
        actuator.stop()
        while True:
            now = time.monotonic()
            elapsed = now - previous
            previous = now
            command = read_command(args.command_file)
            heartbeat = float(command.get("heartbeat", 0.0))
            active = bool(command.get("active", False))
            stale = time.time() - heartbeat > args.heartbeat_timeout

            if not active or stale:
                reason = "command disabled" if not active else "app heartbeat expired"
                print(f"STOP: {reason}; applying ramp down.", flush=True)
                while throttle > 0.0:
                    throttle = ramp_value(throttle, 0.0, ramp_rate, args.sample_period)
                    actuator.set_throttles({motor: throttle for motor in range(1, args.motor_count + 1)})
                    time.sleep(args.sample_period)
                break

            wind_mps = float(command["wind_mps"])
            distance_m = float(command["distance_m"])
            target = requested_throttle(model, wind_mps, distance_m, args.max_throttle)
            throttle = ramp_value(throttle, target, ramp_rate, elapsed)
            actuator.set_throttles({motor: throttle for motor in range(1, args.motor_count + 1)})
            print(
                f"wind_target={wind_mps:.2f} m/s distance={distance_m:.2f} m "
                f"target_throttle={target:.1%} applied={throttle:.1%}",
                flush=True,
            )
            time.sleep(args.sample_period)
    except KeyboardInterrupt:
        print("Interrupted by operator.", flush=True)
    finally:
        actuator.stop()
        time.sleep(0.2)
        actuator.stop()
        actuator.close()
        print("STOP SENT. Manual continuous control finished.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (KeyError, PermissionError, TimeoutError, RuntimeError, ValueError, OSError) as error:
        print(f"FAIL SAFE: {error}", file=sys.stderr, flush=True)
        raise SystemExit(2) from error
