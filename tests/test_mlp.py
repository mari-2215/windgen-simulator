import numpy as np

from labo_gerador_de_ventos.models.mlp import TinyMLP, synthetic_calibration_data


def test_mlp_learns_synthetic_mapping() -> None:
    x, y = synthetic_calibration_data(samples=500, seed=3)
    model = TinyMLP(seed=3, hidden_layers=(24, 12))
    history = model.fit(x, y, epochs=700, learning_rate=0.008)
    prediction = model.predict(x)
    assert history.losses[-1] < history.losses[0]
    assert history.validation_losses[-1] < history.validation_losses[0]
    assert np.mean(np.abs(prediction - y)) < 0.06


def test_mlp_save_and_load_deep_model(tmp_path) -> None:
    x, y = synthetic_calibration_data(samples=300, seed=8)
    model = TinyMLP(seed=8, hidden_layers=(16, 8))
    model.fit(x, y, epochs=300, learning_rate=0.008)
    path = tmp_path / "deep_mlp.npz"
    model.save(path)
    loaded = TinyMLP.load(path)
    assert np.allclose(model.predict(x[:10]), loaded.predict(x[:10]))
