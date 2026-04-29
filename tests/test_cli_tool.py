from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from binit.cli.tool import tool


INSTALLED_TOOLS = {
    'grant': {
        'name': 'grant',
        'version': '0.6.4',
        'release': 'v0.6.4',
        'repo': 'https://github.com/anchore/grant',
        'binary': '/home/user/.binit/bin/grant',
    }
}


class TestToolInstall:
    def test_install_calls_installer(self):
        runner = CliRunner()
        with patch('binit.cli.tool.Installer') as mock_installer:
            mock_installer.return_value.run.return_value = MagicMock()
            result = runner.invoke(tool, ['install', '-r', 'anchore/grant'])
        assert result.exit_code == 0
        mock_installer.assert_called_once_with('anchore/grant', name=None)
        mock_installer.return_value.run.assert_called_once()


    def test_install_with_name(self):
        runner = CliRunner()
        with patch('binit.cli.tool.Installer') as mock_installer:
            mock_installer.return_value.run.return_value = MagicMock()
            result = runner.invoke(tool, ['install', '-r', 'ahmetb/kubectx', '-n', 'kubens'])
        assert result.exit_code == 0
        mock_installer.assert_called_once_with('ahmetb/kubectx', name='kubens')


    def test_install_missing_repo_fails(self):
        runner = CliRunner()
        result = runner.invoke(tool, ['install'])
        assert result.exit_code != 0


    def test_install_value_error_shown(self):
        runner = CliRunner()
        with patch('binit.cli.tool.Installer') as mock_installer:
            mock_installer.return_value.run.side_effect = ValueError('No matching asset found')
            result = runner.invoke(tool, ['install', '-r', 'anchore/grant'])
        assert result.exit_code != 0
        assert 'No matching asset found' in result.output


class TestToolListInstalled:
    def test_list_installed_shows_table(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': INSTALLED_TOOLS}):
            result = runner.invoke(tool, ['--list-installed'])
        assert result.exit_code == 0
        assert 'grant' in result.output
        assert '0.6.4' in result.output


    def test_list_installed_no_tools(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': {}}):
            result = runner.invoke(tool, ['--list-installed'])
        assert result.exit_code == 0
        assert 'No tools installed' in result.output


    def test_list_installed_config_not_found(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', side_effect=FileNotFoundError('Config not found')):
            result = runner.invoke(tool, ['--list-installed'])
        assert result.exit_code != 0
        assert 'Config not found' in result.output


class TestToolUpdate:
    def test_update_already_up_to_date(self):
        runner = CliRunner()
        latest = MagicMock()
        latest.tag_name = 'v0.6.4'
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': INSTALLED_TOOLS}), patch('binit.cli.tool.GhApi') as mock_api, patch('binit.cli.tool.parse_github_repo', return_value=('anchore', 'grant')):
            mock_api.return_value.repos.get_latest_release.return_value = latest
            result = runner.invoke(tool, ['update', '-n', 'grant'])
        assert result.exit_code == 0
        assert 'already up to date' in result.output


    def test_update_installs_new_version(self):
        runner = CliRunner()
        latest = MagicMock()
        latest.tag_name = 'v0.7.0'
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': INSTALLED_TOOLS}), patch('binit.cli.tool.GhApi') as mock_api, patch('binit.cli.tool.parse_github_repo', return_value=('anchore', 'grant')), patch('binit.cli.tool.Installer') as mock_installer:
            mock_api.return_value.repos.get_latest_release.return_value = latest
            mock_installer.return_value.run.return_value = MagicMock()
            result = runner.invoke(tool, ['update', '-n', 'grant'])
        assert result.exit_code == 0
        assert 'v0.6.4' in result.output
        assert 'v0.7.0' in result.output
        mock_installer.return_value.run.assert_called_once()


    def test_update_tool_not_installed(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': {}}):
            result = runner.invoke(tool, ['update', '-n', 'unknown'])
        assert result.exit_code != 0
        assert 'not installed' in result.output


    def test_update_all_no_tools(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': {}}):
            result = runner.invoke(tool, ['update', '--all'])
        assert result.exit_code == 0
        assert 'No tools installed' in result.output


    def test_update_all_updates_each_tool(self):
        runner = CliRunner()
        tools = {
            'grant': {**INSTALLED_TOOLS['grant']},
            'gitleaks': {
                'name': 'gitleaks',
                'version': '8.0.0',
                'release': 'v8.0.0',
                'repo': 'https://github.com/gitleaks/gitleaks',
                'binary': '/home/user/.binit/bin/gitleaks',
            },
        }
        latest = MagicMock()
        latest.tag_name = 'v99.0.0'
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': tools}), patch('binit.cli.tool.GhApi') as mock_api, patch('binit.cli.tool.parse_github_repo', side_effect=lambda u: ('owner', u.split('/')[-1])), patch('binit.cli.tool.Installer') as mock_installer:
            mock_api.return_value.repos.get_latest_release.return_value = latest
            mock_installer.return_value.run.return_value = MagicMock()
            result = runner.invoke(tool, ['update', '--all'])
        assert result.exit_code == 0
        assert mock_installer.return_value.run.call_count == 2


    def test_update_requires_name_or_all(self):
        runner = CliRunner()
        result = runner.invoke(tool, ['update'])
        assert result.exit_code != 0
        assert 'Provide --name or --all' in result.output


class TestToolUninstall:
    def test_uninstall_removes_binary_and_config(self, tmp_path):
        binary = tmp_path / 'grant'
        binary.write_text('binary')
        tools = {
            'grant': {**INSTALLED_TOOLS['grant'], 'binary': str(binary)},
        }
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': tools}), patch('binit.cli.tool.write_config') as mock_write:
            result = runner.invoke(tool, ['uninstall', '-n', 'grant'])
        assert result.exit_code == 0
        assert 'Uninstalled grant' in result.output
        assert not binary.exists()
        mock_write.assert_called_once()


    def test_uninstall_tool_not_installed(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': {}}):
            result = runner.invoke(tool, ['uninstall', '-n', 'unknown'])
        assert result.exit_code != 0
        assert 'not installed' in result.output


    def test_uninstall_config_not_found(self):
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', side_effect=FileNotFoundError('Config not found')):
            result = runner.invoke(tool, ['uninstall', '-n', 'grant'])
        assert result.exit_code != 0
        assert 'Config not found' in result.output


    def test_uninstall_missing_binary_no_error(self):
        tools = {
            'grant': {**INSTALLED_TOOLS['grant'], 'binary': '/nonexistent/grant'},
        }
        runner = CliRunner()
        with patch('binit.cli.tool.load_config', return_value={'installed_tools': tools}), patch('binit.cli.tool.write_config'):
            result = runner.invoke(tool, ['uninstall', '-n', 'grant'])
        assert result.exit_code == 0
        assert 'Uninstalled grant' in result.output


    def test_uninstall_missing_name_fails(self):
        runner = CliRunner()
        result = runner.invoke(tool, ['uninstall'])
        assert result.exit_code != 0
