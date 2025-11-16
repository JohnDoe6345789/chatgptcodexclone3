from __future__ import annotations

import unittest
import os

from codex_clone.config import load_config, Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_load_default_config(self):
        """Test loading configuration with defaults."""
        for key in ['CODEX_BASE_URL', 'CODEX_MODEL', 'CODEX_TEMPERATURE', 'CODEX_MAX_TOKENS']:
            if key in os.environ:
                del os.environ[key]
        
        config = load_config()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.base_url, "http://localhost:1234")
        self.assertEqual(config.model, "local-coder")
        self.assertEqual(config.temperature, 0.2)
        self.assertEqual(config.max_tokens, 2048)
    
    def test_load_custom_config(self):
        """Test loading configuration with custom environment variables."""
        os.environ['CODEX_BASE_URL'] = 'http://example.com:5000'
        os.environ['CODEX_MODEL'] = 'custom-model'
        os.environ['CODEX_TEMPERATURE'] = '0.5'
        os.environ['CODEX_MAX_TOKENS'] = '4096'
        
        config = load_config()
        
        self.assertEqual(config.base_url, 'http://example.com:5000')
        self.assertEqual(config.model, 'custom-model')
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 4096)
    
    def test_api_key_optional(self):
        """Test that API key is optional."""
        if 'CODEX_API_KEY' in os.environ:
            del os.environ['CODEX_API_KEY']
        
        config = load_config()
        self.assertIsNone(config.api_key)
    
    def test_config_dataclass(self):
        """Test Config dataclass."""
        cfg = Config(
            base_url="http://localhost:1234",
            api_key=None,
            model="test-model",
            system_prompt="Test prompt",
            temperature=0.3,
            max_tokens=1024
        )
        
        self.assertEqual(cfg.base_url, "http://localhost:1234")
        self.assertIsNone(cfg.api_key)
        self.assertEqual(cfg.model, "test-model")
        self.assertEqual(cfg.system_prompt, "Test prompt")
        self.assertEqual(cfg.temperature, 0.3)
        self.assertEqual(cfg.max_tokens, 1024)


if __name__ == "__main__":
    unittest.main()
