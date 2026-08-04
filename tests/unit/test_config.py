import pytest

from utils.config import Config


@pytest.fixture
def config(tmp_config_dir):
    return Config()


def test_writes_default_config_file(tmp_config_dir):
    Config()
    assert (tmp_config_dir / "omniglyph" / "config.toml").exists()


def test_default_shortcut_value(config):
    assert config.get("shortcuts", "quit") == "ctrl+q"


def test_get_returns_default_for_missing_key(config):
    assert config.get("shortcuts", "nope", default="fallback") == "fallback"


def test_get_returns_default_when_intermediate_not_dict(config):
    # "quit" resolves to a string, not a dict -- next lookup must not crash
    assert config.get("shortcuts", "quit", "deeper", default="x") == "x"


def test_merge_overrides_leaf_values():
    base = {"a": {"x": 1, "y": 2}}
    override = {"a": {"y": 99}}
    merged = Config._merge(Config.__new__(Config), base, override)
    assert merged == {"a": {"x": 1, "y": 99}}


def test_merge_adds_new_top_level_keys():
    base = {"a": 1}
    override = {"b": 2}
    merged = Config._merge(Config.__new__(Config), base, override)
    assert merged == {"a": 1, "b": 2}


def test_shortcut_label_formats_modifiers(config):
    label = config.shortcut_label("quit")
    assert label == "Ctrl+Q"


def test_shortcut_label_empty_for_missing_shortcut(config):
    assert config.shortcut_label("does_not_exist") == ""


def test_load_reloads_from_disk(config, tmp_config_dir):
    config_file = tmp_config_dir / "omniglyph" / "config.toml"
    text = config_file.read_text()
    modified = text.replace('quit = "ctrl+q"', 'quit = "ctrl+w"')
    config_file.write_text(modified)

    config.load()
    assert config.get("shortcuts", "quit") == "ctrl+w"
