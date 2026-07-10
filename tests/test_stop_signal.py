from labo_gerador_de_ventos.control import clear_stop_request, request_stop, stop_requested


def test_stop_signal_latches_and_clears() -> None:
    clear_stop_request()
    assert not stop_requested()
    path = request_stop("test stop")
    assert path.exists()
    assert stop_requested()
    clear_stop_request()
    assert not stop_requested()
