from __future__ import annotations

import shlex
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .control import (
    BENCH_TEST_1_PROFILE,
    BENCH_TEST_2_PROFILE,
    ControlPoint,
    build_bench_test_3_profile,
    interpolate_profile,
)


@dataclass(frozen=True)
class BenchAppConfig:
    bench_test: str
    mode: str
    port: str = "/dev/ttyACM0"
    motor: int = 1
    max_throttle: float = 0.60
    duration_s: float = 3.0
    ramp_s: float = 2.0
    hold_s: float = 3.0
    sample_period_s: float = 0.25
    prompt: str = "vento offshore de 6 m/s por 3 s a 1 m"
    layout: str = "cross"
    motor_count: int = 1
    wind_source: str = "simulated"
    wind_port: str = ""
    feedback_kp: float = 0.035


def profile_points(config: BenchAppConfig) -> tuple[ControlPoint, ...]:
    if config.bench_test == "Bench Test 1":
        return BENCH_TEST_1_PROFILE
    if config.bench_test == "Bench Test 2":
        return BENCH_TEST_2_PROFILE
    if config.bench_test == "Bench Test 3":
        return build_bench_test_3_profile(
            max_throttle=config.max_throttle,
            ramp_s=config.ramp_s,
            hold_s=config.hold_s,
        )
    if config.bench_test == "Bench Test 4":
        return build_bench_test_3_profile(
            max_throttle=config.max_throttle,
            ramp_s=config.ramp_s,
            hold_s=config.duration_s,
        )
    if config.bench_test == "Bench Test 5":
        return build_bench_test_3_profile(
            max_throttle=config.max_throttle,
            ramp_s=config.ramp_s,
            hold_s=config.duration_s,
        )
    raise ValueError(f"unknown bench test: {config.bench_test}")


def profile_frame(config: BenchAppConfig) -> pd.DataFrame:
    points = interpolate_profile(profile_points(config), sample_period_s=config.sample_period_s)
    return pd.DataFrame(
        {
            "time_s": [point.time_s for point in points],
            "throttle": [point.throttle for point in points],
            "throttle_percent": [100.0 * point.throttle for point in points],
        }
    )


def command_preview(config: BenchAppConfig) -> str:
    return " ".join(shlex.quote(part) for part in command_args(config, python_executable="python3"))


def command_args(config: BenchAppConfig, *, python_executable: str | None = None) -> list[str]:
    python = python_executable or sys.executable
    if config.bench_test == "Bench Test 1":
        if config.mode == "mock":
            return [python, "scripts/bench_test_1.py", "--mode", "mock"]
        if config.mode == "neural-mock":
            return [
                python,
                "scripts/bench_test_1.py",
                "--mode",
                "neural-mock",
                "--prompt",
                config.prompt,
                "--max-throttle",
                f"{config.max_throttle:.2f}",
            ]
        if config.mode == "serial-check":
            return [python, "scripts/bench_test_1.py", "--mode", "serial-check", "--port", config.port]
        if config.mode in ("physical-preview", "motor"):
            return [
                python,
                "scripts/bench_test_1.py",
                "--mode",
                "neural-motor",
                "--port",
                config.port,
                "--motor",
                str(config.motor),
                "--max-throttle",
                f"{min(config.max_throttle, 0.10):.2f}",
                "--duration",
                f"{config.duration_s:.1f}",
                "--prompt",
                config.prompt,
            ]
    if config.bench_test == "Bench Test 2":
        if config.mode == "mock":
            return [python, "scripts/bench_test_2.py", "--mode", "mock"]
        if config.mode in ("physical-preview", "motor"):
            return [
                python,
                "scripts/bench_test_2.py",
                "--mode",
                "motor",
                "--port",
                config.port,
                "--motor",
                str(config.motor),
                "--allow-high-throttle",
            ]
    if config.bench_test == "Bench Test 3":
        args = [
            python,
            "scripts/bench_test_3.py",
            "--mode",
            "motor" if config.mode == "motor" else "mock",
            "--max-throttle",
            f"{config.max_throttle:.2f}",
            "--ramp",
            f"{config.ramp_s:.1f}",
            "--hold",
            f"{config.hold_s:.1f}",
            "--sample-period",
            f"{config.sample_period_s:.2f}",
        ]
        if config.mode == "motor":
            args.extend(
                [
                    "--port",
                    config.port,
                    "--motor",
                    str(config.motor),
                    "--allow-full-throttle",
                    "--confirm-secured",
                    "--confirm-supervision",
                    "--confirm-estop",
                ]
            )
        return args
    if config.bench_test == "Bench Test 4":
        args = [
            python,
            "scripts/bench_test_4.py",
            "--mode",
            "motor" if config.mode == "motor" else "mock",
            "--prompt",
            config.prompt,
            "--layout",
            config.layout,
            "--motor-count",
            str(config.motor_count),
            "--max-throttle",
            f"{config.max_throttle:.2f}",
            "--duration",
            f"{config.duration_s:.1f}",
            "--ramp",
            f"{config.ramp_s:.1f}",
            "--sample-period",
            f"{config.sample_period_s:.2f}",
        ]
        if config.mode == "motor":
            args.extend(
                [
                    "--port",
                    config.port,
                    "--confirm-secured",
                    "--confirm-supervision",
                    "--confirm-estop",
                ]
            )
        return args
    if config.bench_test == "Bench Test 5":
        args = [
            python,
            "scripts/bench_test_5.py",
            "--mode",
            "motor" if config.mode == "motor" else "mock",
            "--prompt",
            config.prompt,
            "--layout",
            config.layout,
            "--motor-count",
            str(config.motor_count),
            "--max-throttle",
            f"{config.max_throttle:.2f}",
            "--duration",
            f"{config.duration_s:.1f}",
            "--ramp",
            f"{config.ramp_s:.1f}",
            "--sample-period",
            f"{config.sample_period_s:.2f}",
            "--kp",
            f"{config.feedback_kp:.4f}",
            "--wind-source",
            config.wind_source,
        ]
        if config.wind_source == "serial":
            args.extend(["--wind-port", config.wind_port])
        if config.mode == "motor":
            args.extend(
                [
                    "--port",
                    config.port,
                    "--confirm-secured",
                    "--confirm-supervision",
                    "--confirm-estop",
                ]
            )
        return args
    raise ValueError(f"unsupported command mode: {config.bench_test} / {config.mode}")


def command_timeout_s(config: BenchAppConfig) -> float:
    if config.bench_test == "Bench Test 1":
        return max(config.duration_s + 12.0, 20.0)
    frame = profile_frame(config)
    return float(frame.time_s.max() + 20.0)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def bench_log_markdown(config: BenchAppConfig, notes: str) -> str:
    return "\n".join(
        [
            f"# {config.bench_test} - registro de bancada",
            "",
            f"- Modo planejado: `{config.mode}`",
            f"- Porta serial: `{config.port}`",
            f"- Motor: `{config.motor}`",
            f"- Throttle máximo: `{100 * config.max_throttle:.1f}%`",
            f"- Rampa: `{config.ramp_s:.1f} s`",
            f"- Patamar: `{config.hold_s:.1f} s`",
            "",
            "## Comando planejado",
            "",
            "```bash",
            command_preview(config),
            "```",
            "",
            "## Observações",
            "",
            notes.strip() or "Sem observações registradas.",
            "",
        ]
    )
