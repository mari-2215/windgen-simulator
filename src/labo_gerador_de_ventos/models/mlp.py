from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class TrainingHistory:
    losses: list[float]


class TinyMLP:
    """MLP 2->H->1 leve, suficiente para inferência no Raspberry Pi 2."""

    def __init__(self, hidden: int = 12, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        self.w1 = rng.normal(0, 0.25, (2, hidden))
        self.b1 = np.zeros((1, hidden))
        self.w2 = rng.normal(0, 0.25, (hidden, 1))
        self.b2 = np.zeros((1, 1))
        self.x_mean = np.zeros((1, 2))
        self.x_std = np.ones((1, 2))
        self.y_min = 0.0
        self.y_span = 1.0

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

    def fit(
        self, x: np.ndarray, y: np.ndarray, epochs: int = 1500, learning_rate: float = 0.03
    ) -> TrainingHistory:
        x = np.asarray(x, dtype=float).reshape(-1, 2)
        y = np.asarray(y, dtype=float).reshape(-1, 1)
        self.x_mean = x.mean(axis=0, keepdims=True)
        self.x_std = x.std(axis=0, keepdims=True) + 1e-8
        self.y_min = float(y.min())
        self.y_span = max(float(y.max() - y.min()), 1e-8)
        xn = (x - self.x_mean) / self.x_std
        yn = (y - self.y_min) / self.y_span
        losses: list[float] = []
        n = len(xn)
        for epoch in range(epochs):
            hidden = np.tanh(xn @ self.w1 + self.b1)
            pred = self._sigmoid(hidden @ self.w2 + self.b2)
            error = pred - yn
            if epoch % 100 == 0 or epoch == epochs - 1:
                losses.append(float(np.mean(error**2)))
            dz2 = (2.0 / n) * error * pred * (1.0 - pred)
            dw2 = hidden.T @ dz2
            db2 = dz2.sum(axis=0, keepdims=True)
            dh = dz2 @ self.w2.T
            dz1 = dh * (1.0 - hidden**2)
            self.w2 -= learning_rate * dw2
            self.b2 -= learning_rate * db2
            self.w1 -= learning_rate * (xn.T @ dz1)
            self.b1 -= learning_rate * dz1.sum(axis=0, keepdims=True)
        return TrainingHistory(losses)

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float).reshape(-1, 2)
        hidden = np.tanh(((x - self.x_mean) / self.x_std) @ self.w1 + self.b1)
        normalized = self._sigmoid(hidden @ self.w2 + self.b2)
        return (self.y_min + normalized * self.y_span).ravel()

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2,
            x_mean=self.x_mean, x_std=self.x_std, y_min=self.y_min, y_span=self.y_span,
        )

    @classmethod
    def load(cls, path: str | Path) -> "TinyMLP":
        data = np.load(path)
        model = cls(hidden=data["w1"].shape[1])
        for name in ("w1", "b1", "w2", "b2", "x_mean", "x_std"):
            setattr(model, name, data[name])
        model.y_min = float(data["y_min"])
        model.y_span = float(data["y_span"])
        return model


def synthetic_calibration_data(samples: int = 1200, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Planta inicial apenas para integração; substituir por medições de anemômetro."""
    rng = np.random.default_rng(seed)
    wind = rng.uniform(0.5, 22.0, samples)
    distance = rng.uniform(0.3, 3.0, samples)
    throttle = np.sqrt(wind / 28.0) * (1.0 + 0.13 * distance)
    throttle += rng.normal(0, 0.008, samples)
    return np.column_stack((wind, distance)), np.clip(throttle, 0.0, 1.0)


def build_default_model(seed: int = 42, epochs: int = 1000) -> TinyMLP:
    x, y = synthetic_calibration_data(seed=seed)
    model = TinyMLP(seed=seed)
    model.fit(x, y, epochs=epochs)
    return model

