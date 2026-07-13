from labo_gerador_de_ventos.control import StopKeyWatcher


def test_stop_key_watcher_matches_requested_key() -> None:
    watcher = StopKeyWatcher("p")
    watcher._read_char = lambda: "p"  # type: ignore[method-assign]

    assert watcher.pressed()


def test_stop_key_watcher_ignores_other_keys() -> None:
    watcher = StopKeyWatcher("p")
    watcher._read_char = lambda: "x"  # type: ignore[method-assign]

    assert not watcher.pressed()
