from __future__ import annotations

import streamlit as st

from labo_gerador_de_ventos.models.mlp import build_default_model
from labo_gerador_de_ventos.prompt import parse_prompt
from labo_gerador_de_ventos.simulation import simulate


st.set_page_config(page_title="Neural Offshore Wind Lab", page_icon="🌬️", layout="wide")
st.title("Neural Offshore Wind Lab")
st.caption("Phase 1 / Fase 1 - Weibull + MLP | simulation mode")
st.warning("Hardware is disabled here. Validate the test bench and read docs/en/hardware.md.")

prompt = st.text_area(
    "Prompt do cenário",
    "cenário offshore moderado, média 12 m/s, rajadas de 18 m/s, por 60 s a 1,5 m",
)
seed = st.number_input("Semente", min_value=0, value=42, step=1)
sampling_hz = st.slider("Amostragem (Hz)", 1, 20, 5)


@st.cache_resource
def model_for(seed_value: int):
    return build_default_model(seed=seed_value)


if st.button("Simular", type="primary"):
    try:
        request = parse_prompt(prompt)
        frame = simulate(request, model_for(int(seed)), sampling_hz=float(sampling_hz), seed=int(seed))
        a, b, c = st.columns(3)
        a.metric("Média", f"{frame.wind_target_mps.mean():.2f} m/s")
        b.metric("Máxima", f"{frame.wind_target_mps.max():.2f} m/s")
        c.metric("Throttle médio (modelo)", f"{100 * frame.throttle_model.mean():.1f}%")
        st.line_chart(frame.set_index("time_s")[["wind_target_mps"]])
        st.download_button(
            "Baixar CSV", frame.to_csv(index=False).encode("utf-8"),
            "wind_series.csv", "text/csv",
        )
        st.dataframe(frame.head(100), use_container_width=True)
    except ValueError as error:
        st.error(str(error))
