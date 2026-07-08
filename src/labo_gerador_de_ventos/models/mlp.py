from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class TrainingHistory:
    losses: list[float]
    validation_losses: list[float]


class TinyMLP:
    """Configurable NumPy MLP for prompt-to-throttle inference on low-power hardware.

    The public class name was preserved for script compatibility, but the implementation now
    supports multiple hidden layers, Adam optimization, validation tracking, and deterministic
    train/validation splits.
    """

    def __init__(
        self,
        hidden: int | None = 12,
        seed: int = 42,
        hidden_layers: tuple[int, ...] | None = None,
        activation: str = "tanh",
    ) -> None:
        if hidden_layers is None:
            hidden_layers = (hidden or 12,)
        if not hidden_layers or any(layer <= 0 for layer in hidden_layers):
            raise ValueError("hidden_layers must contain positive layer sizes")
        if activation not in {"tanh", "relu"}:
            raise ValueError("activation must be 'tanh' or 'relu'")

        self.hidden_layers = tuple(int(layer) for layer in hidden_layers)
        self.activation = activation
        self.seed = seed
        self.x_mean = np.zeros((1, 2))
        self.x_std = np.ones((1, 2))
        self.y_min = 0.0
        self.y_span = 1.0

        rng = np.random.default_rng(seed)
        layer_sizes = (2, *self.hidden_layers, 1)
        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []
        for fan_in, fan_out in zip(layer_sizes, layer_sizes[1:]):
            scale = np.sqrt(2.0 / fan_in) if activation == "relu" else np.sqrt(1.0 / fan_in)
            self.weights.append(rng.normal(0.0, scale, (fan_in, fan_out)))
            self.biases.append(np.zeros((1, fan_out)))

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

    def _activate(self, x: np.ndarray) -> np.ndarray:
        if self.activation == "relu":
            return np.maximum(x, 0.0)
        return np.tanh(x)

    def _activation_grad(self, activated: np.ndarray) -> np.ndarray:
        if self.activation == "relu":
            return (activated > 0.0).astype(float)
        return 1.0 - activated**2

    def _forward(self, x: np.ndarray) -> tuple[list[np.ndarray], np.ndarray]:
        activations = [x]
        current = x
        for weight, bias in zip(self.weights[:-1], self.biases[:-1]):
            current = self._activate(current @ weight + bias)
            activations.append(current)
        output = self._sigmoid(current @ self.weights[-1] + self.biases[-1])
        activations.append(output)
        return activations, output

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        epochs: int = 1500,
        learning_rate: float = 0.01,
        validation_split: float = 0.2,
        weight_decay: float = 1e-4,
    ) -> TrainingHistory:
        x = np.asarray(x, dtype=float).reshape(-1, 2)
        y = np.asarray(y, dtype=float).reshape(-1, 1)
        if len(x) < 10:
            raise ValueError("at least 10 samples are required")

        self.x_mean = x.mean(axis=0, keepdims=True)
        self.x_std = x.std(axis=0, keepdims=True) + 1e-8
        self.y_min = float(y.min())
        self.y_span = max(float(y.max() - y.min()), 1e-8)
        xn = (x - self.x_mean) / self.x_std
        yn = (y - self.y_min) / self.y_span

        rng = np.random.default_rng(self.seed)
        indices = rng.permutation(len(xn))
        val_size = int(round(len(xn) * validation_split))
        val_size = min(max(val_size, 1), len(xn) - 1)
        val_idx = indices[:val_size]
        train_idx = indices[val_size:]
        x_train, y_train = xn[train_idx], yn[train_idx]
        x_val, y_val = xn[val_idx], yn[val_idx]

        losses: list[float] = []
        validation_losses: list[float] = []
        m_w = [np.zeros_like(weight) for weight in self.weights]
        v_w = [np.zeros_like(weight) for weight in self.weights]
        m_b = [np.zeros_like(bias) for bias in self.biases]
        v_b = [np.zeros_like(bias) for bias in self.biases]
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        n = len(x_train)

        for epoch in range(1, epochs + 1):
            activations, pred = self._forward(x_train)
            error = pred - y_train
            dz = (2.0 / n) * error * pred * (1.0 - pred)

            grad_w: list[np.ndarray] = [np.empty_like(weight) for weight in self.weights]
            grad_b: list[np.ndarray] = [np.empty_like(bias) for bias in self.biases]
            for layer in reversed(range(len(self.weights))):
                grad_w[layer] = activations[layer].T @ dz + weight_decay * self.weights[layer]
                grad_b[layer] = dz.sum(axis=0, keepdims=True)
                if layer > 0:
                    dz = (dz @ self.weights[layer].T) * self._activation_grad(activations[layer])

            for index in range(len(self.weights)):
                m_w[index] = beta1 * m_w[index] + (1.0 - beta1) * grad_w[index]
                v_w[index] = beta2 * v_w[index] + (1.0 - beta2) * (grad_w[index] ** 2)
                m_b[index] = beta1 * m_b[index] + (1.0 - beta1) * grad_b[index]
                v_b[index] = beta2 * v_b[index] + (1.0 - beta2) * (grad_b[index] ** 2)

                m_w_hat = m_w[index] / (1.0 - beta1**epoch)
                v_w_hat = v_w[index] / (1.0 - beta2**epoch)
                m_b_hat = m_b[index] / (1.0 - beta1**epoch)
                v_b_hat = v_b[index] / (1.0 - beta2**epoch)

                self.weights[index] -= learning_rate * m_w_hat / (np.sqrt(v_w_hat) + eps)
                self.biases[index] -= learning_rate * m_b_hat / (np.sqrt(v_b_hat) + eps)

            if epoch % 100 == 0 or epoch == 1 or epoch == epochs:
                train_loss = float(np.mean((self._forward(x_train)[1] - y_train) ** 2))
                val_loss = float(np.mean((self._forward(x_val)[1] - y_val) ** 2))
                losses.append(train_loss)
                validation_losses.append(val_loss)

        return TrainingHistory(losses, validation_losses)

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float).reshape(-1, 2)
        xn = (x - self.x_mean) / self.x_std
        normalized = self._forward(xn)[1]
        return (self.y_min + normalized * self.y_span).ravel()

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {
            "x_mean": self.x_mean,
            "x_std": self.x_std,
            "y_min": np.array(self.y_min),
            "y_span": np.array(self.y_span),
            "hidden_layers": np.array(self.hidden_layers, dtype=int),
            "activation": np.array(self.activation),
        }
        for index, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            payload[f"w{index}"] = weight
            payload[f"b{index}"] = bias
        np.savez(path, **payload)

    @classmethod
    def load(cls, path: str | Path) -> "TinyMLP":
        data = np.load(path)
        if "hidden_layers" in data:
            hidden_layers = tuple(int(item) for item in data["hidden_layers"])
            activation = str(data["activation"])
            model = cls(hidden_layers=hidden_layers, activation=activation)
            model.weights = [data[f"w{index}"] for index in range(len(hidden_layers) + 1)]
            model.biases = [data[f"b{index}"] for index in range(len(hidden_layers) + 1)]
        else:
            model = cls(hidden=int(data["w1"].shape[1]))
            model.weights = [data["w1"], data["w2"]]
            model.biases = [data["b1"], data["b2"]]
        model.x_mean = data["x_mean"]
        model.x_std = data["x_std"]
        model.y_min = float(data["y_min"])
        model.y_span = float(data["y_span"])
        return model


def synthetic_calibration_data(samples: int = 2400, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Initial plant model for integration; replace with anemometer-calibrated data."""
    rng = np.random.default_rng(seed)
    wind = rng.uniform(0.5, 24.0, samples)
    distance = rng.uniform(0.25, 3.5, samples)
    base = np.sqrt(wind / 30.0) * (1.0 + 0.11 * distance)
    nonlinear_loss = 0.018 * distance**2 + 0.025 * np.maximum(wind - 16.0, 0.0) / 8.0
    throttle = base + nonlinear_loss
    throttle += rng.normal(0, 0.006, samples)
    return np.column_stack((wind, distance)), np.clip(throttle, 0.0, 1.0)


def build_default_model(seed: int = 42, epochs: int = 1200) -> TinyMLP:
    x, y = synthetic_calibration_data(seed=seed)
    model = TinyMLP(seed=seed, hidden_layers=(32, 24, 12), activation="tanh")
    model.fit(x, y, epochs=epochs, learning_rate=0.008)
    return model
