from types import SimpleNamespace

import pytest

from binit.installer import Installer


def make_asset(name: str) -> SimpleNamespace:
    return SimpleNamespace(name=name, browser_download_url=f'https://example.com/{name}')


class TestMatchAsset:
    def setup_method(self):
        self.installer = Installer.__new__(Installer)
        self.installer.owner = 'anchore'
        self.installer.repo = 'grant'

    def _match(self, names, os_name='linux', arch_aliases=None):
        if arch_aliases is None:
            arch_aliases = {'amd64', 'x86_64', 'x64'}
        assets = [make_asset(n) for n in names]
        return self.installer._match_asset(assets, os_name, arch_aliases)

    def test_picks_tar_gz(self):
        asset = self._match([
            'grant_0.6.4_linux_amd64.deb',
            'grant_0.6.4_linux_amd64.tar.gz',
        ])
        assert asset.name == 'grant_0.6.4_linux_amd64.tar.gz'

    def test_prefers_tar_gz_over_zip(self):
        asset = self._match([
            'grant_0.6.4_linux_amd64.zip',
            'grant_0.6.4_linux_amd64.tar.gz',
        ])
        assert asset.name == 'grant_0.6.4_linux_amd64.tar.gz'

    def test_falls_back_to_zip(self):
        asset = self._match(['grant_0.6.4_linux_amd64.zip'])
        assert asset.name == 'grant_0.6.4_linux_amd64.zip'

    def test_ignores_deb_rpm(self):
        asset = self._match([
            'grant_0.6.4_linux_amd64.deb',
            'grant_0.6.4_linux_amd64.rpm',
        ])
        assert asset is None

    def test_ignores_sbom_sig_txt(self):
        asset = self._match([
            'grant_0.6.4_linux_amd64.sbom',
            'grant_0.6.4_checksums.txt',
            'grant_0.6.4_checksums.txt.sig',
        ])
        assert asset is None

    def test_no_match_wrong_os(self):
        asset = self._match(['grant_0.6.4_darwin_amd64.tar.gz'], os_name='linux')
        assert asset is None

    def test_no_match_wrong_arch(self):
        asset = self._match(
            ['grant_0.6.4_linux_arm64.tar.gz'],
            arch_aliases={'amd64', 'x86_64'},
        )
        assert asset is None

    def test_arch_alias_matched(self):
        asset = self._match(
            ['grant_0.6.4_linux_x86_64.tar.gz'],
            arch_aliases={'amd64', 'x86_64'},
        )
        assert asset is not None

    def test_tgz_matched(self):
        asset = self._match(['grant_0.6.4_linux_amd64.tgz'])
        assert asset.name == 'grant_0.6.4_linux_amd64.tgz'

    def test_tar_bz2_matched(self):
        asset = self._match(['grant_0.6.4_linux_amd64.tar.bz2'])
        assert asset.name == 'grant_0.6.4_linux_amd64.tar.bz2'

    def test_returns_none_empty_assets(self):
        asset = self._match([])
        assert asset is None
