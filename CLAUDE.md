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

## Agent Helper CLI

```bash
python agent.py <command> [options]
```

Convenient CLI for common development tasks:

**Git Commands**: `git-status`, `git-log [N]`, `git-diff`, `git-diff-staged`, `git-branch`  
**Search & Analysis**: `grep-files <pattern> [ext]`, `count-lines [ext]`, `list-files [ext] [depth]`  
**Testing & Quality**: `test`, `lint`, `typecheck`  
**Utilities**: `help`

Examples:
```bash
python agent.py help                      # Show all commands
python agent.py count-lines py            # Count Python lines
python agent.py grep-files "def " py      # Search for functions
python agent.py git-log 10                # Show last 10 commits
python agent.py list-files py 2           # List Python files (max depth 2)
```

**Note**: If you need to run a command that's not already defined in `agent.py`, add it to the agent helper first rather than running ad-hoc bash commands. This keeps the development workflow documented and consistent.

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
