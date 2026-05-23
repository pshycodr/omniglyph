import json
import os
from os import path


class CollectionLoader:
    def __init__(self):
        self.emojis = []
        self.collection_path = path.join(os.path.dirname(__file__), "collections")

    def LoadEmojis(self):
        with open(
            path.join(self.collection_path, "emojis.json"), "r", encoding="utf-8"
        ) as f:
            self.emojis = json.load(f)
            return self.emojis
