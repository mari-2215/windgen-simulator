from labo_gerador_de_ventos.bench_app import (
    BenchAppConfig,
    bench_log_markdown,
    command_args,
    command_preview,
    profile_frame,
)


def test_bench_app_generates_profile_frame_for_bench_test_3() -> None:
    config = BenchAppConfig(
        bench_test="Bench Test 3",
        mode="planning",
        max_throttle=0.60,
        ramp_s=2.0,
        hold_s=3.0,
        sample_period_s=1.0,
    )
    frame = profile_frame(config)
    assert list(frame.columns) == ["time_s", "throttle", "throttle_percent"]
    assert frame.throttle.max() == 0.60
    assert frame.iloc[-1].throttle == 0.0


def test_bench_app_keeps_physical_bench_test_1_capped_at_ten_percent() -> None:
    config = BenchAppConfig(
        bench_test="Bench Test 1",
        mode="physical-preview",
        max_throttle=0.80,
        prompt="vento offshore de 6 m/s por 3 s a 1 m",
    )
    command = command_preview(config)
    assert "--mode neural-motor" in command
    assert "--max-throttle 0.10" in command


def test_bench_app_exports_markdown_log() -> None:
    config = BenchAppConfig(bench_test="Bench Test 2", mode="mock")
    markdown = bench_log_markdown(config, "Teste simulado.")
    assert "# Bench Test 2 - registro de bancada" in markdown
    assert "Teste simulado." in markdown


def test_bench_app_generates_real_motor_command_for_bench_test_3() -> None:
    config = BenchAppConfig(
        bench_test="Bench Test 3",
        mode="motor",
        port="/dev/ttyACM0",
        motor=1,
        max_throttle=1.0,
        ramp_s=2.0,
        hold_s=3.0,
    )
    args = command_args(config, python_executable="python3")
    assert "--mode" in args
    assert "motor" in args
    assert "--allow-full-throttle" in args
    assert "--confirm-secured" in args
    assert "--confirm-supervision" in args
    assert "--confirm-estop" in args


def test_bench_app_generates_bench_test_4_neural_motor_command() -> None:
    config = BenchAppConfig(
        bench_test="Bench Test 4",
        mode="motor",
        prompt="vento offshore de 12 m/s por 10 min a 1 m",
        layout="x",
        motor_count=4,
        duration_s=600.0,
        max_throttle=1.0,
    )
    args = command_args(config, python_executable="python3")
    assert "scripts/bench_test_4.py" in args
    assert "--prompt" in args
    assert "--layout" in args
    assert "x" in args
    assert "--motor-count" in args
    assert "4" in args


def test_bench_app_generates_bench_test_5_feedback_command() -> None:
    config = BenchAppConfig(
        bench_test="Bench Test 5",
        mode="motor",
        prompt="vento offshore de 12 m/s por 60 s a 1 m",
        layout="cross",
        motor_count=1,
        duration_s=60.0,
        max_throttle=1.0,
        wind_source="serial",
        wind_port="/dev/ttyUSB0",
        feedback_kp=0.04,
    )
    args = command_args(config, python_executable="python3")
    assert "scripts/bench_test_5.py" in args
    assert "--wind-source" in args
    assert "serial" in args
    assert "--wind-port" in args
    assert "/dev/ttyUSB0" in args
    assert "--kp" in args
    assert "0.0400" in args
