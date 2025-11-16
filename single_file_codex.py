#!/usr/bin/env python3
"""
Single-file project structure generator for Codex Portable Desktop.
Outputs the complete multi-file project structure as code.
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
dependencies = []

[tool.setuptools.packages.find]
where = ["codex_clone"]
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

def generate_codex_clone_init():
    """codex_clone/__init__.py"""
    return '''"""Local ChatGPT/Codex-style coding assistant."""
'''

def generate_codex_clone_config():
    """codex_clone/config.py"""
    return '''from __future__ import annotations

import os
from dataclasses import dataclass


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
        return default
    return value


def load_config() -> Config:
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
    return Config(
        base_url=base_url,
        api_key=api_key,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
'''

def generate_codex_clone_logging_utils():
    """codex_clone/logging_utils.py"""
    return '''from __future__ import annotations

from pathlib import Path
import threading
import datetime


_log_lock = threading.Lock()
_LOG_PATH = Path(__file__).resolve().parent.parent / "codex.log"


def log_line(text: str) -> None:
    """Append a timestamped line to the shared log file."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {text}"
    with _log_lock:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\\n")
'''

def generate_codex_clone_api():
    """codex_clone/api.py"""
    return '''from __future__ import annotations

from typing import Iterable, List, Dict

import json
import urllib.request
import urllib.error
import time

from .config import Config
from .logging_utils import log_line


class CodexError(RuntimeError):
    """Error raised when the HTTP API fails."""


