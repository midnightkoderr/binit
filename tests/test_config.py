from unittest.mock import patch

import pytest

from binit.core.config import load_config


class TestLoadConfig:
    def test_raises_when_config_missing(self, tmp_path):
        with patch('binit.core.config.DEFAULT_BASE_DIR', tmp_path):
            with pytest.raises(FileNotFoundError, match='binit init'):
                load_config()


    def test_normalizes_installed_tools_list_to_dict(self, tmp_path):
        config_file = tmp_path / 'config.yaml'
        config_file.write_text('binit_version: 0.1.0\nos: linux\narch: amd64\ninstalled_tools: []\n')
        with patch('binit.core.config.DEFAULT_BASE_DIR', tmp_path):
            config = load_config()
        assert config['installed_tools'] == {}


    def test_normalizes_installed_tools_none_to_dict(self, tmp_path):
        config_file = tmp_path / 'config.yaml'
        config_file.write_text('binit_version: 0.1.0\ninstalled_tools: null\n')
        with patch('binit.core.config.DEFAULT_BASE_DIR', tmp_path):
            config = load_config()
        assert config['installed_tools'] == {}


    def test_keeps_installed_tools_dict_unchanged(self, tmp_path):
        config_file = tmp_path / 'config.yaml'
        config_file.write_text('binit_version: 0.1.0\ninstalled_tools:\n  grant:\n    name: grant\n')
        with patch('binit.core.config.DEFAULT_BASE_DIR', tmp_path):
            config = load_config()
        assert 'grant' in config['installed_tools']
