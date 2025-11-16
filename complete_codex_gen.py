#!/usr/bin/env python3
"""
Complete single-file project structure generator for Codex Portable Desktop.
Outputs the entire multi-file project structure with full content.
Run: python single_file_codex.py > OUTPUT.txt
"""

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

logger = logging.getLogger(__name__)


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
    logger.info("Loading configuration from environment")
    
    base_url = _get_env("CODEX_BASE_URL", "http://localhost:1234")
    api_key = os.getenv("CODEX_API_KEY")
    model = _get_env("CODEX_MODEL", "local-coder")
    system_prompt = _get_env(
        "CODEX_SYSTEM_PROMPT",
        (
            "You are a helpful coding assistant. Focus on code, "
            "be concise, and always provide complete examples."
        ),
    )
    temperature_str = _get_env("CODEX_TEMPERATURE", "0.2")
    max_tokens_str = _get_env("CODEX_MAX_TOKENS", "2048")
    
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


class CodexError(RuntimeError):
    """Error raised when the HTTP API fails."""


def _build_payload(
    messages: Iterable[Dict[str, str]],
    config: Config,
) -> bytes:
    msg_list = list(messages)
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
        logger.debug(f"Authorization header added (key ending: ***{config.api_key[-4:]})")
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
    """Send a chat completion request to the local HTTP backend."""
    logger.info("=" * 80)
    logger.info(f"Starting chat request with {len(messages)} messages")
    
    start_time = time.time()
    
    try:
        payload = _build_payload(messages, config)
        request = _build_request(payload, config)
        
        logger.debug("Opening HTTP connection (timeout: 600 seconds)...")
        
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
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
            except Exception:
                pass
            
            raise CodexError(f"HTTP {exc.code}: {exc.reason}") from exc
            
        except urllib.error.URLError as exc:
            elapsed = time.time() - start_time
            logger.error(f"URL error after {elapsed:.2f}s: {exc}")
            raise CodexError(f"Connection failed: {exc.reason}") from exc
            
        except OSError as exc:
            elapsed = time.time() - start_time
            logger.error(f"OS error after {elapsed:.2f}s: {exc}")
            raise CodexError(f"Network error: {exc}") from exc
        
        reply = _parse_response(body)
        
        total_elapsed = time.time() - start_time
        logger.info(f"Chat request completed in {total_elapsed:.2f} seconds")
        logger.debug(f"Reply preview: {reply[:100]}...")
        logger.info("=" * 80)
        
        return reply
        
    except CodexError:
        raise
        
    except Exception as exc:
        elapsed = time.time() - start_time
        logger.error(f"Unexpected error after {elapsed:.2f}s: {exc}", exc_info=True)
        raise CodexError(f"Unexpected error: {exc}") from exc
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


def ensure_huggingface_hub() -> None:
    logger.info("Checking for huggingface_hub module...")
    
    try:
        import huggingface_hub
        logger.info(f"huggingface_hub is already installed (version: {huggingface_hub.__version__})")
        return
    except ImportError:
        logger.warning("huggingface_hub not found, will install")
    
    logger.info("=" * 80)
    logger.info("Installing huggingface_hub>=0.25.0")
    logger.info("=" * 80)
    
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "huggingface_hub>=0.25.0"],
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start_time
    
    logger.info(f"pip install completed in {elapsed:.2f} seconds (return code: {result.returncode})")
    
    if result.stdout:
        for line in result.stdout.split('\\n')[-20:]:  # Last 20 lines
            if line.strip():
                logger.debug(f"  {line}")
    
    if result.returncode != 0:
        logger.warning("pip install returned non-zero code")
        if result.stderr:
            for line in result.stderr.split('\\n')[-10:]:
                if line.strip():
                    logger.error(f"  {line}")
    else:
        logger.info("huggingface_hub installation successful")


