from __future__ import annotations

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
