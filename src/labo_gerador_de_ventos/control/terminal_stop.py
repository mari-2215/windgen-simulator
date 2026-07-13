from __future__ import annotations

import os
import select
import sys
from types import TracebackType


class StopKeyWatcher:
    """Non-blocking terminal key watcher for smooth bench stops.

    Pressing `p` requests an operational ramp-down. This is intentionally separate
    from Ctrl+C, which remains an interruption/fail-safe path.
    """

    def __init__(self, key: str = "p") -> None:
        self.key = key.lower()
        self._old_termios: object | None = None

    def __enter__(self) -> "StopKeyWatcher":
        if os.name != "nt" and sys.stdin.isatty():
            import termios
            import tty

            self._old_termios = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if os.name != "nt" and self._old_termios is not None:
            import termios

            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_termios)

    def pressed(self) -> bool:
        char = self._read_char()
        return char.lower() == self.key if char else False

    def _read_char(self) -> str:
        if os.name == "nt":
            import msvcrt

            if not msvcrt.kbhit():
                return ""
            value = msvcrt.getwch()
            return value if isinstance(value, str) else ""
        if not sys.stdin.isatty():
            return ""
        readable, _, _ = select.select([sys.stdin], [], [], 0)
        if not readable:
            return ""
        return sys.stdin.read(1)
