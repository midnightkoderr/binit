from unittest.mock import patch

from click.testing import CliRunner

from importlib.metadata import version

from binit.cli.init import init
from binit.initialiser import Initialiser
from binit.utils import ConfigManager, make_yaml_handler


def make_initialiser(tmp_path, reinit=False):
    base = tmp_path / 'binit'
    initialiser = Initialiser(base_dir=base, reinit=reinit)
    return initialiser, base


class TestInitialiser:
    def test_creates_expected_dirs(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        initialiser.run()
        assert base.is_dir()
        assert (base / 'bin').is_dir()
        assert (base / 'downloads').is_dir()
        assert (base / 'logs').is_dir()


    def test_creates_config_file(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        initialiser.run()
        assert (base / 'config.yaml').is_file()


    def test_config_fields(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        initialiser.run()
        config = ConfigManager(make_yaml_handler()).load_config(base / 'config.yaml')
        assert config['binit_version'] == version('binit')
        assert config['os'] in {'linux', 'darwin', 'windows'}
        assert 'arch' in config
        assert 'init_at' in config
        assert config['base_dir'] == str(base)
        assert config['installed_tools'] == {}


    def test_skips_config_if_exists(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        initialiser.run()
        config_file = base / 'config.yaml'
        original_mtime = config_file.stat().st_mtime
        make_initialiser(tmp_path)[0].run()
        assert config_file.stat().st_mtime == original_mtime


    def test_reinit_deletes_and_recreates(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        initialiser.run()
        sentinel = base / 'sentinel.txt'
        sentinel.write_text('should be gone')
        make_initialiser(tmp_path, reinit=True)[0].run()
        assert not sentinel.exists()
        assert base.is_dir()
        assert (base / 'config.yaml').is_file()


    def test_reinit_overwrites_config(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        initialiser.run()
        config_file = base / 'config.yaml'
        original_inode = config_file.stat().st_ino
        make_initialiser(tmp_path, reinit=True)[0].run()
        assert config_file.stat().st_ino != original_inode


    def test_skips_existing_dirs_without_reinit(self, tmp_path):
        initialiser, base = make_initialiser(tmp_path)
        base.mkdir()
        (base / 'bin').mkdir()
        initialiser.run()
        assert (base / 'bin').is_dir()


class TestInitCommand:
    def test_init_runs_successfully(self, tmp_path):
        base = tmp_path / 'binit'
        runner = CliRunner()
        with patch('binit.initialiser.DEFAULT_BASE_DIR', base), patch('binit.cli.init.Initialiser') as mock:
            mock.return_value.run.return_value = None
            result = runner.invoke(init)
        assert result.exit_code == 0
        mock.assert_called_once_with(reinit=False)


    def test_reinit_flag_passed(self, tmp_path):
        runner = CliRunner()
        with patch('binit.cli.init.Initialiser') as mock:
            mock.return_value.run.return_value = None
            result = runner.invoke(init, ['--reinit'])
        assert result.exit_code == 0
        mock.assert_called_once_with(reinit=True)
