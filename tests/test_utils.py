import io
from pathlib import Path

import pytest

from binit.core.exceptions import YamlError
from binit.utils import ConfigManager, make_yaml_handler, os_arch_detect


ARCH_ALIASES = {
    'amd64': {'amd64', 'x86_64', 'x86-64'},
    'arm64': {'arm64', 'aarch64'},
    'armv7': {'armv7', 'armhf'},
}


class TestOsArchDetect:
    def test_linux_prefix_normalised(self):
        os_name, _ = os_arch_detect('linux-gnu', 'amd64', ARCH_ALIASES)
        assert os_name == 'linux'


    def test_linux_exact(self):
        os_name, _ = os_arch_detect('linux', 'amd64', ARCH_ALIASES)
        assert os_name == 'linux'


    def test_non_linux_os_unchanged(self):
        os_name, _ = os_arch_detect('darwin', 'amd64', ARCH_ALIASES)
        assert os_name == 'darwin'


    def test_arch_alias_resolved(self):
        _, arch = os_arch_detect('linux', 'x86_64', ARCH_ALIASES)
        assert arch == 'amd64'


    def test_arch_alias_aarch64(self):
        _, arch = os_arch_detect('linux', 'aarch64', ARCH_ALIASES)
        assert arch == 'arm64'


    def test_arch_alias_armhf(self):
        _, arch = os_arch_detect('linux', 'armhf', ARCH_ALIASES)
        assert arch == 'armv7'


    def test_unknown_arch_passthrough(self):
        _, arch = os_arch_detect('linux', 'riscv64', ARCH_ALIASES)
        assert arch == 'riscv64'


    def test_canonical_arch_unchanged(self):
        _, arch = os_arch_detect('linux', 'amd64', ARCH_ALIASES)
        assert arch == 'amd64'


class TestYamlHandler:
    def setup_method(self):
        self.handler = make_yaml_handler()


    def test_load_valid_yaml(self):
        stream = io.StringIO('key: value\nnumber: 42')
        result = self.handler.load(stream)
        assert result == {'key': 'value', 'number': 42}


    def test_load_empty_yaml(self):
        stream = io.StringIO('')
        result = self.handler.load(stream)
        assert result is None


    def test_load_invalid_yaml_raises(self):
        stream = io.StringIO('key: [unclosed')
        with pytest.raises(YamlError):
            self.handler.load(stream)


    def test_dump_and_reload(self):
        data = {'name': 'binit', 'version': '0.1.0', 'items': [1, 2, 3]}
        buf = io.StringIO()
        self.handler.dump(data, buf)
        buf.seek(0)
        result = self.handler.load(buf)
        assert result == data


class TestConfigManager:
    def setup_method(self):
        self.manager = ConfigManager(make_yaml_handler())


    def test_config_exists_false(self, tmp_path):
        assert self.manager.config_exists(tmp_path / 'missing.yaml') is False


    def test_config_exists_true(self, tmp_path):
        f = tmp_path / 'config.yaml'
        f.write_text('key: value')
        assert self.manager.config_exists(f) is True


    def test_load_config_missing_returns_empty(self, tmp_path):
        result = self.manager.load_config(tmp_path / 'missing.yaml')
        assert result == {}


    def test_load_config_reads_file(self, tmp_path):
        f = tmp_path / 'config.yaml'
        f.write_text('binit_version: 0.1.0\nos: linux')
        result = self.manager.load_config(f)
        assert result == {'binit_version': '0.1.0', 'os': 'linux'}


    def test_write_config_creates_file(self, tmp_path):
        path = tmp_path / 'config.yaml'
        self.manager.write_config({'key': 'value'}, path)
        assert path.exists()


    def test_write_config_roundtrip(self, tmp_path):
        path = tmp_path / 'config.yaml'
        data = {'binit_version': '0.1.0', 'installed_tools': []}
        self.manager.write_config(data, path)
        result = self.manager.load_config(path)
        assert result == data
