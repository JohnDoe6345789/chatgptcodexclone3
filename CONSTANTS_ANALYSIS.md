# Constants Analysis: Which Are Exposed to Settings Panel

## Summary
The settings panel in `codex_portable.py` exposes only **6 out of ~23 constants** defined in the generator. Many important constants remain hardcoded and inaccessible to users.

## Exposed to Settings Panel ✅

These are controlled via the Configuration Settings form in the GUI:

1. **base_url** - AI backend server URL (QLineEdit)
   - Default: "http://localhost:1234"
   - Source: config.py DEFAULT_BASE_URL

2. **api_key** - Optional API key for remote backends (QLineEdit, password mode)
   - Default: None
   - Source: config.py (empty by default)

3. **model** - Model name to use (QLineEdit)
   - Default: "local-coder"
   - Source: config.py DEFAULT_MODEL

4. **temperature** - Response creativity (0.0-2.0) (QDoubleSpinBox)
   - Default: 0.2
   - Source: config.py DEFAULT_TEMPERATURE

5. **max_tokens** - Maximum response length (QSpinBox, 1-32768)
   - Default: 2048
   - Source: config.py DEFAULT_MAX_TOKENS

6. **system_prompt** - System instruction prompt (QTextEdit, 80px height)
   - Default: "You are a helpful coding assistant..."
   - Source: config.py DEFAULT_SYSTEM_PROMPT

## NOT Exposed ❌

These constants are hardcoded in various modules:

### API Constants (codex_clone/api.py)
- `MAX_MESSAGE_LENGTH` = 10000
- `MAX_MESSAGES` = 100
- `MAX_RETRIES` = 3
- `INITIAL_BACKOFF` = 1.0
- `REQUEST_TIMEOUT` = 120
- `RESPONSE_PREVIEW_LENGTH` = 200
- `REPLY_PREVIEW_LENGTH` = 100

### Backend Constants (codex_clone/backend.py)
- `PROCESS_TIMEOUT` = 10

### Backend Helper Constants (codex_clone/backend_helper.py)
- `PROCESS_TIMEOUT` = 10
- `LLAMA_HOST` = "127.0.0.1"
- `LLAMA_PORT` = 1234
- `CONTEXT_SIZE` = 8192
- `MAX_LINE_BUFFER` = 1000000
- (Also repeats some API constants)

### Socket Backend Constants (codex_clone/socket_backend.py)
- `HOST` = os.getenv("CODEX_SOCKET_HOST", "127.0.0.1")
- `PORT` = os.getenv("CODEX_SOCKET_PORT", "9876")
- `MAX_WORKERS` = os.getenv("CODEX_SOCKET_MAX_WORKERS", "10")
- `SOCKET_TIMEOUT` = 1.0

### Logging Constants (codex_clone/logging_utils.py)
- `LOG_MAX_BYTES` = 10 * 1024 * 1024
- `LOG_BACKUP_COUNT` = 5

### GUI Constants (codex_portable.py)
- Socket connection hardcoded to: `127.0.0.1:9876` (line 2047)

## Recommendations

### High Priority - Add to Settings Panel:
- `BACKEND_LLAMA_PORT` (currently hardcoded to 1234)
- `SOCKET_HOST` and `SOCKET_PORT` (currently hardcoded to 127.0.0.1:9876)
- `API_REQUEST_TIMEOUT` (affects all API calls)
- `BACKEND_PROCESS_TIMEOUT` (affects shutdown behavior)

### Medium Priority - Environment Variables:
- `MAX_WORKERS` already uses env var with fallback
- Consider similar pattern for other socket settings

### Low Priority - Advanced Settings Tab:
- API_MAX_MESSAGE_LENGTH
- API_MAX_MESSAGES
- API_MAX_RETRIES
- API_INITIAL_BACKOFF
- BACKEND_CONTEXT_SIZE
- LOG_MAX_BYTES / LOG_BACKUP_COUNT
- SOCKET_TIMEOUT

## Current Implementation Details

### Settings Storage
- Stored in: `~/.config/codex-portable/settings.yaml` (Linux/macOS)
- Or: `%APPDATA%/codex-portable/settings.yaml` (Windows)
- Format: YAML with safe_load/safe_dump

### Settings Loading Priority
1. Environment variables (CODEX_*)
2. Saved YAML settings
3. Hardcoded defaults
