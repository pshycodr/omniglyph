import json
import os
from pathlib import Path

GLOBAL_LIMIT = 50

_DATA_DIR = (
    Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    / "omniglyph"
)
_HISTORY_FILE = _DATA_DIR / "history.json"


class HistoryService:
    def __init__(self):
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self):
        try:
            return json.loads(_HISTORY_FILE.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {"global": []}

    def _save(self):
        _HISTORY_FILE.write_text(json.dumps(self._data, ensure_ascii=False, indent=2))

    def add(self, entry: dict):
        symbol = entry.get("symbol", "")
        if not symbol:
            return

        stamped = {**entry}
        # stamped = {**entry, "collection_name": collection_name}

        global_hist = [e for e in self._data["global"] if e.get("symbol") != symbol]
        global_hist.insert(0, stamped)
        self._data["global"] = global_hist[:GLOBAL_LIMIT]

        self._save()

    def get_global(self) -> list:
        return list(self._data["global"])

    def clear_global(self):
        self._data["global"] = []
        self._save()
