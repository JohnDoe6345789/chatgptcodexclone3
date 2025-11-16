from __future__ import annotations

import unittest
from codex_clone.api import _validate_messages, CodexError, MAX_MESSAGE_LENGTH, MAX_MESSAGES


class TestApiValidation(unittest.TestCase):
    def test_validate_empty_messages(self):
        """Test validation rejects empty messages."""
        with self.assertRaises(CodexError):
            _validate_messages([])
    
    def test_validate_too_many_messages(self):
        """Test validation rejects too many messages."""
        messages = [
            {"role": "user", "content": f"msg {i}"}
            for i in range(MAX_MESSAGES + 1)
        ]
        with self.assertRaises(CodexError):
            _validate_messages(messages)
    
    def test_validate_missing_fields(self):
        """Test validation rejects messages with missing fields."""
        with self.assertRaises(CodexError):
            _validate_messages([{"role": "user"}])
        
        with self.assertRaises(CodexError):
            _validate_messages([{"content": "test"}])
    
    def test_validate_non_string_content(self):
        """Test validation rejects non-string content."""
        with self.assertRaises(CodexError):
            _validate_messages([{"role": "user", "content": 123}])
    
    def test_validate_oversized_message(self):
        """Test validation rejects oversized messages."""
        content = "x" * (MAX_MESSAGE_LENGTH + 1)
        with self.assertRaises(CodexError):
            _validate_messages([{"role": "user", "content": content}])
    
    def test_validate_valid_messages(self):
        """Test validation accepts valid messages."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        result = _validate_messages(messages)
        self.assertEqual(len(result), 3)
    
    def test_validate_not_dict(self):
        """Test validation rejects non-dict messages."""
        with self.assertRaises(CodexError):
            _validate_messages(["not a dict"])


if __name__ == "__main__":
    unittest.main()
