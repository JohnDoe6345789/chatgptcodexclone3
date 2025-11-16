# Development Guide

## Running the Application

```bash
python run.py
```

The bootstrap installer (`run.py`) will:
- Check for required dependencies (PyQt6, PyYAML)
- Show a GUI setup wizard if dependencies are missing
- Install missing packages via pip
- Launch the main application

## Testing

```bash
python run_tests.py
```

Runs all unit tests in the `tests/` directory.

## Project Structure

- `run.py` - Bootstrap installer with dependency management
- `codex_portable.py` - Main PyQt6 GUI application
- `codex_clone/` - Application package
  - `config.py` - Configuration and environment variables
  - `logging_utils.py` - Logging setup
  - `settings.py` - YAML-based settings persistence
  - `socket_backend.py` - Socket daemon for backend communication
  - `backend_helper.py` - Model management and llama.cpp server
  - `api.py` - OpenAI-compatible API client
- `generate_codex_project.py` - Project structure generator script

## Key Features

1. **Fresh Install Support**: `run.py` handles all dependency installation
2. **GUI-Based Setup**: tkinter GUI on Windows/macOS, ncurses on Linux
3. **Headless Support**: Automatic pip installation in CI/non-interactive environments
4. **Socket Architecture**: Daemon backend runs independently from GUI
5. **Comprehensive Logging**: All operations logged to `codex.log`
