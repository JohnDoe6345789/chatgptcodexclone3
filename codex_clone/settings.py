from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


def get_settings_dir() -> Path:
    """Get platform-specific app data directory."""
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if not appdata:
            appdata = Path.home() / "AppData" / "Roaming"
        else:
            appdata = Path(appdata)
    else:
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            appdata = Path(xdg_config)
        else:
            appdata = Path.home() / ".config"
    
    settings_dir = appdata / "codex-portable"
    logger.debug(f"Settings directory: {settings_dir}")
    return settings_dir


def get_settings_file() -> Path:
    """Get path to settings YAML file."""
    return get_settings_dir() / "settings.yaml"


def load_settings() -> dict[str, Any]:
    """Load settings from YAML file, returning empty dict if file doesn't exist."""
    settings_file = get_settings_file()
    
    if not settings_file.exists():
        logger.debug(f"Settings file not found: {settings_file}")
        return {}
    
    if yaml is None:
        logger.warning("PyYAML not available, cannot load settings file")
        return {}
    
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f) or {}
        logger.info(f"Settings loaded from {settings_file}")
        return settings
    except Exception as exc:
        logger.error(f"Failed to load settings from {settings_file}: {exc}")
        return {}


def save_settings(settings: dict[str, Any]) -> None:
    """Save settings to YAML file."""
    if yaml is None:
        logger.warning("PyYAML not available, cannot save settings")
        return
    
    settings_file = get_settings_file()
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(settings, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Settings saved to {settings_file}")
    except Exception as exc:
        logger.error(f"Failed to save settings to {settings_file}: {exc}")
