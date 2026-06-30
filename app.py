from __future__ import annotations

import streamlit as st

from labo_gerador_de_ventos.bench_app import (
    BenchAppConfig,
    bench_log_markdown,
    command_preview,
    profile_frame,
)
from labo_gerador_de_ventos.models.mlp import build_default_model
from labo_gerador_de_ventos.prompt import parse_prompt
from labo_gerador_de_ventos.simulation import simulate


st.set_page_config(page_title="Neural Offshore Wind Lab", page_icon="🌬️", layout="wide")
st.title("Neural Offshore Wind Lab")
st.caption("Phase 1 / Fase 1 - Weibull + MLP | simulation and bench-planning mode")
st.warning(
    "Hardware is disabled inside this app v0. Physical tests must remain under the guarded CLI "
    "scripts and the hardware checklist."
)


@st.cache_resource
def model_for(seed_value: int):
    return build_default_model(seed=seed_value)


def render_simulation_tab() -> None:
    prompt = st.text_area(
        "Prompt do cenário",
        "cenário offshore moderado, média 12 m/s, rajadas de 18 m/s, por 60 s a 1,5 m",
    )
    seed = st.number_input("Semente", min_value=0, value=42, step=1)
    sampling_hz = st.slider("Amostragem (Hz)", 1, 20, 5)

    if st.button("Simular", type="primary"):
        try:
            request = parse_prompt(prompt)
            frame = simulate(
                request,
                model_for(int(seed)),
                sampling_hz=float(sampling_hz),
                seed=int(seed),
            )
            a, b, c = st.columns(3)
            a.metric("Média", f"{frame.wind_target_mps.mean():.2f} m/s")
            b.metric("Máxima", f"{frame.wind_target_mps.max():.2f} m/s")
            c.metric("Throttle médio (modelo)", f"{100 * frame.throttle_model.mean():.1f}%")
            st.line_chart(frame.set_index("time_s")[["wind_target_mps"]])
            st.download_button(
                "Baixar CSV",
                frame.to_csv(index=False).encode("utf-8"),
                "wind_series.csv",
                "text/csv",
            )
            st.dataframe(frame.head(100), use_container_width=True)
        except ValueError as error:
            st.error(str(error))


def render_bench_tab() -> None:
    st.subheader("Bench Tests")
    st.caption(
        "Aplicativo de bancada v0: planejamento, perfil de throttle, comando pronto e registro. "
        "Nenhum comando físico é enviado por esta tela."
    )

    col_left, col_right = st.columns([1, 1])
    with col_left:
        bench_test = st.selectbox("Teste", ["Bench Test 1", "Bench Test 2", "Bench Test 3"])
        mode_options = {
            "Bench Test 1": ["mock", "neural-mock", "serial-check", "physical-preview"],
            "Bench Test 2": ["mock", "physical-preview"],
            "Bench Test 3": ["planning"],
        }
        mode = st.selectbox("Modo", mode_options[bench_test])
        port = st.text_input("Porta serial", "/dev/ttyACM0")
        motor = st.number_input("Motor", min_value=1, max_value=8, value=1, step=1)

    with col_right:
        max_default = 0.08 if bench_test == "Bench Test 1" else 0.60
        max_throttle = st.slider("Throttle máximo", 0.01, 1.0, max_default, 0.01)
        duration_s = st.number_input("Duração do Bench Test 1 (s)", 1.0, 10.0, 3.0, 0.5)
        ramp_s = st.number_input("Rampa do Bench Test 3 (s)", 0.5, 10.0, 2.0, 0.5)
        hold_s = st.number_input("Patamar do Bench Test 3 (s)", 0.5, 30.0, 3.0, 0.5)
        sample_period_s = st.number_input("Amostragem do perfil (s)", 0.05, 2.0, 0.25, 0.05)

    prompt = st.text_area(
        "Prompt neural para Bench Test 1",
        "vento offshore de 6 m/s por 3 s a 1 m",
    )

    config = BenchAppConfig(
        bench_test=bench_test,
        mode=mode,
        port=port,
        motor=int(motor),
        max_throttle=float(max_throttle),
        duration_s=float(duration_s),
        ramp_s=float(ramp_s),
        hold_s=float(hold_s),
        sample_period_s=float(sample_period_s),
        prompt=prompt,
    )

    frame = profile_frame(config)
    a, b, c = st.columns(3)
    a.metric("Duração do perfil", f"{frame.time_s.max():.2f} s")
    b.metric("Throttle máximo planejado", f"{frame.throttle_percent.max():.1f}%")
    c.metric("Amostras", f"{len(frame)}")

    st.line_chart(frame.set_index("time_s")[["throttle_percent"]])
    st.dataframe(frame, use_container_width=True)

    if mode == "physical-preview":
        st.error(
            "Este modo apenas gera o comando físico. A execução continua fora do app, com as "
            "confirmações do script, hélice removida, proteção física e corte de energia."
        )
    else:
        st.success("Modo seguro: o comando gerado não aciona hardware físico.")

    command = command_preview(config)
    st.code(command, language="bash")

    notes = st.text_area(
        "Registro do ensaio",
        "Resultado previsto, observações de bancada, ruído, aquecimento, RPM e mídia associada.",
    )
    log_markdown = bench_log_markdown(config, notes)
    st.download_button(
        "Baixar registro Markdown",
        log_markdown.encode("utf-8"),
        f"{bench_test.lower().replace(' ', '-')}-log.md",
        "text/markdown",
    )

    st.download_button(
        "Baixar perfil CSV",
        frame.to_csv(index=False).encode("utf-8"),
        f"{bench_test.lower().replace(' ', '-')}-profile.csv",
        "text/csv",
    )


simulation_tab, bench_tab = st.tabs(["Simulação Weibull + MLP", "Bench Tests"])
with simulation_tab:
    render_simulation_tab()
with bench_tab:
    render_bench_tab()
