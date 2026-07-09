from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class WindRequest:
    mean_mps: float
    gust_mps: float
    duration_s: float
    distance_m: float
    shape: float = 2.0


def _plain(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))


def parse_prompt(text: str) -> WindRequest:
    clean = _plain(text).replace(",", ".")
    preset = 12.0
    if "leve" in clean or "light" in clean:
        preset = 6.0
    elif "forte" in clean or "strong" in clean:
        preset = 18.0
    speeds = [(float(v), unit) for v, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(m/s|km/h)", clean)]
    converted = [v / 3.6 if unit == "km/h" else v for v, unit in speeds]
    mean = converted[0] if converted else preset
    gust = converted[1] if len(converted) > 1 else mean * 1.35
    duration = 60.0
    match = re.search(
        r"(?:por|durante|for|during|duracao\s*(?:de)?|duration\s*(?:of)?)\s*"
        r"(\d+(?:\.\d+)?)\s*(s|sec|seconds?|min|minutes?|minutos?)",
        clean,
    )
    if match:
        duration = float(match.group(1)) * (60.0 if match.group(2).startswith("min") else 1.0)
    else:
        match = re.search(
            r"(?<!/)\b(\d+(?:\.\d+)?)\s*(segundos?|secs?|sec|seconds?|s|min|minutes?|minutos?)\b",
            clean,
        )
        if match:
            duration = float(match.group(1)) * (60.0 if match.group(2).startswith("min") else 1.0)
    distance = 1.5
    match = re.search(
        r"(?:\ba\s+|\bat\s+|\bdistancia\s*(?:de)?\s*|\bdistance\s*(?:of)?\s*)"
        r"(\d+(?:\.\d+)?)\s*(mm|m)(?!\s*/)",
        clean,
    )
    if match:
        distance = float(match.group(1)) / (1000.0 if match.group(2) == "mm" else 1.0)
    if not 0 <= mean <= 35 or not 0 <= gust <= 45:
        raise ValueError("velocidade fora da faixa acadêmica configurada")
    if not 1 <= duration <= 3600 or not 0.1 <= distance <= 5:
        raise ValueError("duração ou distância fora da faixa permitida")
    return WindRequest(mean, max(gust, mean), duration, distance)
