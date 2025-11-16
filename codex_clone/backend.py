from __future__ import annotations

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
