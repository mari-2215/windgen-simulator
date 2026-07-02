import pytest

from labo_gerador_de_ventos.control import (
    MockMultiMotorActuator,
    build_msp_v1_frame,
    read_msp_v1_response,
)


class FakeSerial:
    def __init__(self, data: bytes) -> None:
        self.data = bytearray(data)

    def read(self, size: int) -> bytes:
        result = bytes(self.data[:size])
        del self.data[:size]
        return result


def response(command: int, payload: bytes) -> bytes:
    checksum = len(payload) ^ command
    for byte in payload:
        checksum ^= byte
    return b"$M>" + bytes((len(payload), command)) + payload + bytes((checksum,))


def test_build_msp_api_version_request() -> None:
    assert build_msp_v1_frame(1) == b"$M<\x00\x01\x01"


def test_read_msp_response() -> None:
    payload = b"\x00\x01\x2e"
    assert read_msp_v1_response(FakeSerial(b"noise" + response(1, payload)), 1) == payload


def test_bad_checksum_fails() -> None:
    with pytest.raises(RuntimeError, match="checksum"):
        read_msp_v1_response(FakeSerial(b"$M>\x00\x01\x00"), 1)


def test_mock_multi_motor_actuator_records_mapping() -> None:
    actuator = MockMultiMotorActuator()
    actuator.set_throttles({1: 0.5, 4: 0.25})
    actuator.stop()
    assert actuator.commands[0] == {1: 0.5, 4: 0.25}
    assert actuator.commands[-1] == {}
