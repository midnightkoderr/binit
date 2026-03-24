from pathlib import Path

from binit.logger import LoggingConfig


class TestLoggingConfig:
    def setup_method(self, tmp_path=None):
        self.log_file = Path('/tmp/test_binit.log')

    def test_get_config_has_required_keys(self):
        config = LoggingConfig(self.log_file).get_config()
        assert config['version'] == 1
        assert 'formatters' in config
        assert 'handlers' in config
        assert 'root' in config

    def test_get_config_has_stderr_and_file_handlers(self):
        config = LoggingConfig(self.log_file).get_config()
        assert 'stderr' in config['handlers']
        assert 'file' in config['handlers']

    def test_file_handler_uses_filehandler_by_default(self):
        config = LoggingConfig(self.log_file).get_config()
        assert config['handlers']['file']['class'] == 'logging.FileHandler'

    def test_file_handler_uses_rotating_when_rotate_true(self):
        config = LoggingConfig(self.log_file, rotate=True).get_config()
        assert config['handlers']['file']['class'] == 'logging.handlers.TimedRotatingFileHandler'
        assert 'when' in config['handlers']['file']
        assert 'backupCount' in config['handlers']['file']

    def test_file_handler_path(self):
        config = LoggingConfig(self.log_file).get_config()
        assert config['handlers']['file']['filename'] == str(self.log_file)

    def test_log_level_applied_to_stderr(self):
        config = LoggingConfig(self.log_file, log_level='WARNING').get_config()
        assert config['handlers']['stderr']['level'] == 'WARNING'

    def test_file_level_applied(self):
        config = LoggingConfig(self.log_file, file_level='ERROR').get_config()
        assert config['handlers']['file']['level'] == 'ERROR'

    def test_default_formatters_used_when_none_provided(self):
        config = LoggingConfig(self.log_file).get_config()
        assert 'default' in config['formatters']
        assert 'format' in config['formatters']['default']

    def test_custom_formatters_override_default(self):
        custom = {'custom': {'format': '%(message)s'}}
        config = LoggingConfig(self.log_file, formatters=custom).get_config()
        assert 'custom' in config['formatters']
        assert 'default' not in config['formatters']

    def test_root_logger_has_both_handlers(self):
        config = LoggingConfig(self.log_file).get_config()
        assert set(config['root']['handlers']) == {'stderr', 'file'}
