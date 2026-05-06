from unittest.mock import patch

from click.testing import CliRunner

from binit.cli.cache import cache

BASE_CFG = {'base_dir': '/home/user/.binit'}


class TestCacheNoFlags:
    def test_no_flags_raises_usage_error(self):
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value=BASE_CFG):
            result = runner.invoke(cache, [])
        assert result.exit_code != 0
        assert 'Provide at least one option' in result.output


    def test_config_not_found_raises_error(self):
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', side_effect=FileNotFoundError('Config not found')):
            result = runner.invoke(cache, ['--clean'])
        assert result.exit_code != 0
        assert 'Config not found' in result.output


    def test_missing_base_dir_raises_error(self):
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={}):
            result = runner.invoke(cache, ['--logs'])
        assert result.exit_code != 0
        assert 'base_dir not set' in result.output


class TestCacheClean:
    def test_downloads_dir_missing_reports_empty(self, tmp_path):
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['--clean'])
        assert result.exit_code == 0
        assert 'already empty' in result.output


    def test_downloads_dir_cleared(self, tmp_path):
        downloads = tmp_path / 'downloads'
        downloads.mkdir()
        (downloads / 'tool').mkdir()
        (downloads / 'archive.tar.gz').write_text('data')
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['--clean'])
        assert result.exit_code == 0
        assert downloads.is_dir()
        assert list(downloads.iterdir()) == []
        assert f'Cleared {downloads}.' in result.output


    def test_short_flag_works(self, tmp_path):
        downloads = tmp_path / 'downloads'
        downloads.mkdir()
        (downloads / 'file').write_text('x')
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['-c'])
        assert result.exit_code == 0
        assert list(downloads.iterdir()) == []


class TestCacheLogs:
    def test_logs_dir_missing_reports_empty(self, tmp_path):
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['--logs'])
        assert result.exit_code == 0
        assert 'already empty' in result.output


    def test_logs_dir_cleared(self, tmp_path):
        logs = tmp_path / 'logs'
        logs.mkdir()
        (logs / 'binit_2026-05-01.log').write_text('log data')
        (logs / 'binit_2026-05-02.log').write_text('log data')
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['--logs'])
        assert result.exit_code == 0
        assert logs.is_dir()
        assert list(logs.iterdir()) == []
        assert f'Cleared {logs}.' in result.output


    def test_short_flag_works(self, tmp_path):
        logs = tmp_path / 'logs'
        logs.mkdir()
        (logs / 'binit.log').write_text('x')
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['-l'])
        assert result.exit_code == 0
        assert list(logs.iterdir()) == []


class TestCacheBothFlags:
    def test_both_flags_clears_both(self, tmp_path):
        downloads = tmp_path / 'downloads'
        logs = tmp_path / 'logs'
        downloads.mkdir()
        logs.mkdir()
        (downloads / 'file.tar.gz').write_text('data')
        (logs / 'binit.log').write_text('log')
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['--clean', '--logs'])
        assert result.exit_code == 0
        assert list(downloads.iterdir()) == []
        assert list(logs.iterdir()) == []
        assert f'Cleared {downloads}.' in result.output
        assert f'Cleared {logs}.' in result.output


    def test_both_flags_one_dir_missing(self, tmp_path):
        downloads = tmp_path / 'downloads'
        downloads.mkdir()
        (downloads / 'file.tar.gz').write_text('data')
        runner = CliRunner()
        with patch('binit.cli.cache.load_config', return_value={'base_dir': str(tmp_path)}):
            result = runner.invoke(cache, ['--clean', '--logs'])
        assert result.exit_code == 0
        assert list(downloads.iterdir()) == []
        assert 'Logs directory is already empty' in result.output
