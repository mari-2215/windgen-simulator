"""Send an immediate MSP motor stop command to the SpeedyBee/Betaflight stack."""

from __future__ import annotations

import argparse
import os
import sys

from labo_gerador_de_ventos.control import BetaflightMSPMultiMotorActuator


def main() -> None:
    parser = argparse.ArgumentParser(description="Neural Offshore Wind Lab - emergency motor stop")
    parser.add_argument("--port", required=True)
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--confirm-stop", action="store_true")
    args = parser.parse_args()
    if not args.confirm_stop:
        raise SystemExit("Emergency stop requires --confirm-stop.")
    os.environ["LABO_HARDWARE_ENABLE"] = BetaflightMSPMultiMotorActuator.ENABLE_TOKEN
    actuator = BetaflightMSPMultiMotorActuator(args.port, baudrate=args.baudrate)
    try:
        actuator.stop()
        print("STOP SENT.")
    finally:
        actuator.close()


if __name__ == "__main__":
    try:
        main()
    except (PermissionError, TimeoutError, RuntimeError, OSError) as error:
        print(f"FAIL SAFE: {error}", file=sys.stderr)
        raise SystemExit(2) from error
