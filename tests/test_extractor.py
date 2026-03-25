import gzip
import io
import tarfile
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from binit.extractor import extract, find_executable
from binit.utils import FileKind


ELF_MAGIC = b'\x7fELF' + b'\x00' * 60


def make_tar_gz(dest: Path, members: dict[str, bytes]) -> Path:
    archive = dest / 'archive.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for name, content in members.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return archive


def make_zip(dest: Path, members: dict[str, bytes]) -> Path:
    archive = dest / 'archive.zip'
    with zipfile.ZipFile(archive, 'w') as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return archive


class TestExtract:
    def test_tar_gz_extracted(self, tmp_path):
        archive = make_tar_gz(tmp_path, {'hello.txt': b'hello'})
        extract(archive)
        assert (tmp_path / 'hello.txt').exists()


    def test_zip_extracted(self, tmp_path):
        archive = make_zip(tmp_path, {'hello.txt': b'hello'})
        extract(archive)
        assert (tmp_path / 'hello.txt').exists()


    def test_binary_skipped(self, tmp_path):
        binary = tmp_path / 'mybinary'
        binary.write_bytes(ELF_MAGIC)
        result = extract(binary)
        assert result == binary


    def test_unknown_file_skipped(self, tmp_path):
        f = tmp_path / 'data.bin'
        f.write_bytes(b'\x00\x01\x02\x03')
        result = extract(f)
        assert result == f


    def test_max_depth_stops_recursion(self, tmp_path):
        archive = make_tar_gz(tmp_path, {'inner.txt': b'data'})
        result = extract(archive, _depth=3, _max_depth=3)
        assert result == archive


    def test_original_archive_not_re_extracted(self, tmp_path):
        archive = make_tar_gz(tmp_path, {'file.txt': b'content'})
        with patch('binit.extractor.extract', wraps=extract) as mock_extract:
            extract(archive)
            # original archive must not be passed as a nested call
            nested_calls = [c.args[0] for c in mock_extract.call_args_list[1:]]
            assert archive not in nested_calls


    def test_nested_archive_recursed(self, tmp_path):
        # inner archive is a direct child after outer extraction
        inner_buf = io.BytesIO()
        with tarfile.open(fileobj=inner_buf, mode='w:gz') as tar:
            data = b'deep content'
            info = tarfile.TarInfo(name='deep.txt')
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        inner_bytes = inner_buf.getvalue()

        outer_archive = tmp_path / 'outer.tar.gz'
        with tarfile.open(outer_archive, 'w:gz') as tar:
            info = tarfile.TarInfo(name='inner.tar.gz')
            info.size = len(inner_bytes)
            tar.addfile(info, io.BytesIO(inner_bytes))

        extract(outer_archive)
        assert (tmp_path / 'deep.txt').exists()


class TestFindExecutable:
    def test_finds_elf_binary(self, tmp_path):
        binary = tmp_path / 'mytool'
        binary.write_bytes(ELF_MAGIC)
        result = find_executable(tmp_path)
        assert result == binary


    def test_returns_none_when_no_binary(self, tmp_path):
        (tmp_path / 'readme.txt').write_text('hello')
        result = find_executable(tmp_path)
        assert result is None


    def test_finds_binary_in_subdirectory(self, tmp_path):
        subdir = tmp_path / 'sub'
        subdir.mkdir()
        binary = subdir / 'tool'
        binary.write_bytes(ELF_MAGIC)
        result = find_executable(tmp_path)
        assert result == binary


    def test_ignores_non_binary_files(self, tmp_path):
        (tmp_path / 'data.bin').write_bytes(b'\x00\x01\x02')
        result = find_executable(tmp_path)
        assert result is None


    def test_preferred_name_selects_correct_binary(self, tmp_path):
        (tmp_path / 'kubectx').write_bytes(ELF_MAGIC)
        (tmp_path / 'kubens').write_bytes(ELF_MAGIC)
        result = find_executable(tmp_path, preferred_name='kubens')
        assert result.name == 'kubens'


    def test_preferred_name_falls_back_to_first_when_not_found(self, tmp_path):
        binary = tmp_path / 'kubectx'
        binary.write_bytes(ELF_MAGIC)
        result = find_executable(tmp_path, preferred_name='kubens')
        assert result == binary
