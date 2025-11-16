from __future__ import annotations

from typing import Iterable, List, Dict

import json
import urllib.request
import urllib.error
import time
import logging

from .config import Config

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 10000
MAX_MESSAGES = 100
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0


class CodexError(RuntimeError):
    """Error raised when the HTTP API fails."""


def _validate_messages(messages: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    """Validate and sanitize messages."""
    msg_list = list(messages)
    
    if not msg_list:
        raise CodexError("Messages list cannot be empty")
    
    if len(msg_list) > MAX_MESSAGES:
        raise CodexError(f"Too many messages: {len(msg_list)} > {MAX_MESSAGES}")
    
    for i, msg in enumerate(msg_list):
        if not isinstance(msg, dict):
            raise CodexError(f"Message {i} is not a dict")
        
        if "role" not in msg or "content" not in msg:
            raise CodexError(f"Message {i} missing required fields (role, content)")
        
        content = msg.get("content", "")
        if not isinstance(content, str):
            raise CodexError(f"Message {i} content is not a string")
        
        if len(content) > MAX_MESSAGE_LENGTH:
            raise CodexError(f"Message {i} exceeds max length: {len(content)} > {MAX_MESSAGE_LENGTH}")
    
    logger.debug(f"Validated {len(msg_list)} messages")
    return msg_list


def _build_payload(
    messages: Iterable[Dict[str, str]],
    config: Config,
) -> bytes:
    msg_list = _validate_messages(messages)
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
        logger.debug("Authorization header added")
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
    """Send a chat completion request to the local HTTP backend with retry logic."""
    logger.info("=" * 80)
    logger.info(f"Starting chat request with {len(messages)} messages")
    
    start_time = time.time()
    last_error = None
    backoff = INITIAL_BACKOFF
    
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
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
            
            if exc.code >= 500 and attempt < MAX_RETRIES - 1:
                logger.warning(f"Server error (attempt {attempt + 1}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            
            raise CodexError(f"HTTP {exc.code}: {exc.reason}") from exc
            
        except urllib.error.URLError as exc:
            elapsed = time.time() - start_time
            logger.error(f"URL error after {elapsed:.2f}s: {exc}")
            
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Connection error (attempt {attempt + 1}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            
            raise CodexError(f"Connection failed: {exc.reason}") from exc
            
        except (OSError, TimeoutError) as exc:
            elapsed = time.time() - start_time
            logger.error(f"Network error after {elapsed:.2f}s: {exc}")
            
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Network error (attempt {attempt + 1}), retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            
            raise CodexError(f"Network error: {exc}") from exc
        
        reply = _parse_response(body)
        
        total_elapsed = time.time() - start_time
        logger.info(f"Chat request completed in {total_elapsed:.2f} seconds")
        logger.debug(f"Reply preview: {reply[:100]}...")
        logger.info("=" * 80)
        
        return reply
    
    if last_error:
        raise last_error
    raise CodexError("Unknown error: request failed after retries")
