import pytest

from labo_gerador_de_ventos.prompt import parse_prompt


def test_prompt_converts_units() -> None:
    request = parse_prompt("vento de 36 km/h, rajadas de 54 km/h por 2 min a 1500 mm")
    assert request.mean_mps == pytest.approx(10)
    assert request.gust_mps == pytest.approx(15)
    assert request.duration_s == 120
    assert request.distance_m == pytest.approx(1.5)


def test_prompt_rejects_extreme_speed() -> None:
    with pytest.raises(ValueError):
        parse_prompt("vento de 200 m/s")


def test_english_prompt() -> None:
    request = parse_prompt("offshore wind at 12 m/s, gusts of 18 m/s for 2 min at 1500 mm")
    assert request.mean_mps == pytest.approx(12)
    assert request.gust_mps == pytest.approx(18)
    assert request.duration_s == 120
    assert request.distance_m == pytest.approx(1.5)