def _build_payload(
    messages: Iterable[Dict[str, str]],
    config: Config,
) -> bytes:
    log_line(f"[api] Building chat payload with {len(list(messages))} messages")
    
    payload = {
        "model": config.model,
        "messages": list(messages),
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    
    log_line(f"[api] Model: {config.model}")
    log_line(f"[api] Temperature: {config.temperature}")
    log_line(f"[api] Max tokens: {config.max_tokens}")
    
    text = json.dumps(payload)
    payload_bytes = text.encode("utf-8")
    
    log_line(f"[api] Payload size: {len(payload_bytes)} bytes")
    
    return payload_bytes


def _build_request(
    payload: bytes,
    config: Config,
) -> urllib.request.Request:
    url = config.base_url.rstrip("/") + "/v1/chat/completions"
    
    log_line(f"[api] Building HTTP request")
    log_line(f"[api] URL: {url}")
    log_line(f"[api] Method: POST")
    
    request = urllib.request.Request(url, data=payload)
    request.add_header("Content-Type", "application/json")
    log_line(f"[api] Header added: Content-Type: application/json")
    
    if config.api_key:
        request.add_header("Authorization", f"Bearer {config.api_key}")
        log_line(f"[api] Header added: Authorization: Bearer ***{config.api_key[-4:]}")
    else:
        log_line(f"[api] No API key configured (local server mode)")
    
    return request


def _parse_response(data: bytes) -> str:
    log_line(f"[api] Parsing response ({len(data)} bytes)")
    
    try:
        text = data.decode("utf-8")
        log_line(f"[api] Response decoded successfully ({len(text)} characters)")
        
    except UnicodeDecodeError as exc:
        log_line(f"[api] ERROR: Failed to decode response as UTF-8: {exc}")
        raise CodexError("Response is not valid UTF-8") from exc
    
    try:
        obj = json.loads(text)
        log_line(f"[api] JSON parsed successfully")
        
    except json.JSONDecodeError as exc:
        log_line(f"[api] ERROR: Invalid JSON from server: {exc}")
        log_line(f"[api] Response preview: {text[:200]}...")
        raise CodexError("Invalid JSON from server") from exc
    
    if "error" in obj:
        error_msg = obj["error"]
        log_line(f"[api] ERROR: Server returned error: {error_msg}")
        raise CodexError(f"Server error: {error_msg}")
    
    choices = obj.get("choices") or []
    log_line(f"[api] Response contains {len(choices)} choices")
    
    if not choices:
        log_line(f"[api] ERROR: Response contains no choices")
        raise CodexError("Response contains no choices")
    
    message = choices[0].get("message") or {}
    log_line(f"[api] Extracting content from first choice")
    
    content = message.get("content", "")
    
    if not isinstance(content, str):
        log_line(f"[api] ERROR: Assistant content is not a string (type: {type(content).__name__})")
        raise CodexError("Assistant content is not a string")
    
    log_line(f"[api] Content extracted: {len(content)} characters")
    
    if "usage" in obj:
        usage = obj["usage"]
        log_line(f"[api] Token usage: prompt={usage.get('prompt_tokens', '?')}, "
                f"completion={usage.get('completion_tokens', '?')}, "
                f"total={usage.get('total_tokens', '?')}")
    
    return content


def send_chat(
    messages: List[Dict[str, str]],
    config: Config,
) -> str:
    """Send a chat completion request to the local HTTP backend."""
    log_line("[api] ==================== HTTP CHAT REQUEST ====================")
    log_line(f"[api] Starting chat request with {len(messages)} messages")
    
    start_time = time.time()
    
    try:
        payload = _build_payload(messages, config)
        request = _build_request(payload, config)
        
        log_line(f"[api] Opening HTTP connection (timeout: 600 seconds)...")
        
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                log_line(f"[api] HTTP connection established")
                log_line(f"[api] Response code: {response.code}")
                log_line(f"[api] Reading response body...")
                
                body = response.read()
                
                elapsed = time.time() - start_time
                log_line(f"[api] Response received in {elapsed:.2f} seconds")
                
        except urllib.error.HTTPError as exc:
            elapsed = time.time() - start_time
            log_line(f"[api] HTTP ERROR after {elapsed:.2f} seconds: {exc}")
            log_line(f"[api] Status code: {exc.code}")
            log_line(f"[api] Reason: {exc.reason}")
            
            try:
                error_body = exc.read().decode('utf-8')
                log_line(f"[api] Error response body: {error_body}")
            except Exception:
                pass
            
            raise CodexError(f"HTTP {exc.code}: {exc.reason}") from exc
            
        except urllib.error.URLError as exc:
            elapsed = time.time() - start_time
            log_line(f"[api] URL ERROR after {elapsed:.2f} seconds: {exc}")
            raise CodexError(f"Connection failed: {exc.reason}") from exc
            
        except OSError as exc:
            elapsed = time.time() - start_time
            log_line(f"[api] OS ERROR after {elapsed:.2f} seconds: {exc}")
            raise CodexError(f"Network error: {exc}") from exc
        
        reply = _parse_response(body)
        
        total_elapsed = time.time() - start_time
        log_line(f"[api] Chat request completed in {total_elapsed:.2f} seconds")
        log_line(f"[api] Reply preview: {reply[:100]}...")
        log_line("[api] ==================== HTTP CHAT COMPLETE ====================")
        
        return reply
        
    except CodexError:
        raise
        
    except Exception as exc:
        elapsed = time.time() - start_time
        log_line(f"[api] UNEXPECTED ERROR after {elapsed:.2f} seconds: {exc}")
        raise CodexError(f"Unexpected error: {exc}") from exc
'''

def generate_codex_clone_backend_helper():
    """codex_clone/backend_helper.py"""
    return '''from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Final

from .logging_utils import log_line


HF_REPO: Final[str] = "TheBloke/deepseek-coder-6.7B-instruct-GGUF"
HF_FILE: Final[str] = "deepseek-coder-6.7b-instruct.Q4_K_M.gguf"


def project_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    log(f"[helper] Project root: {root}")
    return root


def models_dir() -> Path:
    directory = project_root() / "models"
    log(f"[helper] Models directory: {directory}")
    
    if not directory.exists():
        log(f"[helper] Creating models directory...")
        directory.mkdir(parents=True, exist_ok=True)
        log(f"[helper] Models directory created")
    else:
        log(f"[helper] Models directory already exists")
    
    return directory


def log(msg: str) -> None:
    """Log to both stdout (for daemon capture) and log file."""
    print(msg, flush=True)
    log_line(msg)


def ensure_huggingface_hub() -> None:
    log("[helper] Checking for huggingface_hub module...")
    
    try:
        import huggingface_hub  # noqa: F401
        log(f"[helper] huggingface_hub is already installed (version: {huggingface_hub.__version__})")
        return
    except ImportError:
        log("[helper] huggingface_hub not found, need to install")
    except Exception as exc:
        log(f"[helper] Error checking huggingface_hub: {exc}")
    
    log("[helper] ==================== INSTALLING HUGGINGFACE_HUB ====================")
    log("[helper] Running: pip install huggingface_hub>=0.25.0")
    
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "huggingface_hub>=0.25.0"],
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start_time
    
    log(f"[helper] pip install completed in {elapsed:.2f} seconds")
    log(f"[helper] Return code: {result.returncode}")
    
    if result.stdout:
        log(f"[helper] STDOUT:\\n{result.stdout}")
    if result.stderr:
        log(f"[helper] STDERR:\\n{result.stderr}")
    
    if result.returncode != 0:
        log(f"[helper] WARNING: pip install returned non-zero code")
    else:
        log(f"[helper] huggingface_hub installation successful")


