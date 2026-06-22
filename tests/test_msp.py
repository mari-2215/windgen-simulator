import pytest

from labo_gerador_de_ventos.control import build_msp_v1_frame, read_msp_v1_response


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

