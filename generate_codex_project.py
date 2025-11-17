#!/usr/bin/env python3
"""
Project structure generator for Codex Portable Desktop.
Writes the entire multi-file project structure to disk with logging.
Run: python generate_codex_project.py
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Callable
import sys


def setup_logging(log_path: Path) -> None:
    """Configure logging with both file and console handlers."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='[%(levelname)s] %(message)s'
    )
    
    file_handler = logging.FileHandler(
        log_path,
        mode='w',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    root_logger.info("=" * 80)
    root_logger.info("Project Generator Started")
    root_logger.info(f"Log file: {log_path}")
    root_logger.info("=" * 80)


def generate_pyproject_toml():
    """pyproject.toml"""
    return '''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "codex-portable-socket-clean"
version = "1.3.0"
description = "Codex-style assistant with modern PyQt6 UI, socket daemon, clean shutdown, and logging"
authors = [{ name = "Local User" }]
requires-python = ">=3.10"
dependencies = [
    "PyQt6>=6.4.0",
    "PyYAML>=6.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["codex_clone*"]
'''

def generate_run_tests_py():
    """run_tests.py"""
    return '''from __future__ import annotations

import unittest


def main() -> int:
    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

def generate_run_tests_sh():
    """run_tests.sh"""
    return '''#!/usr/bin/env bash
set -euo pipefail
python run_tests.py
'''

def generate_run_tests_bat():
    """run_tests.bat"""
    return '''@echo off
python run_tests.py
'''

def generate_readme():
    """README.md"""
    return '''# Codex Portable Desktop

A local AI coding assistant with a modern PyQt6 GUI and automatic model management.

## Features

- **Automatic Setup**: Downloads and configures DeepSeek Coder 6.7B model
- **Socket-based Architecture**: Daemon process manages the backend independently
- **Modern UI**: Clean PyQt6 interface with syntax highlighting
- **Comprehensive Logging**: All operations logged to `codex.log`

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install PyQt6>=6.4.0
   ```

2. **Run the Application**:
   ```bash
   python codex_portable.py
   ```

3. **First Launch**:
   - The app will automatically install required packages
   - Download the model (one-time, ~4GB)
   - Start the local AI backend
   - This may take 5-10 minutes on first run

## Usage

- Type your coding questions in the input field
- Press Enter or click Send
- Use "Start Backend" / "Stop Backend" buttons to control the AI server
- Check `codex.log` for detailed operation logs

## Requirements

- Python 3.10+
- ~6GB free disk space (for model)
- 8GB+ RAM recommended

## Configuration

Set environment variables to customize:

```bash
export CODEX_BASE_URL="http://localhost:1234"
export CODEX_MODEL="local-coder"
export CODEX_TEMPERATURE="0.2"
export CODEX_MAX_TOKENS="2048"
```

## Testing

```bash
python run_tests.py
```

## Architecture

- `codex_portable.py` - PyQt6 GUI application
- `codex_clone/socket_backend.py` - Daemon server
- `codex_clone/backend_helper.py` - Model management and llama.cpp server
- `codex_clone/api.py` - OpenAI-compatible API client
- `codex_clone/config.py` - Configuration management
- `codex_clone/logging_utils.py` - Logging utilities

## Troubleshooting

**Backend won't start**: Check `codex.log` for errors. May need to install build tools for llama-cpp-python.

**Model download fails**: Check internet connection. Delete `models/` folder to retry.

**Port 1234 in use**: Change `CODEX_BASE_URL` to use a different port.

## License

MIT License - Free to use and modify.
'''

def generate_codex_clone_init():
    """codex_clone/__init__.py"""
    return '''"""Local ChatGPT/Codex-style coding assistant."""
'''

def generate_codex_clone_config():
    """codex_clone/config.py"""
    return '''from __future__ import annotations

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
'''

def generate_codex_clone_logging_utils():
    """codex_clone/logging_utils.py"""
    return '''from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_path: Path | None = None, level: int = logging.DEBUG) -> None:
    """Configure logging with both file and console handlers."""
    if log_path is None:
        log_path = Path(__file__).resolve().parent.parent / "codex.log"
    
    # Ensure log directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup
    root_logger.info("=" * 80)
    root_logger.info("Logging initialized")
    root_logger.info(f"Log file: {log_path}")
    root_logger.info("=" * 80)
'''

def generate_codex_clone_settings():
    """codex_clone/settings.py"""
    return '''from __future__ import annotations

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
'''

def generate_codex_clone_api():
    """codex_clone/api.py"""
    return '''from __future__ import annotations

from typing import Iterable, List, Dict

import json
import urllib.request
import urllib.error
import time
import logging

from .config import Config

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 10000
MAX_MESSAGES = 100
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0


class CodexError(RuntimeError):
    """Error raised when the HTTP API fails."""


def _validate_messages(messages: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    """Validate and sanitize messages."""
    msg_list = list(messages)
    
    if not msg_list:
        raise CodexError("Messages list cannot be empty")
    
    if len(msg_list) > MAX_MESSAGES:
        raise CodexError(f"Too many messages: {len(msg_list)} > {MAX_MESSAGES}")
    
    for i, msg in enumerate(msg_list):
        if not isinstance(msg, dict):
            raise CodexError(f"Message {i} is not a dict")
        
        if "role" not in msg or "content" not in msg:
            raise CodexError(f"Message {i} missing required fields (role, content)")
        
        content = msg.get("content", "")
        if not isinstance(content, str):
            raise CodexError(f"Message {i} content is not a string")
        
        if len(content) > MAX_MESSAGE_LENGTH:
            raise CodexError(f"Message {i} exceeds max length: {len(content)} > {MAX_MESSAGE_LENGTH}")
    
    logger.debug(f"Validated {len(msg_list)} messages")
    return msg_list


def _build_payload(
    messages: Iterable[Dict[str, str]],
    config: Config,
) -> bytes:
    msg_list = _validate_messages(messages)
    logger.debug(f"Building chat payload with {len(msg_list)} messages")
    
    payload = {
        "model": config.model,
        "messages": msg_list,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    
    logger.debug(f"Model: {config.model}, Temperature: {config.temperature}, "
                 f"Max tokens: {config.max_tokens}")
    
    text = json.dumps(payload)
    payload_bytes = text.encode("utf-8")
    
    logger.debug(f"Payload size: {len(payload_bytes)} bytes")
    
    return payload_bytes


def _build_request(
    payload: bytes,
    config: Config,
) -> urllib.request.Request:
    url = config.base_url.rstrip("/") + "/v1/chat/completions"
    
    logger.debug(f"Building HTTP POST request to {url}")
    
    request = urllib.request.Request(url, data=payload)
    request.add_header("Content-Type", "application/json")
    
    if config.api_key:
        request.add_header("Authorization", f"Bearer {config.api_key}")
        logger.debug("Authorization header added")
    else:
        logger.debug("No API key configured (local server mode)")
    
    return request


def _parse_response(data: bytes) -> str:
    logger.debug(f"Parsing response ({len(data)} bytes)")
    
    try:
        text = data.decode("utf-8")
        logger.debug(f"Response decoded successfully ({len(text)} characters)")
        
    except UnicodeDecodeError as exc:
        logger.error(f"Failed to decode response as UTF-8: {exc}")
        raise CodexError("Response is not valid UTF-8") from exc
    
    try:
        obj = json.loads(text)
        logger.debug("JSON parsed successfully")
        
    except json.JSONDecodeError as exc:
        logger.error(f"Invalid JSON from server: {exc}")
        logger.debug(f"Response preview: {text[:200]}...")
        raise CodexError("Invalid JSON from server") from exc
    
    if "error" in obj:
        error_msg = obj["error"]
        logger.error(f"Server returned error: {error_msg}")
        raise CodexError(f"Server error: {error_msg}")
    
    choices = obj.get("choices") or []
    logger.debug(f"Response contains {len(choices)} choices")
    
    if not choices:
        logger.error("Response contains no choices")
        raise CodexError("Response contains no choices")
    
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    
    if not isinstance(content, str):
        logger.error(f"Assistant content is not a string (type: {type(content).__name__})")
        raise CodexError("Assistant content is not a string")
    
    logger.debug(f"Content extracted: {len(content)} characters")
    
    if "usage" in obj:
        usage = obj["usage"]
        logger.info(f"Token usage: prompt={usage.get('prompt_tokens', '?')}, "
                   f"completion={usage.get('completion_tokens', '?')}, "
                   f"total={usage.get('total_tokens', '?')}")
    
    return content


def send_chat(
    messages: List[Dict[str, str]],
    config: Config,
) -> str:
    """Send a chat completion request to the local HTTP backend with retry logic."""
    logger.info("=" * 80)
    logger.info(f"Starting chat request with {len(messages)} messages")
    
    payload = _build_payload(messages, config)
    request = _build_request(payload, config)
    
    start_time = time.time()
    last_error = None
    backoff = INITIAL_BACKOFF
    
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                logger.debug(f"HTTP connection established (status: {response.code})")
                body = response.read()
                
                elapsed = time.time() - start_time
                logger.info(f"Response received in {elapsed:.2f} seconds")
                
        except urllib.error.HTTPError as exc:
            elapsed = time.time() - start_time
            logger.error(f"HTTP error after {elapsed:.2f}s: {exc.code} {exc.reason}")
            
            try:
                error_body = exc.read().decode('utf-8')
                logger.debug(f"Error response body: {error_body}")
            except (UnicodeDecodeError, OSError):
                pass
            
            if exc.code >= 500 and attempt < MAX_RETRIES - 1:
                logger.warning(f"Server error (attempt {attempt + 1}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            
            raise CodexError(f"HTTP {exc.code}: {exc.reason}") from exc
            
        except urllib.error.URLError as exc:
            elapsed = time.time() - start_time
            logger.error(f"URL error after {elapsed:.2f}s: {exc}")
            
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Connection error (attempt {attempt + 1}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            
            raise CodexError(f"Connection failed: {exc.reason}") from exc
            
        except (OSError, TimeoutError) as exc:
            elapsed = time.time() - start_time
            logger.error(f"Network error after {elapsed:.2f}s: {exc}")
            
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Network error (attempt {attempt + 1}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            
            raise CodexError(f"Network error: {exc}") from exc
        
        reply = _parse_response(body)
        
        total_elapsed = time.time() - start_time
        logger.info(f"Chat request completed in {total_elapsed:.2f} seconds")
        logger.debug(f"Reply preview: {reply[:100]}...")
        logger.info("=" * 80)
        
        return reply
    
    if last_error:
        raise last_error
    raise CodexError("Unknown error: request failed after retries")
'''

def generate_codex_clone_backend_helper():
    """codex_clone/backend_helper.py"""
    return '''from __future__ import annotations

import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

HF_REPO: Final[str] = "TheBloke/deepseek-coder-6.7B-instruct-GGUF"
HF_FILE: Final[str] = "deepseek-coder-6.7b-instruct.Q4_K_M.gguf"


def project_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    logger.debug(f"Project root: {root}")
    return root


def models_dir() -> Path:
    directory = project_root() / "models"
    logger.debug(f"Models directory: {directory}")
    
    if not directory.exists():
        logger.info("Creating models directory...")
        directory.mkdir(parents=True, exist_ok=True)
        logger.info("Models directory created")
    
    return directory


def ensure_huggingface_hub() -> bool:
    logger.info("Checking for huggingface_hub module...")
    
    try:
        import huggingface_hub
        logger.info(f"huggingface_hub is already installed (version: {huggingface_hub.__version__})")
        return True
    except ImportError:
        logger.warning("huggingface_hub not found, will install")
    
    max_retries = 3
    for attempt in range(max_retries):
        logger.info("=" * 80)
        logger.info(f"Installing huggingface_hub>=0.25.0 (attempt {attempt + 1}/{max_retries})")
        logger.info("=" * 80)
        
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "huggingface_hub>=0.25.0"],
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start_time
        
        logger.info(f"pip install completed in {elapsed:.2f} seconds (return code: {result.returncode})")
        
        if result.stdout:
            for line in result.stdout.split('\n')[-20:]:
                if line.strip():
                    logger.debug(f"  {line}")
        
        if result.returncode == 0:
            logger.info("huggingface_hub installation successful")
            return True
        else:
            logger.warning(f"pip install returned non-zero code: {result.returncode}")
            if result.stderr:
                for line in result.stderr.split('\n')[-10:]:
                    if line.strip():
                        logger.error(f"  {line}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    logger.error("Failed to install huggingface_hub after all retries")
    return False


def download_model() -> Path:
    logger.info("=" * 80)
    logger.info("MODEL DOWNLOAD PHASE")
    logger.info("=" * 80)
    
    if not ensure_huggingface_hub():
        raise RuntimeError("Failed to install huggingface_hub")
    
    from huggingface_hub import hf_hub_download

    dest_dir = models_dir()
    local_path = dest_dir / HF_FILE
    
    logger.info(f"Target model file: {local_path}")
    
    if local_path.exists():
        file_size_mb = local_path.stat().st_size / (1024 * 1024)
        logger.info(f"Model already present: {local_path} ({file_size_mb:.2f} MB)")
        return local_path
    
    logger.info(f"Model not found locally, starting download...")
    logger.info(f"Repository: {HF_REPO}")
    logger.info(f"Filename: {HF_FILE}")
    logger.info("NOTE: First download may take several minutes (model is ~4GB)")
    
    start_time = time.time()
    
    try:
        actual = hf_hub_download(
            repo_id=HF_REPO,
            filename=HF_FILE,
            local_dir=str(dest_dir),
            local_dir_use_symlinks=False,
        )
        
        elapsed = time.time() - start_time
        local_path = Path(actual)
        file_size_mb = local_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"Download completed in {elapsed:.2f} seconds")
        logger.info(f"Model saved to: {local_path} ({file_size_mb:.2f} MB)")
        
    except Exception as exc:
        logger.error(f"Model download failed: {exc}", exc_info=True)
        raise
    
    return local_path


def have_llama_server() -> bool:
    logger.debug("Checking for llama_cpp.server module...")
    
    try:
        import llama_cpp.server
        import llama_cpp
        logger.info(f"llama-cpp-python is installed (version: {llama_cpp.__version__})")
        return True
    except ImportError:
        logger.debug("llama_cpp.server not found")
        return False


def ensure_llama_cpp() -> bool:
    logger.info("=" * 80)
    logger.info("LLAMA-CPP-PYTHON CHECK")
    logger.info("=" * 80)
    
    if have_llama_server():
        logger.info("llama-cpp-python[server] is already available")
        return True
    
    logger.info("llama-cpp-python[server] not found, installing...")
    logger.warning("NOTE: This may take several minutes and may require compilation")
    
    max_retries = 2
    for attempt in range(max_retries):
        logger.info(f"Installation attempt {attempt + 1}/{max_retries}")
        
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "llama-cpp-python[server]"],
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start_time
        
        logger.info(f"pip install completed in {elapsed:.2f} seconds (return code: {result.returncode})")
        
        if result.stdout:
            for line in result.stdout.split('\\n')[-30:]:
                if line.strip():
                    logger.debug(f"  {line}")
        
        if result.returncode == 0:
            if have_llama_server():
                logger.info("llama-cpp-python[server] installation successful")
                return True
            else:
                logger.warning("Installation succeeded but module check failed, retrying...")
        else:
            logger.warning(f"pip install returned non-zero code: {result.returncode}")
            if result.stderr:
                for line in result.stderr.split('\\n')[-20:]:
                    if line.strip():
                        logger.error(f"  {line}")
        
        if attempt < max_retries - 1:
            wait_time = 10
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    logger.warning("Could not install llama-cpp-python[server]")
    logger.info("You may need to:")
    logger.info("  1. Install build tools (Visual Studio on Windows, gcc on Linux)")
    logger.info("  2. Use LM Studio or another OpenAI-compatible backend manually")
    logger.info("  3. Check your Python version (3.10+ recommended)")
    return False


def run_llama_server(model_path: Path) -> int:
    logger.info("=" * 80)
    logger.info("STARTING LLAMA SERVER")
    logger.info("=" * 80)
    
    cmd = [
        sys.executable,
        "-m",
        "llama_cpp.server",
        "--model",
        str(model_path),
        "--model_alias",
        "local-coder",
        "--host",
        "127.0.0.1",
        "--port",
        "1234",
        "--n_ctx",
        "8192",
    ]
    
    logger.info(f"Command: {' '.join(cmd)}")
    logger.info(f"Model: {model_path}")
    logger.info("Host: 127.0.0.1:1234")
    logger.info("Context size: 8192 tokens")
    logger.info("Starting llama_cpp.server (this may take 30-60 seconds)...")
    logger.info("=" * 80)
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    
    logger.info(f"Server process started with PID: {proc.pid}")
    
    if proc.stdout is None:
        logger.error("Failed to open stdout from server process")
        proc.terminate()
        proc.wait()
        raise RuntimeError("Could not read server output")
    
    line_count = 0
    max_line_buffer = 1000000
    total_bytes = 0
    
    try:
        for line in proc.stdout:
            line_count += 1
            total_bytes += len(line.encode('utf-8'))
            
            if total_bytes > max_line_buffer:
                logger.warning(f"Server output exceeded {max_line_buffer} bytes, stopping read")
                break
            
            msg = line.rstrip()
            print(f"[llama] {msg}", flush=True)
            
            if line_count % 10 == 0 or any(k in line.lower() for k in ['error', 'warn', 'ready', 'listening']):
                logger.debug(f"[llama-server] {msg}")
    
    except Exception as exc:
        logger.error(f"Error reading server output: {exc}", exc_info=True)
    
    logger.info("=" * 80)
    logger.info("Server output stream ended, waiting for process exit...")
    
    code = proc.wait()
    
    logger.info(f"llama_cpp.server exited with code {code} (processed {line_count} output lines)")
    
    return code


def main() -> int:
    from .logging_utils import setup_logging
    setup_logging()
    
    logger.info("=" * 80)
    logger.info("BACKEND HELPER STARTING")
    logger.info("=" * 80)
    logger.info(f"Python: {sys.version}")
    logger.info(f"Executable: {sys.executable}")
    logger.info(f"PID: {sys.getpid()}")
    logger.info(f"Working directory: {Path.cwd()}")
    
    try:
        logger.info("Phase 1: Download/verify model...")
        model_path = download_model()
        logger.info(f"Phase 1 complete: model at {model_path}")
        
    except Exception as exc:
        logger.critical(f"FATAL: model download failed: {exc}", exc_info=True)
        return 1
    
    try:
        logger.info("Phase 2: Ensure llama-cpp-python is installed...")
        if not ensure_llama_cpp():
            logger.warning("Phase 2 failed: llama-cpp-python not available")
            logger.info("Exiting without starting backend")
            return 0
        logger.info("Phase 2 complete: llama-cpp-python ready")
        
    except Exception as exc:
        logger.error(f"Error in Phase 2: {exc}", exc_info=True)
        return 1
    
    try:
        logger.info("Phase 3: Start llama.cpp server...")
        rc = run_llama_server(model_path)
        logger.info(f"Phase 3 complete: server exited with code {rc}")
        
    except Exception as exc:
        logger.error(f"Error in Phase 3: {exc}", exc_info=True)
        return 1
    
    logger.info("=" * 80)
    logger.info("BACKEND HELPER SHUTTING DOWN")
    logger.info("=" * 80)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
'''

def generate_codex_clone_backend():
    """codex_clone/backend.py"""
    return '''from __future__ import annotations

import subprocess
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Backend:
    def __init__(self) -> None:
        self._proc: subprocess.Popen[str] | None = None
        logger.debug("Backend instance created")
    
    def is_running(self) -> bool:
        if self._proc is None:
            return False
        
        poll_result = self._proc.poll()
        running = poll_result is None
        
        if not running and poll_result is not None:
            logger.debug(f"Backend process has exited with code {poll_result}")
        
        return running
    
    def start(self, log_callback=None) -> None:
        if self.is_running():
            logger.warning("Backend already running, ignoring start request")
            if log_callback:
                log_callback("Backend is already running")
            return
        
        logger.info("=" * 80)
        logger.info("STARTING BACKEND")
        logger.info("=" * 80)
        
        if log_callback:
            log_callback("Starting backend process...")
        
        cmd = [
            sys.executable,
            "-m",
            "codex_clone.backend_helper",
        ]
        
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info(f"Working directory: {Path.cwd()}")
        
        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            
            logger.info(f"Backend process started with PID: {self._proc.pid}")
            
            if log_callback:
                log_callback(f"Backend process started (PID: {self._proc.pid})")
            
        except Exception as exc:
            logger.error(f"Failed to start backend: {exc}", exc_info=True)
            if log_callback:
                log_callback(f"ERROR: Failed to start backend: {exc}")
            raise
    
    def stop(self, log_callback=None) -> None:
        if not self.is_running():
            logger.info("Backend is not running, nothing to stop")
            if log_callback:
                log_callback("Backend is not running")
            return
        
        logger.info("=" * 80)
        logger.info("STOPPING BACKEND")
        logger.info("=" * 80)
        
        if log_callback:
            log_callback("Stopping backend process...")
        
        assert self._proc is not None
        pid = self._proc.pid
        
        logger.info(f"Terminating process {pid}...")
        
        try:
            self._proc.terminate()
            
            logger.info("Waiting for process to exit (timeout: 10 seconds)...")
            
            try:
                exit_code = self._proc.wait(timeout=10)
                logger.info(f"Process {pid} exited with code {exit_code}")
                
                if log_callback:
                    log_callback(f"Backend stopped (exit code: {exit_code})")
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {pid} did not exit after 10 seconds, forcing kill...")
                self._proc.kill()
                exit_code = self._proc.wait()
                logger.info(f"Process {pid} killed (exit code: {exit_code})")
                
                if log_callback:
                    log_callback(f"Backend forcefully stopped (exit code: {exit_code})")
        
        except Exception as exc:
            logger.error(f"Error stopping backend: {exc}", exc_info=True)
            if log_callback:
                log_callback(f"ERROR: Failed to stop backend: {exc}")
            raise
        
        finally:
            self._proc = None
            logger.info("Backend process reference cleared")
'''

def generate_codex_clone_socket_backend():
    """codex_clone/socket_backend.py"""
    return '''from __future__ import annotations

import socket
import json
import logging
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

from .backend import Backend
from .config import load_config
from .api import send_chat, CodexError

logger = logging.getLogger(__name__)

HOST: str = "127.0.0.1"
PORT: int = 9876
MAX_WORKERS: int = 10


class SocketBackendServer:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._backend = Backend()
        self._config = load_config()
        self._shutdown_flag = False
        self._executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
        logger.info(f"SocketBackendServer initialized (host={host}, port={port}, max_workers={MAX_WORKERS})")
    
    def _request_shutdown(self) -> None:
        logger.info("Shutdown requested by client")
        self._shutdown_flag = True
    
    def serve_forever(self) -> None:
        logger.info("=" * 80)
        logger.info("SOCKET BACKEND SERVER STARTING")
        logger.info("=" * 80)
        logger.info(f"Binding to {self._host}:{self._port}")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((self._host, self._port))
                sock.listen(5)
                
                logger.info(f"Listening on {self._host}:{self._port}")
                logger.info("Waiting for connections...")
                
                while not self._shutdown_flag:
                    sock.settimeout(1.0)
                    
                    try:
                        conn, addr = sock.accept()
                        logger.info(f"Connection received from {addr}")
                        
                        self._executor.submit(self._handle_client, conn, addr)
                        
                    except socket.timeout:
                        continue
                    except Exception as exc:
                        logger.error(f"Error accepting connection: {exc}", exc_info=True)
                        break
        finally:
            logger.info("Shutting down thread pool executor...")
            self._executor.shutdown(wait=True)
            logger.info("=" * 80)
            logger.info("SOCKET BACKEND SERVER SHUTTING DOWN")
            logger.info("=" * 80)
    
    def _handle_chat(self, messages: list, req_id: str, client_id: str, send: Callable) -> None:
        try:
            reply = send_chat(messages, self._config)
            send({
                "type": "chat_reply",
                "id": req_id,
                "ok": True,
                "content": reply,
            })
        except CodexError as exc:
            logger.error(f"[Client {client_id}] Chat error: {exc}")
            send({
                "type": "chat_reply",
                "id": req_id,
                "ok": False,
                "error": str(exc),
            })
    
    def _handle_client(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        client_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"[Client {client_id}] Connected")
        
        def send(data: dict[str, Any]) -> None:
            try:
                message = json.dumps(data) + "\n"
                conn.sendall(message.encode("utf-8"))
                logger.debug(f"[Client {client_id}] Sent: {data.get('type', '?')}")
            except Exception as exc:
                logger.error(f"[Client {client_id}] Send error: {exc}")
        
        def log_callback(msg: str) -> None:
            logger.info(f"[Backend] {msg}")
            send({"type": "log", "message": msg})
        
        buffer = ""
        
        try:
            while True:
                chunk = conn.recv(4096).decode("utf-8")
                if not chunk:
                    logger.info(f"[Client {client_id}] Connection closed by client")
                    break
                
                buffer += chunk
                
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError as exc:
                        logger.error(f"[Client {client_id}] Invalid JSON: {exc}")
                        send({"type": "error", "message": "Invalid JSON"})
                        continue
                    
                    mtype = msg.get("type")
                    logger.debug(f"[Client {client_id}] Received: {mtype}")
                    
                    if mtype == "ping":
                        send({"type": "pong"})
                        
                    elif mtype == "start_backend":
                        self._executor.submit(self._backend.start, log_callback)
                        send({"type": "start_backend_ack"})
                        
                    elif mtype == "stop_backend":
                        self._executor.submit(self._backend.stop, log_callback)
                        send({"type": "stop_backend_ack"})
                        
                    elif mtype == "status":
                        running = self._backend.is_running()
                        send({"type": "status", "running": running})
                        
                    elif mtype == "chat":
                        messages = msg.get("messages") or []
                        req_id = msg.get("id", "")
                        logger.info(f"[Client {client_id}] Chat request {req_id} ({len(messages)} messages)")
                        
                        self._executor.submit(self._handle_chat, messages, req_id, client_id, send)
                        
                    elif mtype == "shutdown":
                        logger.info(f"[Client {client_id}] Shutdown requested")
                        self._backend.stop(log_callback)
                        send({"type": "shutdown_ack"})
                        self._request_shutdown()
                        break
            
        except Exception as exc:
            logger.error(f"[Client {client_id}] Exception: {exc}", exc_info=True)
            
        finally:
            conn.close()
            logger.info(f"[Client {client_id}] Disconnected")


def main() -> int:
    from .logging_utils import setup_logging
    setup_logging()
    
    logger.info("DAEMON MAIN() CALLED")
    
    server = SocketBackendServer(HOST, PORT)
    server.serve_forever()
    
    logger.info("DAEMON MAIN() EXITING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

def generate_codex_portable():
    """codex_portable.py"""
    return '''#!/usr/bin/env python3
from __future__ import annotations

import sys
import socket
import json
import uuid
import logging
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QFormLayout,
        QTextEdit,
        QLineEdit,
        QSpinBox,
        QDoubleSpinBox,
        QPushButton,
        QLabel,
        QTabWidget,
        QStatusBar,
        QGroupBox,
    )
    from PyQt6.QtCore import QThread, pyqtSignal, Qt
    from PyQt6.QtGui import QFont, QTextCursor, QPalette, QColor
except ImportError:
    print("ERROR: PyQt6 not found. Please install it:")
    print("  pip install PyQt6>=6.4.0")
    sys.exit(1)

from codex_clone.logging_utils import setup_logging

logger = logging.getLogger(__name__)


class SocketClient(QThread):
    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool, str)
    
    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._sock: socket.socket | None = None
        self._running = False
        logger.debug(f"SocketClient initialized (host={host}, port={port})")
    
    def run(self) -> None:
        logger.info("SocketClient thread starting...")
        self._running = True
        
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info(f"Connecting to {self._host}:{self._port}...")
            self._sock.connect((self._host, self._port))
            logger.info("Connected to socket backend")
            self.connection_status.emit(True, "Connected")
            
            buffer = ""
            
            while self._running:
                try:
                    chunk = self._sock.recv(4096).decode("utf-8")
                    if not chunk:
                        logger.warning("Server closed connection")
                        break
                    
                    buffer += chunk
                    
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        
                        if not line:
                            continue
                        
                        try:
                            msg = json.loads(line)
                            logger.debug(f"Received message: {msg.get('type', '?')}")
                            self.message_received.emit(msg)
                        except json.JSONDecodeError as exc:
                            logger.error(f"Invalid JSON from server: {exc}")
                
                except Exception as exc:
                    if self._running:
                        logger.error(f"Socket error: {exc}")
                    break
        
        except Exception as exc:
            logger.error(f"Connection failed: {exc}")
            self.connection_status.emit(False, f"Connection failed: {exc}")
        
        finally:
            if self._sock:
                self._sock.close()
            logger.info("SocketClient thread exiting")
            self.connection_status.emit(False, "Disconnected")
    
    def send_message(self, data: dict) -> None:
        if not self._sock:
            logger.warning("Cannot send message: not connected")
            return
        
        try:
            message = json.dumps(data) + "\\n"
            self._sock.sendall(message.encode("utf-8"))
            logger.debug(f"Sent message: {data.get('type', '?')}")
        except Exception as exc:
            logger.error(f"Failed to send message: {exc}")
    
    def stop(self) -> None:
        logger.info("Stopping SocketClient...")
        self._running = False
        if self._sock:
            try:
                self._sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass


class CodexWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._client: SocketClient | None = None
        self._pending_requests: dict[str, bool] = {}
        self._backend_status = "Unknown"
        self._connection_status = "Disconnected"
        
        self.setWindowTitle("Codex Portable Desktop")
        self.setGeometry(100, 100, 1100, 800)
        
        self._setup_ui()
        self._apply_dark_theme()
        
        logger.info("CodexWindow initialized")
    
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2c2f33;
                background: #36393f;
            }
            QTabBar::tab {
                background: #2c2f33;
                color: #dcddde;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #23272a;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #36393f;
                color: #ffffff;
                border-bottom: 2px solid #5865f2;
            }
            QTabBar::tab:hover {
                background: #3c3f44;
            }
        """)
        
        self._tabs.addTab(self._create_chat_tab(), "💬 Chat")
        self._tabs.addTab(self._create_settings_tab(), "⚙️ Settings")
        
        main_layout.addWidget(self._tabs)
        
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet("""
            QStatusBar {
                background: #2c2f33;
                color: #dcddde;
                border-top: 1px solid #23272a;
                padding: 4px;
                font-size: 12px;
            }
        """)
        self._update_status_bar()
        self.setStatusBar(self._status_bar)
    
    def _create_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        model_group = QGroupBox("AI Model Management")
        model_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #5865f2;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        model_layout = QVBoxLayout()
        
        info_label = QLabel("DeepSeek Coder 6.7B (Auto-installed on first start)")
        info_label.setStyleSheet("color: #b9bbbe; font-size: 12px; padding: 5px;")
        model_layout.addWidget(info_label)
        
        btn_layout = QHBoxLayout()
        
        self._start_backend_btn = QPushButton("▶️ Start AI Backend")
        self._start_backend_btn.clicked.connect(self._on_start_backend)
        self._start_backend_btn.setStyleSheet(self._get_button_style("#43b581"))
        self._start_backend_btn.setMinimumHeight(40)
        btn_layout.addWidget(self._start_backend_btn)
        
        self._stop_backend_btn = QPushButton("⏹️ Stop AI Backend")
        self._stop_backend_btn.clicked.connect(self._on_stop_backend)
        self._stop_backend_btn.setStyleSheet(self._get_button_style("#f04747"))
        self._stop_backend_btn.setMinimumHeight(40)
        btn_layout.addWidget(self._stop_backend_btn)
        
        self._check_status_btn = QPushButton("🔍 Check Status")
        self._check_status_btn.clicked.connect(self._on_check_status)
        self._check_status_btn.setStyleSheet(self._get_button_style("#5865f2"))
        self._check_status_btn.setMinimumHeight(40)
        btn_layout.addWidget(self._check_status_btn)
        
        model_layout.addLayout(btn_layout)
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        conn_group = QGroupBox("Socket Backend Connection")
        conn_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #5865f2;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        conn_layout = QVBoxLayout()
        
        info_label = QLabel("Connect to socket backend daemon (127.0.0.1:9876)")
        info_label.setStyleSheet("color: #b9bbbe; font-size: 12px; padding: 5px;")
        conn_layout.addWidget(info_label)
        
        btn_layout = QHBoxLayout()
        
        self._connect_btn = QPushButton("🔗 Connect to Backend")
        self._connect_btn.clicked.connect(self._on_connect)
        self._connect_btn.setStyleSheet(self._get_button_style("#43b581"))
        self._connect_btn.setMinimumHeight(40)
        btn_layout.addWidget(self._connect_btn)
        
        self._disconnect_btn = QPushButton("🔌 Disconnect")
        self._disconnect_btn.clicked.connect(self._on_disconnect)
        self._disconnect_btn.setStyleSheet(self._get_button_style("#f04747"))
        self._disconnect_btn.setMinimumHeight(40)
        self._disconnect_btn.setEnabled(False)
        btn_layout.addWidget(self._disconnect_btn)
        
        conn_layout.addLayout(btn_layout)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        output_group = QGroupBox("Backend Logs")
        output_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #5865f2;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        output_layout = QVBoxLayout()
        
        self._backend_output = QTextEdit()
        self._backend_output.setReadOnly(True)
        self._backend_output.setFont(QFont("Consolas", 10))
        self._backend_output.setStyleSheet("""
            QTextEdit {
                background: #2c2f33;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        output_layout.addWidget(self._backend_output)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        config_group = QGroupBox("Configuration Settings")
        config_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #5865f2;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        config_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self._base_url_input = QLineEdit()
        self._base_url_input.setStyleSheet("""
            QLineEdit {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #5865f2;
            }
        """)
        form_layout.addRow("Base URL:", self._base_url_input)
        
        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_input.setStyleSheet("""
            QLineEdit {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #5865f2;
            }
        """)
        form_layout.addRow("API Key:", self._api_key_input)
        
        self._model_input = QLineEdit()
        self._model_input.setStyleSheet("""
            QLineEdit {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #5865f2;
            }
        """)
        form_layout.addRow("Model:", self._model_input)
        
        temp_layout = QHBoxLayout()
        self._temperature_input = QDoubleSpinBox()
        self._temperature_input.setMinimum(0.0)
        self._temperature_input.setMaximum(2.0)
        self._temperature_input.setSingleStep(0.1)
        self._temperature_input.setStyleSheet("""
            QDoubleSpinBox {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        temp_layout.addWidget(self._temperature_input)
        temp_layout.addStretch()
        form_layout.addRow("Temperature (0.0-2.0):", temp_layout)
        
        tokens_layout = QHBoxLayout()
        self._max_tokens_input = QSpinBox()
        self._max_tokens_input.setMinimum(1)
        self._max_tokens_input.setMaximum(32768)
        self._max_tokens_input.setSingleStep(256)
        self._max_tokens_input.setStyleSheet("""
            QSpinBox {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        tokens_layout.addWidget(self._max_tokens_input)
        tokens_layout.addStretch()
        form_layout.addRow("Max Tokens:", tokens_layout)
        
        self._system_prompt_input = QTextEdit()
        self._system_prompt_input.setMinimumHeight(80)
        self._system_prompt_input.setStyleSheet("""
            QTextEdit {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        form_layout.addRow("System Prompt:", self._system_prompt_input)
        
        config_layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton("↻ Load Defaults")
        load_btn.clicked.connect(self._on_load_defaults)
        load_btn.setStyleSheet(self._get_button_style("#5865f2"))
        load_btn.setMinimumHeight(35)
        btn_layout.addWidget(load_btn)
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self._on_save_settings)
        save_btn.setStyleSheet(self._get_button_style("#43b581"))
        save_btn.setMinimumHeight(35)
        btn_layout.addWidget(save_btn)
        
        config_layout.addLayout(btn_layout)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        self._load_settings_to_ui()
        
        return tab
    
    def _create_chat_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        chat_group = QGroupBox("AI Chat Interface")
        chat_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #5865f2;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        chat_layout = QVBoxLayout()
        
        self._chat_output = QTextEdit()
        self._chat_output.setReadOnly(True)
        self._chat_output.setFont(QFont("Consolas", 10))
        self._chat_output.setStyleSheet("""
            QTextEdit {
                background: #2c2f33;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        chat_layout.addWidget(self._chat_output)
        
        input_layout = QHBoxLayout()
        
        self._chat_input = QLineEdit()
        self._chat_input.setPlaceholderText("Type your coding question here...")
        self._chat_input.returnPressed.connect(self._on_send_chat)
        self._chat_input.setStyleSheet("""
            QLineEdit {
                background: #40444b;
                color: #dcddde;
                border: 1px solid #23272a;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #5865f2;
            }
        """)
        self._chat_input.setMinimumHeight(40)
        input_layout.addWidget(self._chat_input)
        
        send_btn = QPushButton("📤 Send")
        send_btn.clicked.connect(self._on_send_chat)
        send_btn.setStyleSheet(self._get_button_style("#5865f2"))
        send_btn.setMinimumHeight(40)
        send_btn.setMinimumWidth(100)
        input_layout.addWidget(send_btn)
        
        chat_layout.addLayout(input_layout)
        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)
        
        return tab
    
    def _get_button_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background: {color};
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color)};
            }}
            QPushButton:disabled {{
                background: #4f545c;
                color: #72767d;
            }}
        """
    
    def _lighten_color(self, hex_color: str) -> str:
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(min(int(c * 1.2), 255) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except Exception:
            return hex_color
    
    def _darken_color(self, hex_color: str) -> str:
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            rgb = tuple(max(int(c * 0.8), 0) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        except Exception:
            return hex_color
    
    def _apply_dark_theme(self) -> None:
        self.setStyleSheet("""
            QMainWindow {
                background: #36393f;
            }
            QWidget {
                background: #36393f;
                color: #dcddde;
            }
        """)
    
    def _update_status_bar(self) -> None:
        status_text = f"Backend: {self._backend_status} | Connection: {self._connection_status}"
        self._status_bar.showMessage(status_text)
    
    def _load_settings_to_ui(self) -> None:
        from codex_clone.config import load_config, DEFAULT_BASE_URL, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
        
        config = load_config()
        
        self._base_url_input.setText(config.base_url or DEFAULT_BASE_URL)
        self._api_key_input.setText(config.api_key or "")
        self._model_input.setText(config.model or DEFAULT_MODEL)
        self._temperature_input.setValue(float(config.temperature or DEFAULT_TEMPERATURE))
        self._max_tokens_input.setValue(int(config.max_tokens or DEFAULT_MAX_TOKENS))
        self._system_prompt_input.setText(config.system_prompt or DEFAULT_SYSTEM_PROMPT)
        
        logger.info("Settings loaded to UI")
    
    def _on_load_defaults(self) -> None:
        from codex_clone.config import DEFAULT_BASE_URL, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
        
        self._base_url_input.setText(DEFAULT_BASE_URL)
        self._api_key_input.setText("")
        self._model_input.setText(DEFAULT_MODEL)
        self._temperature_input.setValue(DEFAULT_TEMPERATURE)
        self._max_tokens_input.setValue(DEFAULT_MAX_TOKENS)
        self._system_prompt_input.setText(DEFAULT_SYSTEM_PROMPT)
        
        self._append_chat_output("[System] Default settings loaded\\n", "#faa61a")
        logger.info("Default settings loaded")
    
    def _on_save_settings(self) -> None:
        from codex_clone.config import Config, save_config
        
        config = Config(
            base_url=self._base_url_input.text() or "http://localhost:1234",
            api_key=self._api_key_input.text() or None,
            model=self._model_input.text() or "local-coder",
            system_prompt=self._system_prompt_input.toPlainText(),
            temperature=float(self._temperature_input.value()),
            max_tokens=int(self._max_tokens_input.value()),
        )
        
        save_config(config)
        self._append_chat_output("[System] Settings saved successfully\\n", "#43b581")
        logger.info("Settings saved")
    
    def _on_connect(self) -> None:
        logger.info("User requested to connect to backend")
        self._append_chat_output("[System] Connecting to backend daemon...\\n", "#faa61a")
        self._start_socket_client()
        self._connect_btn.setEnabled(False)
    
    def _on_disconnect(self) -> None:
        logger.info("User requested to disconnect from backend")
        if self._client:
            self._client.stop()
            self._client.wait(2000)
            self._client = None
        self._connection_status = "Disconnected"
        self._update_status_bar()
        self._append_chat_output("[System] Disconnected from backend\\n", "#f04747")
        self._connect_btn.setEnabled(True)
        self._disconnect_btn.setEnabled(False)
    
    def _start_socket_client(self) -> None:
        logger.info("Starting socket client thread...")
        self._client = SocketClient("127.0.0.1", 9876)
        self._client.message_received.connect(self._on_message_received)
        self._client.connection_status.connect(self._on_connection_status)
        self._client.start()
    
    def _on_connection_status(self, connected: bool, message: str) -> None:
        logger.info(f"Connection status: {message}")
        self._connection_status = "Connected" if connected else "Disconnected"
        self._update_status_bar()
        
        if connected:
            self._append_chat_output("[System] ✅ Connected to backend daemon\\n", "#43b581")
            self._disconnect_btn.setEnabled(True)
            self._connect_btn.setEnabled(False)
        else:
            self._append_chat_output(f"[System] ❌ {message}\\n", "#f04747")
            self._disconnect_btn.setEnabled(False)
            self._connect_btn.setEnabled(True)
    
    def _on_message_received(self, msg: dict) -> None:
        mtype = msg.get("type")
        
        if mtype == "log":
            log_msg = msg.get("message", "")
            self._append_backend_output(f"[Backend] {log_msg}\\n", "#72767d")
        
        elif mtype == "chat_reply":
            req_id = msg.get("id", "")
            ok = msg.get("ok", False)
            
            if req_id in self._pending_requests:
                del self._pending_requests[req_id]
            
            if ok:
                content = msg.get("content", "")
                self._append_chat_output(f"\\n[🤖 Assistant]\\n{content}\\n\\n", "#43b581")
            else:
                error = msg.get("error", "Unknown error")
                self._append_chat_output(f"[❌ Error] {error}\\n", "#f04747")
        
        elif mtype == "status":
            running = msg.get("running", False)
            self._backend_status = "Running" if running else "Stopped"
            self._update_status_bar()
            status_text = "✅ Running" if running else "⏹️ Stopped"
            self._append_backend_output(f"[Status] Backend is {status_text}\\n", "#5865f2")
    
    def _append_backend_output(self, text: str, color: str) -> None:
        cursor = self._backend_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._backend_output.setTextCursor(cursor)
        self._backend_output.setTextColor(QColor(color))
        self._backend_output.insertPlainText(text)
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._backend_output.setTextCursor(cursor)
    
    def _append_chat_output(self, text: str, color: str) -> None:
        cursor = self._chat_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._chat_output.setTextCursor(cursor)
        self._chat_output.setTextColor(QColor(color))
        self._chat_output.insertPlainText(text)
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._chat_output.setTextCursor(cursor)
    
    def _on_start_backend(self) -> None:
        logger.info("User requested to start backend")
        if self._client:
            self._client.send_message({"type": "start_backend"})
            self._append_backend_output("[System] ▶️ Starting AI backend...\\n", "#faa61a")
        else:
            self._append_backend_output("[Error] Not connected to daemon. Go to Backend Connection tab.\\n", "#f04747")
    
    def _on_stop_backend(self) -> None:
        logger.info("User requested to stop backend")
        if self._client:
            self._client.send_message({"type": "stop_backend"})
            self._append_backend_output("[System] ⏹️ Stopping AI backend...\\n", "#faa61a")
        else:
            self._append_backend_output("[Error] Not connected to daemon. Go to Backend Connection tab.\\n", "#f04747")
    
    def _on_check_status(self) -> None:
        logger.info("User requested backend status check")
        if self._client:
            self._client.send_message({"type": "status"})
        else:
            self._append_backend_output("[Error] Not connected to daemon. Go to Backend Connection tab.\\n", "#f04747")
    
    def _on_send_chat(self) -> None:
        user_input = self._chat_input.text().strip()
        
        if not user_input:
            return
        
        if not self._client:
            self._append_chat_output("[Error] Not connected to backend. Connect first!\\n", "#f04747")
            return
        
        logger.info(f"User sent message: {user_input[:50]}...")
        
        self._append_chat_output(f"[💬 You] {user_input}\\n", "#5865f2")
        self._chat_input.clear()
        
        req_id = str(uuid.uuid4())
        self._pending_requests[req_id] = True
        
        messages = [
            {"role": "system", "content": "You are a helpful coding assistant. Focus on code, be concise, and always provide complete examples."},
            {"role": "user", "content": user_input}
        ]
        
        self._client.send_message({
            "type": "chat",
            "id": req_id,
            "messages": messages
        })
        self._append_chat_output("[⏳ System] Processing request...\\n", "#72767d")
    
    def closeEvent(self, event) -> None:
        logger.info("Window closing, shutting down client...")
        
        try:
            if self._client:
                logger.info("Stopping socket client...")
                self._client.stop()
                
                if not self._client.wait(5000):
                    logger.warning("Socket client did not stop within 5 seconds")
                
                logger.info("Socket client stopped successfully")
        except Exception as exc:
            logger.error(f"Error during client shutdown: {exc}", exc_info=True)
        finally:
            self._client = None
            event.accept()
            logger.info("Window closed")


def main() -> int:
    setup_logging()
    
    logger.info("=" * 80)
    logger.info("CODEX PORTABLE DESKTOP STARTING")
    logger.info("=" * 80)
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working directory: {Path.cwd()}")
    
    app = QApplication(sys.argv)
    window = CodexWindow()
    window.show()
    
    logger.info("GUI initialized, entering event loop")
    
    rc = app.exec()
    
    logger.info("=" * 80)
    logger.info("CODEX PORTABLE DESKTOP EXITING")
    logger.info("=" * 80)
    
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
'''

def generate_tests_init():
    """tests/__init__.py"""
    return '''"""Test suite for Codex Portable Desktop."""
'''

def generate_test_config():
    """tests/test_config.py"""
    return '''from __future__ import annotations

import unittest
import os

from codex_clone.config import load_config, Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_load_default_config(self):
        """Test loading configuration with defaults."""
        for key in ['CODEX_BASE_URL', 'CODEX_MODEL', 'CODEX_TEMPERATURE', 'CODEX_MAX_TOKENS']:
            if key in os.environ:
                del os.environ[key]
        
        config = load_config()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.base_url, "http://localhost:1234")
        self.assertEqual(config.model, "local-coder")
        self.assertEqual(config.temperature, 0.2)
        self.assertEqual(config.max_tokens, 2048)
    
    def test_load_custom_config(self):
        """Test loading configuration with custom environment variables."""
        os.environ['CODEX_BASE_URL'] = 'http://example.com:5000'
        os.environ['CODEX_MODEL'] = 'custom-model'
        os.environ['CODEX_TEMPERATURE'] = '0.5'
        os.environ['CODEX_MAX_TOKENS'] = '4096'
        
        config = load_config()
        
        self.assertEqual(config.base_url, 'http://example.com:5000')
        self.assertEqual(config.model, 'custom-model')
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 4096)
    
    def test_api_key_optional(self):
        """Test that API key is optional."""
        if 'CODEX_API_KEY' in os.environ:
            del os.environ['CODEX_API_KEY']
        
        config = load_config()
        self.assertIsNone(config.api_key)
    
    def test_config_dataclass(self):
        """Test Config dataclass."""
        cfg = Config(
            base_url="http://localhost:1234",
            api_key=None,
            model="test-model",
            system_prompt="Test prompt",
            temperature=0.3,
            max_tokens=1024
        )
        
        self.assertEqual(cfg.base_url, "http://localhost:1234")
        self.assertIsNone(cfg.api_key)
        self.assertEqual(cfg.model, "test-model")
        self.assertEqual(cfg.system_prompt, "Test prompt")
        self.assertEqual(cfg.temperature, 0.3)
        self.assertEqual(cfg.max_tokens, 1024)


if __name__ == "__main__":
    unittest.main()
'''

def generate_test_api():
    """tests/test_api.py"""
    return '''from __future__ import annotations

import unittest
from codex_clone.api import _validate_messages, CodexError, MAX_MESSAGE_LENGTH, MAX_MESSAGES


class TestApiValidation(unittest.TestCase):
    def test_validate_empty_messages(self):
        """Test validation rejects empty messages."""
        with self.assertRaises(CodexError):
            _validate_messages([])
    
    def test_validate_too_many_messages(self):
        """Test validation rejects too many messages."""
        messages = [
            {"role": "user", "content": f"msg {i}"}
            for i in range(MAX_MESSAGES + 1)
        ]
        with self.assertRaises(CodexError):
            _validate_messages(messages)
    
    def test_validate_missing_fields(self):
        """Test validation rejects messages with missing fields."""
        with self.assertRaises(CodexError):
            _validate_messages([{"role": "user"}])
        
        with self.assertRaises(CodexError):
            _validate_messages([{"content": "test"}])
    
    def test_validate_non_string_content(self):
        """Test validation rejects non-string content."""
        with self.assertRaises(CodexError):
            _validate_messages([{"role": "user", "content": 123}])
    
    def test_validate_oversized_message(self):
        """Test validation rejects oversized messages."""
        content = "x" * (MAX_MESSAGE_LENGTH + 1)
        with self.assertRaises(CodexError):
            _validate_messages([{"role": "user", "content": content}])
    
    def test_validate_valid_messages(self):
        """Test validation accepts valid messages."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        result = _validate_messages(messages)
        self.assertEqual(len(result), 3)
    
    def test_validate_not_dict(self):
        """Test validation rejects non-dict messages."""
        with self.assertRaises(CodexError):
            _validate_messages(["not a dict"])


if __name__ == "__main__":
    unittest.main()
'''

def generate_gitignore():
    """.gitignore"""
    return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
codex.log*

# Models
models/

# OS
.DS_Store
Thumbs.db

# Generated
generator.log
'''


def write_file(path: Path, content: str, logger: logging.Logger) -> None:
    """Write content to a file and log the operation."""
    try:
        logger.info(f"Writing file: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        size_kb = len(content) / 1024
        logger.info(f"  ✓ Created {path} ({size_kb:.2f} KB)")
    except Exception as exc:
        logger.error(f"  ✗ Failed to write {path}: {exc}")
        raise


def main() -> int:
    """Main generator function."""
    root_dir = Path.cwd()
    output_dir = root_dir / "generated"
    log_path = root_dir / "generator.log"
    
    setup_logging(log_path)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Output directory: {output_dir}")
    logger.info("Starting project generation...")
    logger.info("=" * 80)
    
    files_to_generate: list[tuple[str, Callable[[], str]]] = [
        ("pyproject.toml", generate_pyproject_toml),
        ("README.md", generate_readme),
        (".gitignore", generate_gitignore),
        ("run_tests.py", generate_run_tests_py),
        ("run_tests.sh", generate_run_tests_sh),
        ("run_tests.bat", generate_run_tests_bat),
        ("codex_clone/__init__.py", generate_codex_clone_init),
        ("codex_clone/config.py", generate_codex_clone_config),
        ("codex_clone/logging_utils.py", generate_codex_clone_logging_utils),
        ("codex_clone/settings.py", generate_codex_clone_settings),
        ("codex_clone/api.py", generate_codex_clone_api),
        ("codex_clone/backend_helper.py", generate_codex_clone_backend_helper),
        ("codex_clone/backend.py", generate_codex_clone_backend),
        ("codex_clone/socket_backend.py", generate_codex_clone_socket_backend),
        ("codex_portable.py", generate_codex_portable),
        ("tests/__init__.py", generate_tests_init),
        ("tests/test_config.py", generate_test_config),
        ("tests/test_api.py", generate_test_api),
    ]
    
    successful = 0
    failed = 0
    
    for relative_path, generator_func in files_to_generate:
        try:
            logger.info(f"Generating: {relative_path}")
            content = generator_func()
            file_path = output_dir / relative_path
            write_file(file_path, content, logger)
            successful += 1
        except Exception as exc:
            logger.error(f"Failed to generate {relative_path}: {exc}")
            failed += 1
    
    logger.info("=" * 80)
    logger.info("GENERATION COMPLETE")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total: {successful + failed}")
    logger.info("=" * 80)
    
    if failed > 0:
        logger.error(f"{failed} files failed to generate")
        return 1
    
    logger.info("All files generated successfully!")
    logger.info(f"Check {log_path} for detailed logs")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