def download_model() -> Path:
    log("[helper] ==================== MODEL DOWNLOAD PHASE ====================")
    
    ensure_huggingface_hub()
    
    log("[helper] Importing huggingface_hub.hf_hub_download...")
    from huggingface_hub import hf_hub_download

    dest_dir = models_dir()
    local_path = dest_dir / HF_FILE
    
    log(f"[helper] Target model file: {local_path}")
    log(f"[helper] Checking if model already exists...")
    
    if local_path.exists():
        file_size = local_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        log(f"[helper] Model already present: {local_path}")
        log(f"[helper] File size: {file_size_mb:.2f} MB")
        return local_path
    
    log(f"[helper] Model not found locally, starting download...")
    log(f"[helper] Repository: {HF_REPO}")
    log(f"[helper] Filename: {HF_FILE}")
    log(f"[helper] Destination: {dest_dir}")
    log(f"[helper] NOTE: First download may take several minutes (model is ~4GB)")
    log(f"[helper] Downloading model from Hugging Face... (this may take a while)")
    
    start_time = time.time()
    
    try:
        actual = hf_hub_download(
            repo_id=HF_REPO,
            filename=HF_FILE,
            local_dir=str(dest_dir),
            local_dir_use_symlinks=False,
        )
        
        elapsed = time.time() - start_time
        log(f"[helper] Download completed in {elapsed:.2f} seconds")
        
        local_path = Path(actual)
        file_size = local_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        log(f"[helper] Model downloaded to: {local_path}")
        log(f"[helper] File size: {file_size_mb:.2f} MB")
        
    except Exception as exc:
        log(f"[helper] ERROR during model download: {exc}")
        log(f"[helper] Exception type: {type(exc).__name__}")
        raise
    
    return local_path


def have_llama_server() -> bool:
    log("[helper] Checking for llama_cpp.server module...")
    
    try:
        import llama_cpp.server  # type: ignore[unused-ignore]  # noqa: F401
        import llama_cpp
        log(f"[helper] llama-cpp-python is installed (version: {llama_cpp.__version__})")
        return True
    except ImportError:
        log("[helper] llama_cpp.server not found")
        return False
    except Exception as exc:
        log(f"[helper] Error checking llama_cpp: {exc}")
        return False


def ensure_llama_cpp() -> bool:
    log("[helper] ==================== LLAMA-CPP-PYTHON CHECK ====================")
    
    if have_llama_server():
        log("[helper] llama-cpp-python[server] is already available")
        return True
    
    log("[helper] llama-cpp-python[server] not found, installing...")
    log("[helper] NOTE: This may take several minutes and may require compilation")
    log("[helper] Running: pip install llama-cpp-python[server]")
    
    start_time = time.time()
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "llama-cpp-python[server]"],
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start_time
    
    log(f"[helper] pip install completed in {elapsed:.2f} seconds")
    log(f"[helper] Return code: {result.returncode}")
    
    if result.stdout:
        stdout_lines = result.stdout.split('\\n')
        if len(stdout_lines) > 50:
            log(f"[helper] STDOUT (last 50 lines):\\n" + '\\n'.join(stdout_lines[-50:]))
        else:
            log(f"[helper] STDOUT:\\n{result.stdout}")
    
    if result.stderr:
        stderr_lines = result.stderr.split('\\n')
        if len(stderr_lines) > 50:
            log(f"[helper] STDERR (last 50 lines):\\n" + '\\n'.join(stderr_lines[-50:]))
        else:
            log(f"[helper] STDERR:\\n{result.stderr}")
    
    if result.returncode == 0 and have_llama_server():
        log("[helper] llama-cpp-python[server] installation successful")
        return True
    
    log("[helper] WARNING: Could not install llama-cpp-python[server]")
    log("[helper] You may need to:")
    log("[helper]   1. Install build tools (Visual Studio on Windows, gcc on Linux)")
    log("[helper]   2. Use LM Studio or another OpenAI-compatible backend manually")
    log("[helper]   3. Check your Python version (3.10+ recommended)")
    return False


