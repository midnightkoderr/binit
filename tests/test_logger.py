import logging
from datetime import date
from pathlib import Path

from binit.logger import get_logger, setup_file_logging


class TestSetupFileLogging:
    def test_creates_log_file(self, tmp_path):
        setup_file_logging(tmp_path)
        expected = tmp_path / f'binit_{date.today()}.log'
        assert expected.exists()


    def test_creates_log_dir_if_missing(self, tmp_path):
        log_dir = tmp_path / 'logs'
        setup_file_logging(log_dir)
        assert log_dir.is_dir()


    def test_adds_file_handler(self, tmp_path):
        root = logging.getLogger()
        before = len(root.handlers)
        setup_file_logging(tmp_path)
        after = len(root.handlers)
        assert after > before


    def teardown_method(self):
        root = logging.getLogger()
        for h in root.handlers[:]:
            if isinstance(h, logging.FileHandler):
                h.close()
                root.removeHandler(h)


class TestGetLogger:
    def test_returns_logger(self):
        logger = get_logger('binit.test')
        assert isinstance(logger, logging.Logger)


    def test_logger_name(self):
        logger = get_logger('binit.test')
        assert logger.name == 'binit.test'


    def test_empty_name_returns_root(self):
        logger = get_logger('')
        assert logger is logging.getLogger('')
