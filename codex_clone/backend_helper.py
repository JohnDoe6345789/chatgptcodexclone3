from __future__ import annotations

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
            for line in result.stdout.split('\n')[-30:]:
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
                for line in result.stderr.split('\n')[-20:]:
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
