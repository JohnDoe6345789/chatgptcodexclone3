# Codex Portable Desktop

A local AI coding assistant with a modern PyQt6 GUI and automatic model management.

## Features

- **Automatic Setup**: Downloads and configures DeepSeek Coder 6.7B model
- **Socket-based Architecture**: Daemon process manages the backend independently
- **Modern UI**: Clean PyQt6 interface with syntax highlighting
- **Comprehensive Logging**: All operations logged to `codex.log`

## Quick Start

1. **Run the Application** (no manual setup needed!):
   ```bash
   python run.py
   ```

2. **First Launch**:
   - A setup wizard will appear if dependencies are missing
   - GUI-based installation on Windows/macOS (ncurses on Linux)
   - Or automatic pip installation in headless environments
   - After setup, downloads and configures DeepSeek Coder 6.7B model
   - Starts the local AI backend
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

- `run.py` - Bootstrap installer with dependency management
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
