"""CLI integration tests using Click's CliRunner."""

from unittest.mock import patch

from click.testing import CliRunner

from linux_ql.cli import main


@patch("linux_ql.build.shutil.which", return_value="/usr/bin/codeql")
class TestHelpOutputs:
    """Verify all commands appear in --help and accept --help themselves."""

    def test_main_help(self, _mock_which):
        result = CliRunner().invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "build" in result.output
        assert "query" in result.output
        assert "docker" in result.output

    def test_build_help(self, _mock_which):
        result = CliRunner().invoke(main, ["build", "--help"])
        assert result.exit_code == 0
        assert "--arch" in result.output

    def test_query_help(self, _mock_which):
        result = CliRunner().invoke(main, ["query", "--help"])
        assert result.exit_code == 0
        assert "--database" in result.output

    def test_docker_help(self, _mock_which):
        result = CliRunner().invoke(main, ["docker", "--help"])
        assert result.exit_code == 0
        assert "--arch" in result.output
        assert "--toolchain" in result.output


class TestValidationErrors:
    def test_build_bad_arch_exits_2(self):
        result = CliRunner().invoke(main, ["build", "-a", "sparc"])
        assert result.exit_code == 2
        assert "Unsupported" in result.output

    def test_query_invalid_suite_exits_2(self):
        result = CliRunner().invoke(main, ["query", "-d", "fake.db", "-s", "invalid"])
        assert result.exit_code == 2
        assert "Invalid value" in result.output

    def test_query_missing_database_exits_2(self):
        result = CliRunner().invoke(main, ["query"])
        assert result.exit_code == 2
        assert "Missing option" in result.output or "required" in result.output.lower()


class TestBuildErrors:
    @patch("linux_ql.build.shutil.which", return_value="/usr/bin/codeql")
    @patch("linux_ql.arch.shutil.which", return_value=None)
    def test_build_without_source_or_url(self, _arch_which, _build_which):
        # codeql is found but x86_64 needs no cross compiler check,
        # so resolve_source is the first thing that fails
        result = CliRunner().invoke(main, ["build"])
        assert result.exit_code == 1
        assert "--source or --url" in result.output
