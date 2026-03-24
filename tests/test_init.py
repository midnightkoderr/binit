from click.testing import CliRunner

from binit.cli.init import Initialiser, init
from binit.core.constants import VERSION


class TestInitialiser:
    def test_creates_expected_dirs(self, tmp_path):
        base = tmp_path / 'binit'
        Initialiser(base_dir=base).run()
        assert base.is_dir()
        assert (base / 'bin').is_dir()
        assert (base / 'downloads').is_dir()
        assert (base / 'logs').is_dir()

    def test_creates_config_file(self, tmp_path):
        base = tmp_path / 'binit'
        Initialiser(base_dir=base).run()
        assert (base / 'config.yaml').is_file()

    def test_config_fields(self, tmp_path):
        base = tmp_path / 'binit'
        Initialiser(base_dir=base).run()
        from binit.utils import make_yaml_handler, ConfigManager
        config = ConfigManager(make_yaml_handler()).load_config(base / 'config.yaml')
        assert config['binit_version'] == VERSION
        assert config['os'] in {'linux', 'darwin', 'windows'}
        assert 'arch' in config
        assert 'init_at' in config
        assert config['base_dir'] == str(base)
        assert config['installed_tools'] == []

    def test_skips_config_if_exists(self, tmp_path):
        base = tmp_path / 'binit'
        Initialiser(base_dir=base).run()
        config_file = base / 'config.yaml'
        original_mtime = config_file.stat().st_mtime
        Initialiser(base_dir=base).run()
        assert config_file.stat().st_mtime == original_mtime

    def test_reinit_deletes_and_recreates(self, tmp_path):
        base = tmp_path / 'binit'
        Initialiser(base_dir=base).run()
        sentinel = base / 'sentinel.txt'
        sentinel.write_text('should be gone')
        Initialiser(base_dir=base, reinit=True).run()
        assert not sentinel.exists()
        assert base.is_dir()
        assert (base / 'config.yaml').is_file()

    def test_reinit_overwrites_config(self, tmp_path):
        base = tmp_path / 'binit'
        Initialiser(base_dir=base).run()
        config_file = base / 'config.yaml'
        original_inode = config_file.stat().st_ino
        Initialiser(base_dir=base, reinit=True).run()
        assert config_file.stat().st_ino != original_inode

    def test_skips_existing_dirs_without_reinit(self, tmp_path):
        base = tmp_path / 'binit'
        base.mkdir()
        (base / 'bin').mkdir()
        Initialiser(base_dir=base).run()
        assert (base / 'bin').is_dir()


class TestInitCommand:
    def test_init_creates_base_dir(self, tmp_path):
        runner = CliRunner()
        base = tmp_path / 'binit'
        result = runner.invoke(init, ['--base-dir', str(base)])
        assert result.exit_code == 0
        assert base.is_dir()

    def test_reinit_flag(self, tmp_path):
        runner = CliRunner()
        base = tmp_path / 'binit'
        runner.invoke(init, ['--base-dir', str(base)])
        sentinel = base / 'sentinel.txt'
        sentinel.write_text('should be gone')
        result = runner.invoke(init, ['--base-dir', str(base), '--reinit'])
        assert result.exit_code == 0
        assert not sentinel.exists()
