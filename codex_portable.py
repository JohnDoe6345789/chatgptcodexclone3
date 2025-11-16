#!/usr/bin/env python3
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
            message = json.dumps(data) + "\n"
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
        
        self._append_chat_output("[System] Default settings loaded\n", "#faa61a")
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
        self._append_chat_output("[System] Settings saved successfully\n", "#43b581")
        logger.info("Settings saved")
    
    def _on_connect(self) -> None:
        logger.info("User requested to connect to backend")
        self._append_chat_output("[System] Connecting to backend daemon...\n", "#faa61a")
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
        self._append_chat_output("[System] Disconnected from backend\n", "#f04747")
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
            self._append_chat_output("[System] ✅ Connected to backend daemon\n", "#43b581")
            self._disconnect_btn.setEnabled(True)
            self._connect_btn.setEnabled(False)
        else:
            self._append_chat_output(f"[System] ❌ {message}\n", "#f04747")
            self._disconnect_btn.setEnabled(False)
            self._connect_btn.setEnabled(True)
    
    def _on_message_received(self, msg: dict) -> None:
        mtype = msg.get("type")
        
        if mtype == "log":
            log_msg = msg.get("message", "")
            self._append_backend_output(f"[Backend] {log_msg}\n", "#72767d")
        
        elif mtype == "chat_reply":
            req_id = msg.get("id", "")
            ok = msg.get("ok", False)
            
            if req_id in self._pending_requests:
                del self._pending_requests[req_id]
            
            if ok:
                content = msg.get("content", "")
                self._append_chat_output(f"\n[🤖 Assistant]\n{content}\n\n", "#43b581")
            else:
                error = msg.get("error", "Unknown error")
                self._append_chat_output(f"[❌ Error] {error}\n", "#f04747")
        
        elif mtype == "status":
            running = msg.get("running", False)
            self._backend_status = "Running" if running else "Stopped"
            self._update_status_bar()
            status_text = "✅ Running" if running else "⏹️ Stopped"
            self._append_backend_output(f"[Status] Backend is {status_text}\n", "#5865f2")
    
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
            self._append_backend_output("[System] ▶️ Starting AI backend...\n", "#faa61a")
        else:
            self._append_backend_output("[Error] Not connected to daemon. Go to Backend Connection tab.\n", "#f04747")
    
    def _on_stop_backend(self) -> None:
        logger.info("User requested to stop backend")
        if self._client:
            self._client.send_message({"type": "stop_backend"})
            self._append_backend_output("[System] ⏹️ Stopping AI backend...\n", "#faa61a")
        else:
            self._append_backend_output("[Error] Not connected to daemon. Go to Backend Connection tab.\n", "#f04747")
    
    def _on_check_status(self) -> None:
        logger.info("User requested backend status check")
        if self._client:
            self._client.send_message({"type": "status"})
        else:
            self._append_backend_output("[Error] Not connected to daemon. Go to Backend Connection tab.\n", "#f04747")
    
    def _on_send_chat(self) -> None:
        user_input = self._chat_input.text().strip()
        
        if not user_input:
            return
        
        if not self._client:
            self._append_chat_output("[Error] Not connected to backend. Connect first!\n", "#f04747")
            return
        
        logger.info(f"User sent message: {user_input[:50]}...")
        
        self._append_chat_output(f"[💬 You] {user_input}\n", "#5865f2")
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
        self._append_chat_output("[⏳ System] Processing request...\n", "#72767d")
    
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
