from __future__ import annotations

import os
import struct
import time
from dataclasses import dataclass
from typing import Protocol


class Actuator(Protocol):
    def set_throttle(self, value: float) -> None: ...
    def stop(self) -> None: ...


class MockActuator:
    def __init__(self) -> None:
        self.commands: list[float] = []

    def set_throttle(self, value: float) -> None:
        self.commands.append(float(value))

    def stop(self) -> None:
        self.commands.append(0.0)


def build_msp_v1_frame(command: int, payload: bytes = b"") -> bytes:
    """Build a host-to-flight-controller MSP v1 frame."""
    if not 0 <= command <= 255 or len(payload) > 255:
        raise ValueError("MSP v1 command and payload must fit in one byte")
    checksum = len(payload) ^ command
    for byte in payload:
        checksum ^= byte
    return b"$M<" + bytes((len(payload), command)) + payload + bytes((checksum,))


def read_msp_v1_response(serial_port: object, expected_command: int, timeout_s: float = 1.0) -> bytes:
    """Read and validate one MSP v1 response, ignoring unrelated leading bytes."""
    deadline = time.monotonic() + timeout_s
    window = bytearray()
    while time.monotonic() < deadline:
        byte = serial_port.read(1)
        if not byte:
            continue
        window.extend(byte)
        if len(window) > 3:
            del window[:-3]
        if bytes(window) not in (b"$M>", b"$M!"):
            continue
        is_error = bytes(window) == b"$M!"
        header = serial_port.read(2)
        if len(header) != 2:
            break
        size, command = header
        payload = serial_port.read(size)
        checksum_bytes = serial_port.read(1)
        if len(payload) != size or len(checksum_bytes) != 1:
            break
        checksum = size ^ command
        for item in payload:
            checksum ^= item
        if checksum != checksum_bytes[0]:
            raise RuntimeError("invalid MSP checksum")
        if is_error:
            raise RuntimeError(f"flight controller rejected MSP command {command}")
        if command == expected_command:
            return payload
        window.clear()
    raise TimeoutError(f"no valid MSP response for command {expected_command}")


def probe_betaflight(port: str, baudrate: int = 115200) -> tuple[int, int, int]:
    """Read-only MSP_API_VERSION probe; it never sends a motor command."""
    import serial

    with serial.Serial(port, baudrate=baudrate, timeout=0.1) as serial_port:
        serial_port.reset_input_buffer()
        serial_port.write(build_msp_v1_frame(1))  # MSP_API_VERSION
        serial_port.flush()
        payload = read_msp_v1_response(serial_port, expected_command=1)
    if len(payload) < 3:
        raise RuntimeError("unexpected MSP_API_VERSION payload")
    return payload[0], payload[1], payload[2]


class BetaflightMSPActuator:
    """Backend experimental MSP v1; exige validação local da versão do firmware."""

    MSP_SET_MOTOR = 214
    ENABLE_TOKEN = "EU_CONFIRMO_BANCADA_SEGURA"

    def __init__(self, port: str, baudrate: int = 115200, motor_index: int = 0) -> None:
        if os.getenv("LABO_HARDWARE_ENABLE") != self.ENABLE_TOKEN:
            raise PermissionError("hardware bloqueado; liberação descrita em docs/hardware.md")
        import serial

        if motor_index not in range(8):
            raise ValueError("motor_index deve estar entre 0 e 7")
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.2)
        self.motor_index = motor_index

    def _send(self, command: int, payload: bytes) -> None:
        self.serial.write(build_msp_v1_frame(command, payload))
        self.serial.flush()

    def set_throttle(self, value: float) -> None:
        value = min(max(float(value), 0.0), 1.0)
        motors = [1000] * 8
        motors[self.motor_index] = int(round(1000 + 1000 * value))
        self._send(self.MSP_SET_MOTOR, struct.pack("<8H", *motors))

    def stop(self) -> None:
        self._send(self.MSP_SET_MOTOR, struct.pack("<8H", *([1000] * 8)))

    def close(self) -> None:
        self.serial.close()


@dataclass
class SafetyController:
    actuator: Actuator
    minimum: float = 0.0
    maximum: float = 0.30
    max_delta_per_second: float = 0.08
    _last: float = 0.0
    _last_time: float | None = None

    def command(self, requested: float, now: float | None = None) -> float:
        now = time.monotonic() if now is None else now
        requested = min(max(float(requested), self.minimum), self.maximum)
        if self._last_time is None:
            applied = min(requested, self.minimum)
        else:
            allowed = self.max_delta_per_second * max(now - self._last_time, 0.0)
            applied = min(max(requested, self._last - allowed), self._last + allowed)
        self.actuator.set_throttle(applied)
        self._last, self._last_time = applied, now
        return applied

    def emergency_stop(self) -> None:
        self.actuator.stop()
        self._last = 0.0
        self._last_time = None