def run_llama_server(model_path: Path) -> int:
    log("[helper] ==================== STARTING LLAMA SERVER ====================")
    
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
    
    log(f"[helper] Command: {' '.join(cmd)}")
    log(f"[helper] Model: {model_path}")
    log(f"[helper] Host: 127.0.0.1")
    log(f"[helper] Port: 1234")
    log(f"[helper] Context size: 8192 tokens")
    log("[helper] Starting llama_cpp.server (this may take 30-60 seconds)...")
    log("[helper] Server output will appear below:")
    log("[helper] " + "="*70)
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    
    log(f"[helper] Server process started with PID: {proc.pid}")
    
    assert proc.stdout is not None
    line_count = 0
    
    try:
        for line in proc.stdout:
            line_count += 1
            msg = "[llama] " + line.rstrip()
            print(msg, flush=True)
            log_line(msg)
            
            if line_count % 20 == 0:
                log(f"[helper] (Server output: {line_count} lines processed)")
    
    except Exception as exc:
        log(f"[helper] ERROR reading server output: {exc}")
        log(f"[helper] Exception type: {type(exc).__name__}")
    
    log("[helper] " + "="*70)
    log("[helper] Server output stream ended, waiting for process exit...")
    
    code = proc.wait()
    
    log(f"[helper] llama_cpp.server exited with code {code}")
    log(f"[helper] Total output lines: {line_count}")
    
    return code


def main() -> int:
    log("[helper] ==================== BACKEND HELPER STARTING ====================")
    log(f"[helper] Python: {sys.version}")
    log(f"[helper] Executable: {sys.executable}")
    log(f"[helper] PID: {sys.getpid()}")
    log(f"[helper] Working directory: {Path.cwd()}")
    
    try:
        log("[helper] Phase 1: Download/verify model...")
        model_path = download_model()
        log(f"[helper] Phase 1 complete: model at {model_path}")
        
    except Exception as exc:
        log(f"[helper] FATAL ERROR: model download failed: {exc}")
        log(f"[helper] Exception type: {type(exc).__name__}")
        log(f"[helper] Cannot continue without model")
        return 1
    
    try:
        log("[helper] Phase 2: Ensure llama-cpp-python is installed...")
        if not ensure_llama_cpp():
            log("[helper] Phase 2 failed: llama-cpp-python not available")
            log("[helper] Exiting without starting backend")
            return 0
        log("[helper] Phase 2 complete: llama-cpp-python ready")
        
    except Exception as exc:
        log(f"[helper] ERROR in Phase 2: {exc}")
        log(f"[helper] Exception type: {type(exc).__name__}")
        return 1
    
    try:
        log("[helper] Phase 3: Start llama.cpp server...")
        rc = run_llama_server(model_path)
        log(f"[helper] Phase 3 complete: server exited with code {rc}")
        
    except Exception as exc:
        log(f"[helper] ERROR in Phase 3: {exc}")
        log(f"[helper] Exception type: {type(exc).__name__}")
        return 1
    
    log("[helper] ==================== BACKEND HELPER SHUTTING DOWN ====================")
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
from typing import Callable, Optional

from .config import load_config
from .api import send_chat, CodexError
from .logging_utils import log_line


HOST = "127.0.0.1"
PORT = 56789


