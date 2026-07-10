from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def stop_request_path() -> Path:
    return project_root() / "artifacts" / "control" / "STOP_REQUESTED"


def request_stop(reason: str = "manual stop") -> Path:
    path = stop_request_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(reason.strip() + "\n", encoding="utf-8")
    return path


def clear_stop_request() -> None:
    path = stop_request_path()
    if path.exists():
        path.unlink()


def stop_requested() -> bool:
    return stop_request_path().exists()
