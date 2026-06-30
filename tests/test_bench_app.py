from labo_gerador_de_ventos.bench_app import (
    BenchAppConfig,
    bench_log_markdown,
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
