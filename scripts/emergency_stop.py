"""Send an immediate MSP motor stop command to the SpeedyBee/Betaflight stack."""

from __future__ import annotations

import argparse
import os
import sys
import time

from labo_gerador_de_ventos.control import BetaflightMSPMultiMotorActuator, request_stop


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - emergency motor stop")
    parser.add_argument("--port", required=True)
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--hold", type=float, default=2.0)
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument("--confirm-stop", action="store_true")
    args = parser.parse_args()
    if not args.confirm_stop:
        raise SystemExit("Emergency stop requires --confirm-stop.")
    path = request_stop("manual emergency stop")
    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPMultiMotorActuator.ENABLE_TOKEN
    actuator = BetaflightMSPMultiMotorActuator(args.port, baudrate=args.baudrate)
    try:
        deadline = time.monotonic() + max(args.hold, 0.1)
        count = 0
        while time.monotonic() < deadline:
            actuator.stop()
            count += 1
            time.sleep(max(args.interval, 0.01))
        actuator.stop()
        print(f"STOP LATCHED at {path}. STOP frames sent={count + 1}.")
    finally:
        actuator.close()


if __name__ == "__main__":
    try:
        main()
    except (PermissionError, TimeoutError, RuntimeError, OSError) as error:
        print(f"FAIL SAFE: {error}", file=sys.stderr)
        raise SystemExit(2) from error
