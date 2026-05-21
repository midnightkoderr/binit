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
        self.installer._name = None


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


    def test_repo_name_bonus_picks_repo_over_sibling(self):
        # kubectx repo: both assets score equal on os/arch/ext; repo name bonus breaks the tie
        self.installer.repo = 'kubectx'
        self.installer._name = None
        asset = self._match([
            'kubens_v0.9.5_linux_x86_64.tar.gz',
            'kubectx_v0.9.5_linux_x86_64.tar.gz',
        ])
        assert asset.name == 'kubectx_v0.9.5_linux_x86_64.tar.gz'


    def test_name_filter_picks_sibling_binary(self):
        self.installer.repo = 'kubectx'
        self.installer._name = 'kubens'
        asset = self._match([
            'kubens_v0.9.5_linux_x86_64.tar.gz',
            'kubectx_v0.9.5_linux_x86_64.tar.gz',
        ])
        assert asset.name == 'kubens_v0.9.5_linux_x86_64.tar.gz'


    def test_name_filter_excludes_non_matching(self):
        self.installer.repo = 'kubectx'
        self.installer._name = 'kubens'
        asset = self._match(['kubectx_v0.9.5_linux_x86_64.tar.gz'])
        assert asset is None


    def test_no_name_no_repo_bonus_for_unrelated(self):
        # asset name doesn't start with repo name — scores below MIN_SCORE
        self.installer.repo = 'grant'
        self.installer._name = None
        asset = self._match(['hadolint-linux-x86_64'])
        assert asset is None


    def test_loose_match_name_os_separator(self):
        # name-OS separator (e.g. hadolint-linux-x86_64) should match when _name matches
        self.installer.repo = 'hadolint'
        self.installer._name = None
        asset = self._match(['hadolint-linux-x86_64'])
        assert asset is not None
        assert asset.name == 'hadolint-linux-x86_64'


    def test_loose_match_name_arch_separator(self):
        # name-arch separator (e.g. starship-x86_64-unknown-linux-gnu.tar.gz)
        self.installer.repo = 'starship'
        self.installer._name = None
        asset = self._match(['starship-x86_64-unknown-linux-gnu.tar.gz'])
        assert asset is not None


    def test_strict_beats_loose_match(self):
        # strict match (name_*) scores higher than loose match (name-arch-*)
        self.installer.repo = 'starship'
        self.installer._name = None
        asset = self._match([
            'starship-x86_64-unknown-linux-gnu.tar.gz',
            'starship_1.0_linux_x86_64.tar.gz',
        ])
        assert asset.name == 'starship_1.0_linux_x86_64.tar.gz'


class TestNameWordBoundary:
    def setup_method(self):
        self.installer = Installer.__new__(Installer)
        self.installer.owner = 'openbao'
        self.installer.repo = 'openbao'
        self.installer._name = 'bao'


    def _match(self, names, os_name='linux', arch_aliases=None):
        if arch_aliases is None:
            arch_aliases = {'amd64', 'x86_64', 'x64'}
        assets = [make_asset(n) for n in names]
        return self.installer._match_asset(assets, os_name, arch_aliases)


    def test_name_picks_exact_over_compound(self):
        asset = self._match([
            'bao-hsm_2.5.3_linux_x86_64.tar.gz',
            'bao_2.5.3_linux_x86_64.tar.gz',
        ])
        assert asset.name == 'bao_2.5.3_linux_x86_64.tar.gz'


    def test_name_rejects_compound_hyphen_name(self):
        asset = self._match(['bao-hsm_2.5.3_linux_x86_64.tar.gz'])
        assert asset is None


    def test_name_matches_hyphen_version_separator(self):
        asset = self._match(['bao-2.5.3-linux-amd64.tar.gz'])
        assert asset.name == 'bao-2.5.3-linux-amd64.tar.gz'


    def test_name_rejects_compound_with_hyphen_version_separator(self):
        asset = self._match(['bao-hsm-2.5.3-linux-amd64.tar.gz'])
        assert asset is None


    def test_repo_bonus_word_boundary_prefers_exact_name(self):
        self.installer._name = None
        self.installer.repo = 'grant'
        asset = self._match([
            'grant-extra_0.6.4_linux_amd64.tar.gz',
            'grant_0.6.4_linux_amd64.tar.gz',
        ])
        assert asset.name == 'grant_0.6.4_linux_amd64.tar.gz'
