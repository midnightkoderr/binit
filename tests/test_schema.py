from datetime import datetime, timezone

import pytest

from binit.schema import ConfigSchema, ToolSchema


def valid_tool_dict(**overrides):
    data = {
        'name': 'grant',
        'repo': 'https://github.com/anchore/grant',
        'asset': 'grant_0.6.4_linux_amd64.tar.gz',
        'release': 'v0.6.4',
        'version': '0.6.4',
        'homepage': 'https://github.com/anchore/grant',
        'updated_at': datetime(2026, 1, 1, tzinfo=timezone.utc),
        'installed_at': datetime(2026, 1, 2, tzinfo=timezone.utc),
        'description': 'A grant tool',
        'license': 'MIT License',
        'binary': '/home/user/.binit/bin/grant',
    }
    data.update(overrides)
    return data


def valid_config_dict(**overrides):
    data = {
        'binit_version': '0.1.0',
        'os': 'linux',
        'arch': 'amd64',
        'init_at': datetime(2026, 1, 1, tzinfo=timezone.utc),
        'installed_tools': {},
    }
    data.update(overrides)
    return data


class TestToolSchema:
    def test_valid_tool_no_errors(self):
        errors = ToolSchema().validate(valid_tool_dict())
        assert errors == {}


    def test_dump_and_load_roundtrip(self):
        from binit.models import ToolModel
        from pathlib import Path
        tool = ToolModel(**{**valid_tool_dict(), 'binary': Path('/home/user/.binit/bin/grant')})
        dumped = ToolSchema().dump(tool)
        assert dumped['name'] == 'grant'
        assert dumped['version'] == '0.6.4'


    def test_missing_required_name(self):
        data = valid_tool_dict()
        del data['name']
        errors = ToolSchema().validate(data)
        assert 'name' in errors


    def test_invalid_version_format(self):
        errors = ToolSchema().validate(valid_tool_dict(version='1.0'))
        assert 'version' in errors


    def test_invalid_repo_url(self):
        errors = ToolSchema().validate(valid_tool_dict(repo='not-a-url'))
        assert 'repo' in errors


    def test_none_homepage_allowed(self):
        errors = ToolSchema().validate(valid_tool_dict(homepage=None))
        assert errors == {}


    def test_none_description_allowed(self):
        errors = ToolSchema().validate(valid_tool_dict(description=None))
        assert errors == {}


    def test_none_license_allowed(self):
        errors = ToolSchema().validate(valid_tool_dict(license=None))
        assert errors == {}


    def test_rename_to_omitted_from_dump_when_none(self):
        from binit.models import ToolModel
        from pathlib import Path
        tool = ToolModel(**{**valid_tool_dict(), 'binary': Path('/home/user/.binit/bin/grant'), 'rename_to': None})
        dumped = ToolSchema().dump(tool)
        assert 'rename_to' not in dumped


    def test_rename_to_present_in_dump_when_set(self):
        from binit.models import ToolModel
        from pathlib import Path
        tool = ToolModel(**{**valid_tool_dict(), 'binary': Path('/home/user/.binit/bin/grant'), 'rename_to': 'mygrant'})
        dumped = ToolSchema().dump(tool)
        assert dumped['rename_to'] == 'mygrant'


    def test_rename_to_loads_from_dict(self):
        data = valid_tool_dict(rename_to='mygrant')
        errors = ToolSchema().validate(data)
        assert errors == {}


class TestConfigSchema:
    def test_valid_config_no_errors(self):
        errors = ConfigSchema().validate(valid_config_dict())
        assert errors == {}


    def test_invalid_os(self):
        errors = ConfigSchema().validate(valid_config_dict(os='windows'))
        assert 'os' in errors


    def test_invalid_arch(self):
        errors = ConfigSchema().validate(valid_config_dict(arch='mips'))
        assert 'arch' in errors


    def test_missing_binit_version(self):
        data = valid_config_dict()
        del data['binit_version']
        errors = ConfigSchema().validate(data)
        assert 'binit_version' in errors


    def test_installed_tools_with_valid_tool(self):
        errors = ConfigSchema().validate(valid_config_dict(
            installed_tools={'grant': valid_tool_dict()}
        ))
        assert errors == {}
