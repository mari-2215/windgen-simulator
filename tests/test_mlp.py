import numpy as np

from labo_gerador_de_ventos.models.mlp import TinyMLP, synthetic_calibration_data


def test_mlp_learns_synthetic_mapping() -> None:
    x, y = synthetic_calibration_data(samples=500, seed=3)
    model = TinyMLP(seed=3)
    history = model.fit(x, y, epochs=900)
    prediction = model.predict(x)
    assert history.losses[-1] < history.losses[0]
    assert np.mean(np.abs(prediction - y)) < 0.09

