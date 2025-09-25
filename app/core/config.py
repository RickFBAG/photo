import os
from typing import Any, Dict

import yaml


DEFAULT_SETTINGS = {
    "refresh": {"interval_seconds": 28800},
    "display": {"orientation": "portrait"},
    "display": {"mode": "html", "orientation": "portrait", "template": "display.html"},
    "layout": {"enabled_widgets": ["agenda", "news", "market"]},
    "theme": {
        "background": "#0b1220",
        "primary": "#F2F5F9",
        "accent": "#3EC1D3",
        "muted": "#7D8CA3",
        "font": "DejaVuSans.ttf",
    },
    "data": {
        "calendar": {"ics_url": "", "lookahead_days": 3, "timezone": "Europe/Amsterdam", "clock": "24h"},
        "news": {"rss_url": "https://feeds.bbci.co.uk/news/rss.xml", "limit": 3},
        "market": {"symbol": "VWCE", "provider": "mock"},
        "weather": {"lat": 52.3676, "lon": 4.9041},
    },
    "server": {"host": "0.0.0.0", "port": 8080},
}


class ConfigManager:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = os.path.join(self.base_dir, "config")
        self.settings_file = os.path.join(self.config_dir, "settings.yaml")
        os.makedirs(self.config_dir, exist_ok=True)
        self._settings: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.settings_file):
            self._settings = DEFAULT_SETTINGS.copy()
            self.save()
        else:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                self._settings = yaml.safe_load(f) or {}

        # Merge defaults for missing keys
        def merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
            out = dict(a)
            for k, v in b.items():
                if isinstance(v, dict):
                    out[k] = merge(out.get(k, {}), v)
                else:
                    out.setdefault(k, v)
            return out

        self._settings = merge(self._settings, DEFAULT_SETTINGS)

    def get(self, path: str, default: Any | None = None) -> Any:
        node: Any = self._settings
        for key in path.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, path: str, value: Any) -> None:
        keys = path.split(".")
        node = self._settings
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value

    def save(self) -> None:
        with open(self.settings_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._settings, f, sort_keys=False)

    @property
    def settings(self) -> Dict[str, Any]:
        return self._settings