def download_model() -> Path:
    logger.info("=" * 80)
    logger.info("MODEL DOWNLOAD PHASE")
    logger.info("=" * 80)
    
    ensure_huggingface_hub()
    
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
        import llama_cpp.server  # type: ignore
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
    
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "llama-cpp-python[server]"],
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start_time
    
    logger.info(f"pip install completed in {elapsed:.2f} seconds (return code: {result.returncode})")
    
    if result.stdout:
        for line in result.stdout.split('\\n')[-30:]:
            if line.strip():
                logger.debug(f"  {line}")
    
    if result.returncode == 0 and have_llama_server():
        logger.info("llama-cpp-python[server] installation successful")
        return True
    
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
    
    assert proc.stdout is not None
    line_count = 0
    
    try:
        for line in proc.stdout:
            line_count += 1
            msg = line.rstrip()
            print(f"[llama] {msg}", flush=True)
            
            # Log every 10th line to avoid spam
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
    # Setup logging for this module
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

def generate_codex_clone_socket_backend():
    """codex_clone/socket_backend.py"""
    return '''from __future__ import annotations

import json
import socket
import threading
import subprocess
import sys
import time
import logging
from typing import Callable, Optional

from .config import load_config
from .api import send_chat, CodexError

logger = logging.getLogger(__name__)

HOST = "127.0.0.1"
PORT = 56789


class BackendProcessManager:
    """Manage the llama backend helper process."""

    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def is_running(self) -> bool:
        with self._lock:
            if self._proc is None:
                return False
            return self._proc.poll() is None

    def start(self, log_callback: Callable[[str], None]) -> None:
        logger.info("START BACKEND REQUEST RECEIVED")
        
        with self._lock:
            if self.is_running():
                logger.info("Backend already running - ignoring start request")
                log_callback("[daemon] Backend already running")
                return
            
            logger.info("Starting backend_helper subprocess...")
            
            cmd = [sys.executable, "-m", "codex_clone.backend_helper"]
            
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                
                logger.info(f"Subprocess created with PID: {proc.pid}")
                self._proc = proc
                
            except Exception as exc:
                logger.error(f"Failed to start backend_helper: {exc}", exc_info=True)
                log_callback(f"[daemon] ERROR: Failed to start backend: {exc}")
                return
        
        logger.info("backend_helper launched, starting log reader thread...")
        log_callback("[daemon] Backend starting...")
        
        threading.Thread(
            target=self._log_reader, args=(proc, log_callback), daemon=True
        ).start()

    def _log_reader(self, proc: subprocess.Popen, log_callback: Callable[[str], None]) -> None:
        logger.debug("Log reader thread active")
        
        if proc.stdout is None:
            logger.error("subprocess stdout is None!")
            return
        
        line_count = 0
        try:
            for line in proc.stdout:
                line_count += 1
                msg = line.rstrip()
                log_callback(msg)
                
                # Log important lines
                if any(k in msg.lower() for k in ['error', 'warn', 'phase', 'complete', 'ready']):
                    logger.info(f"[backend] {msg}")
        
        except Exception as exc:
            logger.error(f"Error in log reader: {exc}", exc_info=True)
        
        code = proc.wait()
        logger.info(f"backend_helper exited with code {code} ({line_count} lines read)")
        log_callback(f"[daemon] Backend exited with code {code}")

    def stop(self, log_callback: Callable[[str], None]) -> None:
        logger.info("STOP BACKEND REQUEST RECEIVED")
        
        with self._lock:
            if not self.is_running():
                logger.info("No backend process to stop")
                log_callback("[daemon] Backend not running")
                return
            
            assert self._proc is not None
            proc = self._proc
            pid = proc.pid
            self._proc = None
        
        logger.info(f"Terminating backend_helper (PID: {pid})...")
        log_callback("[daemon] Stopping backend...")
        
        try:
            proc.terminate()
            logger.debug("Terminate signal sent")
            
            for i in range(5):
                time.sleep(1)
                if proc.poll() is not None:
                    logger.info(f"Process terminated gracefully after {i+1}s")
                    log_callback("[daemon] Backend stopped")
                    return
            
            logger.warning("Process did not terminate gracefully, killing...")
            proc.kill()
            proc.wait()
            logger.info("Process killed")
            log_callback("[daemon] Backend force-killed")
            
        except Exception as exc:
            logger.error(f"Error during process termination: {exc}", exc_info=True)


class SocketBackendServer:
    """JSON-over-TCP daemon server."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._backend = BackendProcessManager()
        self._config = load_config()
        self._stop_event = threading.Event()
        self._listener: Optional[socket.socket] = None
        self._client_counter = 0

    def serve_forever(self) -> None:
        logger.info("=" * 80)
        logger.info(f"DAEMON STARTING ON {self._host}:{self._port}")
        logger.info("=" * 80)
        logger.info(f"Python version: {sys.version}")
        logger.info(f"PID: {sys.getpid()}")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self._host, self._port))
                s.listen(5)
                self._listener = s
                
                logger.info("=" * 80)
                logger.info("DAEMON READY - Listening for connections")
                logger.info("=" * 80)
                
                while not self._stop_event.is_set():
                    logger.debug("Waiting for client connection...")
                    
                    try:
                        conn, addr = s.accept()
                        self._client_counter += 1
                        client_id = self._client_counter
                        
                        logger.info(f"Client #{client_id} connected from {addr}")
                        
                    except OSError as exc:
                        logger.info(f"Accept interrupted: {exc}")
                        break
                    
                    threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr, client_id),
                        daemon=True
                    ).start()
                    
        except Exception as exc:
            logger.critical(f"FATAL error in serve_forever: {exc}", exc_info=True)
            
        logger.info("=" * 80)
        logger.info("DAEMON STOPPING")
        logger.info("=" * 80)

    def _request_shutdown(self) -> None:
        if not self._stop_event.is_set():
            logger.info("SHUTDOWN SEQUENCE INITIATED")
            self._stop_event.set()
            
            if self._listener is not None:
                logger.debug("Closing listener socket...")
                try:
                    self._listener.close()
                except OSError as exc:
                    logger.warning(f"Error closing listener: {exc}")

    def _handle_client(self, conn: socket.socket, addr, client_id: int) -> None:
        logger.debug(f"[Client {client_id}] Handler thread started")
        
        f_in = conn.makefile("r", encoding="utf-8")
        f_out = conn.makefile("w", encoding="utf-8")
        lock = threading.Lock()

        def send(obj: dict) -> None:
            text = json.dumps(obj, ensure_ascii=False)
            
            with lock:
                try:
                    f_out.write(text + "\n")
                    f_out.flush()
                except OSError as exc:
                    logger.warning(f"[Client {client_id}] Error sending: {exc}")

        def log_callback(text: str) -> None:
            logger.debug(f"[Client {client_id}] {text}")
            send({"type": "backend_log", "message": text})

        send({"type": "hello", "message": "socket backend ready"})
        
        try:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError as exc:
                    logger.warning(f"[Client {client_id}] Invalid JSON: {exc}")
                    continue
                
                mtype = msg.get("type")
                logger.debug(f"[Client {client_id}] Received: {mtype}")
                
                if mtype == "ping":
                    send({"type": "pong"})
                    
                elif mtype == "start_backend":
                    def start_worker():
                        self._backend.start(log_callback)
                    
                    threading.Thread(target=start_worker, daemon=True).start()
                    send({"type": "start_backend_ack"})
                    
                elif mtype == "stop_backend":
                    def stop_worker():
                        self._backend.stop(log_callback)
                    
                    threading.Thread(target=stop_worker, daemon=True).start()
                    send({"type": "stop_backend_ack"})
                    
                elif mtype == "status":
                    running = self._backend.is_running()
                    send({"type": "status", "running": running})
                    
                elif mtype == "chat":
                    messages = msg.get("messages") or []
                    req_id = msg.get("id", "")
                    logger.info(f"[Client {client_id}] Chat request {req_id} ({len(messages)} messages)")

                    def chat_worker() -> None:
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

                    threading.Thread(target=chat_worker, daemon=True).start()
                    
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