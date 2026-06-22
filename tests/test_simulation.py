from labo_gerador_de_ventos.models.mlp import build_default_model
from labo_gerador_de_ventos.prompt import WindRequest
from labo_gerador_de_ventos.simulation import simulate


def test_simulation_schema_and_ranges() -> None:
    frame = simulate(WindRequest(10, 15, 4, 1.0), build_default_model(epochs=300), sampling_hz=5)
    assert list(frame.columns) == ["time_s", "wind_target_mps", "distance_m", "throttle_model"]
    assert len(frame) == 20
    assert frame.throttle_model.between(0, 1).all()

