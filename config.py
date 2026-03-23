import json
import os
from utils.paths import config_path

CONFIG_PATH = config_path()

_config = {}


def load():
    global _config
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config = json.load(f)
    except Exception:
        _config = {
            "steam_api_key": "",
            "build_id": "1.0.0",
            "server_name": "Elysium",
            "developer": "ElysiumChecker"
        }
    return _config


def save():
    path = config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_config, f, indent=4, ensure_ascii=False)


def get(key, default=None):
    if not _config:
        load()
    return _config.get(key, default)


def set_value(key, value):
    if not _config:
        load()
    _config[key] = value
    save()
