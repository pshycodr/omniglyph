import json
from pathlib import Path
from services.notification import notify_if_nerd_font_missing


class CollectionLoader:
    def __init__(self, app):
        self.app = app
        self.collection_path = Path(__file__).resolve().parent / "collections"

    def _load(self, filename):
        with open(
            self.collection_path / filename,
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    def LoadEmojis(self):
        return self._load("emojis.json")

    def LoadEmoticons(self):
        return self._load("emoticons.json")

    def LoadSpecialSymbols(self):
        return self._load("special_symbols.json")

    def LoadCurrency(self):
        return self._load("currency.json")

    def LoadMathSymbols(self):
        return self._load("math.json")

    def LoadArrows(self):
        return self._load("arrows.json")

    def LoadHieroglyphs(self):
        return self._load("hieroglyphs.json")

    def LoadNerdFonts(self):
        notify_if_nerd_font_missing(self.app)
        return self._load("nerd_font_icons.json")