class BackendProcessManager:
    """Manage the llama backend helper process with verbose logging."""

    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._log_callback: Optional[Callable[[str], None]] = None

    def is_running(self) -> bool:
        with self._lock:
            if self._proc is None:
                return False
            poll_result = self._proc.poll()
            running = poll_result is None
            return running

    def start(self, log: Callable[[str], None]) -> None:
        log("[daemon] >>> START BACKEND REQUEST RECEIVED <<<")
        
        with self._lock:
            if self.is_running():
                log("[daemon] Backend already running - ignoring start request")
                return
            
            log("[daemon] No existing backend process found")
            log("[daemon] Building command: python -m codex_clone.backend_helper")
            
            cmd = [sys.executable, "-m", "codex_clone.backend_helper"]
            
            try:
                log(f"[daemon] Executing command: {' '.join(cmd)}")
                log("[daemon] Starting subprocess with stdout/stderr pipes...")
                
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                
                log(f"[daemon] Subprocess created with PID: {proc.pid}")
                self._proc = proc
                self._log_callback = log
                
            except Exception as exc:
                log(f"[daemon] ERROR: Failed to start backend_helper subprocess: {exc}")
                log(f"[daemon] Exception type: {type(exc).__name__}")
                return
        
        log("[daemon] backend_helper launched successfully")
        log("[daemon] Starting log reader thread for subprocess output...")
        
        threading.Thread(
            target=self._log_reader, args=(proc, log), daemon=True, name="backend-log-reader"
        ).start()
        
        log("[daemon] Log reader thread started")

    def _log_reader(self, proc: subprocess.Popen, log: Callable[[str], None]) -> None:
        log("[daemon] Log reader thread active, monitoring subprocess output...")
        
        if proc.stdout is None:
            log("[daemon] ERROR: subprocess stdout is None!")
            return
        
        line_count = 0
        try:
            for line in proc.stdout:
                line_count += 1
                log(line.rstrip())
                
                if line_count % 10 == 0:
                    log(f"[daemon] (Log reader: {line_count} lines processed)")
        
        except Exception as exc:
            log(f"[daemon] ERROR in log reader: {exc}")
            log(f"[daemon] Exception type: {type(exc).__name__}")
        
        log("[daemon] Log reader: subprocess stdout closed, waiting for exit code...")
        code = proc.wait()
        log(f"[daemon] backend_helper exited with code {code}")
        log(f"[daemon] Total lines read from subprocess: {line_count}")

    def stop(self, log: Callable[[str], None]) -> None:
        log("[daemon] >>> STOP BACKEND REQUEST RECEIVED <<<")
        
        with self._lock:
            if not self.is_running():
                log("[daemon] No backend process to stop (already stopped or never started)")
                return
            
            assert self._proc is not None
            proc = self._proc
            pid = proc.pid
            self._proc = None
        
        log(f"[daemon] Terminating backend_helper process (PID: {pid})...")
        
        try:
            proc.terminate()
            log("[daemon] Terminate signal sent successfully")
            
            log("[daemon] Waiting up to 5 seconds for graceful shutdown...")
            for i in range(5):
                time.sleep(1)
                if proc.poll() is not None:
                    log(f"[daemon] Process terminated gracefully after {i+1} seconds")
                    return
            
            log("[daemon] Process did not terminate gracefully, sending KILL signal...")
            proc.kill()
            proc.wait()
            log("[daemon] Process killed forcefully")
            
        except Exception as exc:
            log(f"[daemon] ERROR during process termination: {exc}")
            log(f"[daemon] Exception type: {type(exc).__name__}")


