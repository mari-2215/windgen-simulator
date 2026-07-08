from __future__ import annotations

import os
import subprocess
import sys

import streamlit as st

from labo_gerador_de_ventos.bench_app import (
    BenchAppConfig,
    bench_log_markdown,
    command_args,
    command_preview,
    command_timeout_s,
    project_root,
    profile_frame,
)
from labo_gerador_de_ventos.models.mlp import build_default_model
from labo_gerador_de_ventos.prompt import parse_prompt
from labo_gerador_de_ventos.simulation import simulate


st.set_page_config(page_title="Neural Offshore Wind Lab", page_icon="🌬️", layout="wide")
st.title("Neural Offshore Wind Lab")
st.caption("Phase 1 / Fase 1 - Weibull + MLP | simulation and operational bench mode")
st.warning(
    "Physical motor execution is guarded by laboratory confirmations. Real wind-speed feedback "
    "requires an external anemometer or another measured wind sensor."
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
        "Aplicativo de bancada operacional: planejamento, perfil de throttle, comando pronto, "
        "execução guardada, feedback de vento e registro."
    )

    col_left, col_right = st.columns([1, 1])
    with col_left:
        bench_test = st.selectbox(
            "Teste",
            ["Bench Test 1", "Bench Test 2", "Bench Test 3", "Bench Test 4", "Bench Test 5"],
        )
        mode_options = {
            "Bench Test 1": ["mock", "neural-mock", "serial-check", "physical-preview"],
            "Bench Test 2": ["mock", "physical-preview"],
            "Bench Test 3": ["mock", "motor"],
            "Bench Test 4": ["mock", "motor"],
            "Bench Test 5": ["mock", "motor"],
        }
        mode = st.selectbox("Modo", mode_options[bench_test])
        port = st.text_input("Porta serial", "/dev/ttyACM0")
        motor = st.number_input("Motor", min_value=1, max_value=8, value=1, step=1)
        motor_count = st.number_input("Quantidade de motores no arranjo", 1, 4, 1, 1)
        layout = st.selectbox("Layout do arranjo", ["cross", "x"])

    with col_right:
        max_default = 0.08 if bench_test == "Bench Test 1" else 0.60
        max_throttle = st.slider("Throttle máximo", 0.01, 1.0, max_default, 0.01)
        duration_s = st.number_input("Duração do Bench Test 1 (s)", 1.0, 10.0, 3.0, 0.5)
        endurance_s = st.number_input("Duração do Bench Test 4/5 (s)", 10.0, 900.0, 600.0, 10.0)
        ramp_s = st.number_input("Rampa do Bench Test 3 (s)", 0.5, 10.0, 2.0, 0.5)
        hold_s = st.number_input("Patamar do Bench Test 3 (s)", 0.5, 30.0, 3.0, 0.5)
        sample_period_s = st.number_input("Amostragem do perfil (s)", 0.05, 2.0, 0.25, 0.05)
        feedback_kp = st.number_input("Ganho do feedback de vento (kp)", 0.0, 0.2, 0.035, 0.005)

    if bench_test == "Bench Test 5":
        wind_source = st.selectbox("Fonte da velocidade atual do vento", ["simulated", "serial"])
        wind_port = st.text_input("Porta do anemômetro serial", "")
        if wind_source == "serial":
            st.info("Feedback real de vento habilitado: o anemômetro deve enviar velocidade em m/s por linha serial.")
        else:
            st.warning("Sem sensor externo, a velocidade atual do vento fica simulada. Para feedback real, é necessário anemômetro.")
    else:
        wind_source = "simulated"
        wind_port = ""

    prompt = st.text_area(
        "Prompt neural",
        "vento offshore de 12 m/s por 10 min a 1 m",
    )

    config = BenchAppConfig(
        bench_test=bench_test,
        mode=mode,
        port=port,
        motor=int(motor),
        max_throttle=float(max_throttle),
        duration_s=float(endurance_s if bench_test in ("Bench Test 4", "Bench Test 5") else duration_s),
        ramp_s=float(ramp_s),
        hold_s=float(hold_s),
        sample_period_s=float(sample_period_s),
        prompt=prompt,
        layout=layout,
        motor_count=int(motor_count),
        wind_source=wind_source,
        wind_port=wind_port,
        feedback_kp=float(feedback_kp),
    )

    frame = profile_frame(config)
    a, b, c = st.columns(3)
    a.metric("Duração do perfil", f"{frame.time_s.max():.2f} s")
    b.metric("Throttle máximo planejado", f"{frame.throttle_percent.max():.1f}%")
    c.metric("Amostras", f"{len(frame)}")

    st.line_chart(frame.set_index("time_s")[["throttle_percent"]])
    st.dataframe(frame, use_container_width=True)

    if mode in ("physical-preview", "motor"):
        st.error(
            "Modo físico. A bancada deve estar fixa, supervisionada e com corte de energia pronto. "
            "Bench Tests 3, 4 e 5 podem executar o motor diretamente por esta tela."
        )
    else:
        st.success("Modo seguro: o comando gerado não aciona hardware físico.")

    command = command_preview(config)
    st.code(command, language="bash")

    if bench_test in ("Bench Test 3", "Bench Test 4", "Bench Test 5") and mode == "motor":
        st.subheader("Execução física")
        secured = st.checkbox("Motor/arranjo preso, protegido e sem possibilidade de soltar a fixação")
        supervised = st.checkbox("Supervisão de laboratório ativa")
        estop = st.checkbox("Corte físico de energia pronto")
        full_text = ""
        if max_throttle > 0.60:
            full_text = st.text_input(
                "Confirmação para throttle acima de 60%",
                placeholder="FULL_THROTTLE_APPROVED",
            )
        sensor_ready = not (bench_test == "Bench Test 5" and wind_source == "serial" and not wind_port.strip())
        ready = (
            secured
            and supervised
            and estop
            and sensor_ready
            and (max_throttle <= 0.60 or full_text == "FULL_THROTTLE_APPROVED")
        )
        if not ready:
            st.info("A execução física será liberada após as confirmações de bancada.")
            if not sensor_ready:
                st.warning("Anemômetro serial selecionado sem porta definida.")
        if st.button(f"Executar {bench_test} no motor", type="primary", disabled=not ready):
            root = project_root()
            env = os.environ.copy()
            src_path = str(root / "src")
            env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
            with st.spinner(f"Executando {bench_test} no motor..."):
                result = subprocess.run(
                    command_args(config, python_executable=sys.executable),
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=command_timeout_s(config),
                    check=False,
                )
            if result.returncode == 0:
                st.success(f"{bench_test} finalizado.")
            else:
                st.error(f"{bench_test} terminou com código {result.returncode}.")
            if result.stdout:
                st.text_area("Saída", result.stdout, height=220)
            if result.stderr:
                st.text_area("Erros", result.stderr, height=160)

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
