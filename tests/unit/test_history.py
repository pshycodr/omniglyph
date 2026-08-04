from services.history import HistoryService


def test_add_stores_entry(tmp_history_dir):
    svc = HistoryService()
    svc.add({"symbol": "😀", "name": "grinning"})
    assert svc.get_global()[0]["symbol"] == "😀"


def test_add_ignores_entry_without_symbol(tmp_history_dir):
    svc = HistoryService()
    svc.add({"name": "no symbol here"})
    assert svc.get_global() == []


def test_add_moves_duplicate_to_front(tmp_history_dir):
    svc = HistoryService()
    svc.add({"symbol": "😀"})
    svc.add({"symbol": "😎"})
    svc.add({"symbol": "😀"})
    result = svc.get_global()
    assert result[0]["symbol"] == "😀"
    assert len(result) == 2


def test_global_limit_enforced(tmp_history_dir):
    svc = HistoryService()
    for i in range(60):
        svc.add({"symbol": str(i)})
    assert len(svc.get_global()) == 50


def test_clear_global(tmp_history_dir):
    svc = HistoryService()
    svc.add({"symbol": "😀"})
    svc.clear_global()
    assert svc.get_global() == []


def test_persists_across_instances(tmp_history_dir):
    svc1 = HistoryService()
    svc1.add({"symbol": "😀"})

    svc2 = HistoryService()
    assert svc2.get_global()[0]["symbol"] == "😀"


def test_recovers_from_corrupt_file(tmp_history_dir):
    (tmp_history_dir / "history.json").write_text("not json")
    svc = HistoryService()
    assert svc.get_global() == []
