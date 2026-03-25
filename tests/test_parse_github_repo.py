import pytest

from binit.utils import parse_github_repo


class TestParseGithubRepo:
    def test_owner_repo_format(self):
        owner, repo = parse_github_repo('anchore/grant')
        assert owner == 'anchore'
        assert repo == 'grant'


    def test_full_https_url(self):
        owner, repo = parse_github_repo('https://github.com/anchore/grant')
        assert owner == 'anchore'
        assert repo == 'grant'


    def test_full_url_with_trailing_slash(self):
        owner, repo = parse_github_repo('https://github.com/anchore/grant/')
        assert owner == 'anchore'
        assert repo == 'grant'


    def test_owner_repo_with_leading_slash(self):
        owner, repo = parse_github_repo('/anchore/grant')
        assert owner == 'anchore'
        assert repo == 'grant'


    def test_invalid_no_slash_raises(self):
        with pytest.raises(ValueError, match='Invalid GitHub repo'):
            parse_github_repo('justarepo')


    def test_invalid_empty_raises(self):
        with pytest.raises(ValueError, match='Invalid GitHub repo'):
            parse_github_repo('')


    def test_url_with_extra_path_segments(self):
        owner, repo = parse_github_repo('https://github.com/anchore/grant/releases')
        assert owner == 'anchore'
        assert repo == 'grant'