class SocketBackendServer:
    """JSON-over-TCP daemon with comprehensive logging."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._backend = BackendProcessManager()
        self._config = load_config()
        self._stop_event = threading.Event()
        self._listener: Optional[socket.socket] = None
        self._client_counter = 0

    def serve_forever(self) -> None:
        log_line(f"[daemon] ==================== DAEMON STARTING ====================")
        log_line(f"[daemon] Socket backend initializing on {self._host}:{self._port}")
        log_line(f"[daemon] Python version: {sys.version}")
        log_line(f"[daemon] PID: {sys.getpid()}")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                log_line(f"[daemon] Socket created successfully")
                
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                log_line(f"[daemon] SO_REUSEADDR set to allow immediate rebinding")
                
                log_line(f"[daemon] Attempting to bind to {self._host}:{self._port}...")
                s.bind((self._host, self._port))
                log_line(f"[daemon] Bind successful!")
                
                log_line(f"[daemon] Starting listen with backlog=5...")
                s.listen(5)
                self._listener = s
                
                log_line("[daemon] ==================== DAEMON READY ====================")
                log_line("[daemon] Socket backend listening and ready for connections")
                
                while not self._stop_event.is_set():
                    log_line("[daemon] Waiting for client connection (blocking accept)...")
                    
                    try:
                        conn, addr = s.accept()
                        self._client_counter += 1
                        client_id = self._client_counter
                        
                        log_line(f"[daemon] ======== CLIENT #{client_id} CONNECTED ========")
                        log_line(f"[daemon] Client address: {addr}")
                        
                    except OSError as exc:
                        log_line(f"[daemon] Accept interrupted: {exc}")
                        break
                    
                    log_line(f"[daemon] Starting handler thread for client #{client_id}...")
                    t = threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr, client_id),
                        daemon=True,
                        name=f"client-handler-{client_id}"
                    )
                    t.start()
                    log_line(f"[daemon] Handler thread started for client #{client_id}")
                    
        except Exception as exc:
            log_line(f"[daemon] FATAL ERROR in serve_forever: {exc}")
            log_line(f"[daemon] Exception type: {type(exc).__name__}")
            
        log_line("[daemon] ==================== DAEMON STOPPING ====================")
        log_line("[daemon] Socket backend exiting serve_forever")

    def _request_shutdown(self, log: Callable[[str], None]) -> None:
        if not self._stop_event.is_set():
            log("[daemon] >>> SHUTDOWN SEQUENCE INITIATED <<<")
            log("[daemon] Setting stop event...")
            self._stop_event.set()
            
            if self._listener is not None:
                log("[daemon] Closing listener socket to unblock accept()...")
                try:
                    self._listener.close()
                    log("[daemon] Listener socket closed successfully")
                except OSError as exc:
                    log(f"[daemon] Error closing listener: {exc}")

    def _handle_client(self, conn: socket.socket, addr, client_id: int) -> None:
        log_line(f"[daemon][client-{client_id}] Handler thread started")
        log_line(f"[daemon][client-{client_id}] Creating file objects for I/O...")
        
        f_in = conn.makefile("r", encoding="utf-8")
        f_out = conn.makefile("w", encoding="utf-8")
        lock = threading.Lock()
        message_counter = 0

        def send(obj: dict) -> None:
            nonlocal message_counter
            message_counter += 1
            text = json.dumps(obj, ensure_ascii=False)
            
            with lock:
                try:
                    f_out.write(text + "\\n")
                    f_out.flush()
                    log_line(f"[daemon][client-{client_id}] Sent message #{message_counter}: {obj.get('type', 'unknown')}")
                except OSError as exc:
                    log_line(f"[daemon][client-{client_id}] ERROR sending message: {exc}")
                    return

        def log_fn(text: str) -> None:
            log_line(text)
            send({"type": "backend_log", "message": text})

        log_line(f"[daemon][client-{client_id}] Sending hello message...")
        send({"type": "hello", "message": "socket backend ready"})
        
        try:
            log_line(f"[daemon][client-{client_id}] Entering message receive loop...")
            received_count = 0
            
            for line in f_in:
                received_count += 1
                line = line.strip()
                
                if not line:
                    log_line(f"[daemon][client-{client_id}] Received empty line (skipping)")
                    continue
                
                log_line(f"[daemon][client-{client_id}] Received message #{received_count}: {line[:100]}...")
                
                try:
                    msg = json.loads(line)
                    log_line(f"[daemon][client-{client_id}] JSON parsed successfully")
                except json.JSONDecodeError as exc:
                    log_line(f"[daemon][client-{client_id}] ERROR: Invalid JSON: {exc}")
                    continue
                
                mtype = msg.get("type")
                log_line(f"[daemon][client-{client_id}] Message type: {mtype}")
                
                if mtype == "ping":
                    log_line(f"[daemon][client-{client_id}] Handling PING request")
                    send({"type": "pong"})
                    
                elif mtype == "start_backend":
                    log_line(f"[daemon][client-{client_id}] Handling START_BACKEND request")
                    
                    def start_worker():
                        log_fn(f"[daemon][client-{client_id}] Start worker thread executing...")
                        self._backend.start(log_fn)
                        log_fn(f"[daemon][client-{client_id}] Start worker thread complete")
                    
                    threading.Thread(target=start_worker, daemon=True, name="start-worker").start()
                    send({"type": "start_backend_ack"})
                    log_line(f"[daemon][client-{client_id}] Sent start_backend_ack")
                    
                elif mtype == "stop_backend":
                    log_line(f"[daemon][client-{client_id}] Handling STOP_BACKEND request")
                    
                    def stop_worker():
                        log_fn(f"[daemon][client-{client_id}] Stop worker thread executing...")
                        self._backend.stop(log_fn)
                        log_fn(f"[daemon][client-{client_id}] Stop worker thread complete")
                    
                    threading.Thread(target=stop_worker, daemon=True, name="stop-worker").start()
                    send({"type": "stop_backend_ack"})
                    log_line(f"[daemon][client-{client_id}] Sent stop_backend_ack")
                    
                elif mtype == "status":
                    log_line(f"[daemon][client-{client_id}] Handling STATUS request")
                    running = self._backend.is_running()
                    log_line(f"[daemon][client-{client_id}] Backend running: {running}")
                    send({"type": "status", "running": running})
                    log_line(f"[daemon][client-{client_id}] Sent status response")
                    
                elif mtype == "chat":
                    messages = msg.get("messages") or []
                    req_id = msg.get("id", "")
                    log_line(f"[daemon][client-{client_id}] Handling CHAT request (id={req_id})")
                    log_line(f"[daemon][client-{client_id}] Chat has {len(messages)} messages")

                    def chat_worker() -> None:
                        log_fn(f"[daemon][client-{client_id}] Chat worker starting for request {req_id}...")
                        
                        try:
                            log_fn(f"[daemon][client-{client_id}] Calling send_chat API...")
                            reply = send_chat(messages, self._config)
                            log_fn(f"[daemon][client-{client_id}] Chat API returned successfully")
                            log_fn(f"[daemon][client-{client_id}] Reply length: {len(reply)} characters")
                            
                            send({
                                "type": "chat_reply",
                                "id": req_id,
                                "ok": True,
                                "content": reply,
                            })
                            log_fn(f"[daemon][client-{client_id}] Chat reply sent to client")
                            
                        except CodexError as exc:
                            log_fn(f"[daemon][client-{client_id}] ERROR in chat: {exc}")
                            log_fn(f"[daemon][client-{client_id}] Exception type: {type(exc).__name__}")
                            
                            send({
                                "type": "chat_reply",
                                "id": req_id,
                                "ok": False,
                                "error": str(exc),
                            })
                            log_fn(f"[daemon][client-{client_id}] Error response sent to client")

                    threading.Thread(target=chat_worker, daemon=True, name=f"chat-worker-{req_id}").start()
                    log_line(f"[daemon][client-{client_id}] Chat worker thread started")
                    
                elif mtype == "shutdown":
                    log_fn(f"[daemon][client-{client_id}] Handling SHUTDOWN request")
                    log_fn(f"[daemon][client-{client_id}] Stopping backend if running...")
                    self._backend.stop(log_fn)
                    
                    send({"type": "shutdown_ack"})
                    log_fn(f"[daemon][client-{client_id}] Sent shutdown_ack")
                    
                    log_fn(f"[daemon][client-{client_id}] Requesting daemon shutdown...")
                    self._request_shutdown(log_fn)
                    
                    log_line(f"[daemon][client-{client_id}] Breaking message loop")
                    break
                    
                else:
                    log_line(f"[daemon][client-{client_id}] WARNING: Unknown message type: {mtype}")
            
            log_line(f"[daemon][client-{client_id}] Message loop ended (received {received_count} messages)")
            
        except Exception as exc:
            log_line(f"[daemon][client-{client_id}] EXCEPTION in handler: {exc}")
            log_line(f"[daemon][client-{client_id}] Exception type: {type(exc).__name__}")
            
        finally:
            log_line(f"[daemon][client-{client_id}] Closing connection...")
            try:
                conn.close()
                log_line(f"[daemon][client-{client_id}] Connection closed successfully")
            except Exception as exc:
                log_line(f"[daemon][client-{client_id}] Error closing connection: {exc}")
            
            log_line(f"[daemon][client-{client_id}] ======== CLIENT #{client_id} DISCONNECTED ========")


def main() -> int:
    log_line("[daemon] ==================== DAEMON MAIN() CALLED ====================")
    log_line(f"[daemon] Creating SocketBackendServer instance...")
    
    server = SocketBackendServer(HOST, PORT)
    log_line(f"[daemon] Server instance created, calling serve_forever()...")
    
    server.serve_forever()
    
    log_line("[daemon] serve_forever() returned")
    log_line("[daemon] ==================== DAEMON MAIN() EXITING ====================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

def generate_codex_portable():
    """codex_portable.py"""
    # This is very long, so I'll output it in the print at the end
    # For now, return a placeholder
    return "# See full content in enhanced_codex_portable artifact"

def generate_tests_init():
    """tests/__init__.py"""
    return ""

def generate_test_api_mocked():
    """tests/test_api_mocked.py"""
    return '''import json
import unittest
from unittest.mock import patch, MagicMock

from codex_clone.api import send_chat, CodexError
from codex_clone.config import Config


class TestApiMocked(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config(
            base_url="http://localhost:1234",
            api_key=None,
            model="local-coder",
            system_prompt="",
            temperature=0.1,
            max_tokens=128,
        )

    @patch("codex_clone.api.urllib.request.urlopen")
    def test_send_chat_success(self, mock_urlopen) -> None:
        messages = [{"role": "user", "content": "hi"}]
        body = json.dumps(
            {
                "choices": [
                    {"message": {"content": "hello back"}},
                ]
            }
        ).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_ctx.__exit__.return_value = False
        mock_urlopen.return_value = mock_ctx

        reply = send_chat(messages, self.config)
        self.assertEqual(reply, "hello back")

    @patch("codex_clone.api.urllib.request.urlopen")
    def test_send_chat_error(self, mock_urlopen) -> None:
        mock_urlopen.side_effect = OSError("connection refused")
        with self.assertRaises(CodexError):
            send_chat([{"role": "user", "content": "hi"}], self.config)


if __name__ == "__main__":
    unittest.main()
'''

def generate_test_config():
    """tests/test_config.py"""
    return '''import os
import unittest
from unittest.mock import patch

from codex_clone.config import load_config


class TestConfig(unittest.TestCase):
    def test_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.base_url, "http://localhost:1234")
        self.assertEqual(cfg.model, "local-coder")
        self.assertAlmostEqual(cfg.temperature, 0.2)
        self.assertEqual(cfg.max_tokens, 2048)
        self.assertIsNone(cfg.api_key)

    def test_env_overrides(self) -> None:
        env = {
            "CODEX_BASE_URL": "http://127.0.0.1:9999",
            "CODEX_MODEL": "my-model",
            "CODEX_TEMPERATURE": "0.55",
            "CODEX_MAX_TOKENS": "4096",
            "CODEX_API_KEY": "secret-key",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.base_url, "http://127.0.0.1:9999")
        self.assertEqual(cfg.model, "my-model")
        self.assertAlmostEqual(cfg.temperature, 0.55)
        self.assertEqual(cfg.max_tokens, 4096)
        self.assertEqual(cfg.api_key, "secret-key")


if __name__ == "__main__":
    unittest.main()
'''

def generate_test_logging_utils():
    """tests/test_logging_utils.py"""
    return '''import unittest
from pathlib import Path

from codex_clone import logging_utils


class TestLoggingUtils(unittest.TestCase):
    def test_log_line_creates_file_and_writes(self) -> None:
        log_path = Path(logging_utils.__file__).resolve().parent.parent / "codex.log"
        if log_path.exists():
            log_path.unlink()

        logging_utils.log_line("test line 123")
        self.assertTrue(log_path.exists(), "codex.log should be created")

        data = log_path.read_text(encoding="utf-8")
        self.assertIn("test line 123", data)
        self.assertIn("[", data)
        self.assertIn("]", data)


if __name__ == "__main__":
    unittest.main()
'''

def generate_test_socket_client_basic():
    """tests/test_socket_client_basic.py"""
    return '''import unittest
import queue

from codex_portable import SocketBackendClient


class DummyQueue(queue.Queue):
    def put(self, item, block=True, timeout=None):
        super().put(item, block=block, timeout=timeout)


class TestSocketBackendClientBasic(unittest.TestCase):
    def test_req_id_increments(self) -> None:
        backend_log = DummyQueue()
        chat = DummyQueue()
        state = DummyQueue()
        client = SocketBackendClient(backend_log, chat, state)

        first = client._next_req_id()
        second = client._next_req_id()
        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith("req-"))
        self.assertTrue(second.startswith("req-"))


if __name__ == "__main__":
    unittest.main()
'''


if __name__ == "__main__":
    print("# Complete Codex Portable Desktop Project Structure")
    print("# Copy each section to the appropriate file")
    print()
    
    files = [
        ("pyproject.toml", generate_pyproject_toml),
        ("run_tests.py", generate_run_tests_py),
        ("run_tests.sh", generate_run_tests_sh),
        ("run_tests.bat", generate_run_tests_bat),
        ("codex_clone/__init__.py", generate_codex_clone_init),
        ("codex_clone/config.py", generate_codex_clone_config),
        ("codex_clone/logging_utils.py", generate_codex_clone_logging_utils),
        ("codex_clone/api.py", generate_codex_clone_api),
        ("codex_clone/backend_helper.py", generate_codex_clone_backend_helper),
        ("codex_clone/socket_backend.py", generate_codex_clone_socket_backend),
        ("tests/__init__.py", generate_tests_init),
        ("tests/test_api_mocked.py", generate_test_api_mocked),
        ("tests/test_config.py", generate_test_config),
        ("tests/test_logging_utils.py", generate_test_logging_utils),
        ("tests/test_socket_client_basic.py", generate_test_socket_client_basic),
    ]
    
    for filepath, generator in files:
        print(f"# {'=' * 76}")
        print(f"# FILE: {filepath}")
        print(f"# {'=' * 76}")
        print(generator())
        print()
    
    print("# " + "=" * 76)
    print("# FILE: codex_portable.py")
    print("# " + "=" * 76)
    print("# NOTE: See the 'enhanced_codex_portable' artifact for the full")
    print("# enhanced GUI code with state machine and verbose logging.")
    print("#")
    print("# The codex_portable.py file is too large to include in this")
    print("# generator script, but you already have it in the artifacts.")
