from __future__ import annotations

import shlex
from dataclasses import dataclass

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
    port = shlex.quote(config.port)
    prompt = shlex.quote(config.prompt)
    if config.bench_test == "Bench Test 1":
        if config.mode == "mock":
            return "python3 scripts/bench_test_1.py --mode mock"
        if config.mode == "neural-mock":
            return (
                "python3 scripts/bench_test_1.py "
                f"--mode neural-mock --prompt {prompt} --max-throttle {config.max_throttle:.2f}"
            )
        if config.mode == "serial-check":
            return f"python3 scripts/bench_test_1.py --mode serial-check --port {port}"
        if config.mode == "physical-preview":
            return (
                "python3 scripts/bench_test_1.py "
                f"--mode neural-motor --port {port} --motor {config.motor} "
                f"--max-throttle {min(config.max_throttle, 0.10):.2f} "
                f"--duration {config.duration_s:.1f} --prompt {prompt}"
            )
    if config.bench_test == "Bench Test 2":
        if config.mode == "mock":
            return "python3 scripts/bench_test_2.py --mode mock"
        if config.mode == "physical-preview":
            return (
                "python3 scripts/bench_test_2.py "
                f"--mode motor --port {port} --motor {config.motor} --allow-high-throttle"
            )
    if config.bench_test == "Bench Test 3":
        return (
            "python3 scripts/bench_test_3.py "
            f"--max-throttle {config.max_throttle:.2f} --ramp {config.ramp_s:.1f} "
            f"--hold {config.hold_s:.1f} --sample-period {config.sample_period_s:.2f}"
        )
    raise ValueError(f"unsupported command mode: {config.bench_test} / {config.mode}")


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
