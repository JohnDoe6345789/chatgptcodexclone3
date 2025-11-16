from __future__ import annotations

import os
import logging
from dataclasses import dataclass

from . import settings

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:1234"
DEFAULT_MODEL = "local-coder"
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful coding assistant. Focus on code, "
    "be concise, and always provide complete examples."
)
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2048


@dataclass
class Config:
    base_url: str
    api_key: str | None
    model: str
    system_prompt: str
    temperature: float
    max_tokens: int


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        logger.debug(f"Environment variable {name} not set, using default: {default}")
        return default
    logger.debug(f"Environment variable {name} set to: {value}")
    return value


def load_config() -> Config:
    logger.info("Loading configuration (env vars > saved settings > defaults)")
    
    saved_settings = settings.load_settings()
    logger.debug(f"Loaded {len(saved_settings)} saved settings")
    
    base_url = _get_env("CODEX_BASE_URL", saved_settings.get("base_url", DEFAULT_BASE_URL))
    api_key = os.getenv("CODEX_API_KEY") or saved_settings.get("api_key")
    model = _get_env("CODEX_MODEL", saved_settings.get("model", DEFAULT_MODEL))
    system_prompt = _get_env("CODEX_SYSTEM_PROMPT", saved_settings.get("system_prompt", DEFAULT_SYSTEM_PROMPT))
    
    temperature_str = _get_env("CODEX_TEMPERATURE", str(saved_settings.get("temperature", DEFAULT_TEMPERATURE)))
    max_tokens_str = _get_env("CODEX_MAX_TOKENS", str(saved_settings.get("max_tokens", DEFAULT_MAX_TOKENS)))
    
    temperature = float(temperature_str)
    max_tokens = int(max_tokens_str)
    
    config = Config(
        base_url=base_url,
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    logger.info(f"Configuration loaded: base_url={base_url}, model={model}, "
                f"temperature={temperature}, max_tokens={max_tokens}")
    
    return config


def save_config(config: Config) -> None:
    """Save configuration to YAML file."""
    saved_settings_dict = {
        "base_url": config.base_url,
        "api_key": config.api_key,
        "model": config.model,
        "system_prompt": config.system_prompt,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    settings.save_settings(saved_settings_dict)
    logger.info("Configuration saved")
