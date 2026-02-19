"""Tests for build module: tool checks, source resolution, kernel config, and DB creation."""

from unittest.mock import call, patch

import click
import pytest

from linux_ql.build import check_tool, configure_kernel, create_database, resolve_source


class TestCheckTool:
    def test_passes_when_tool_on_path(self, monkeypatch):
        monkeypatch.setattr("linux_ql.build.shutil.which", lambda _: "/usr/bin/codeql")
        check_tool("codeql", "Install codeql")

    def test_raises_with_hint_when_missing(self, monkeypatch):
        monkeypatch.setattr("linux_ql.build.shutil.which", lambda _: None)
        with pytest.raises(click.ClickException, match="codeql is not installed"):
            check_tool("codeql", "Install from https://example.com")


class TestResolveSource:
    def test_raises_when_no_url_and_no_source(self):
        with pytest.raises(click.ClickException, match="--source or --url"):
            resolve_source("v6.13", url=None, source=None)

    def test_raises_when_source_path_missing(self, tmp_path):
        nonexistent = str(tmp_path / "nope")
        with pytest.raises(click.ClickException, match="not found"):
            resolve_source("v6.13", url=None, source=nonexistent)

    @patch("linux_ql.build.subprocess.run")
    def test_source_calls_git_checkout(self, mock_run, tmp_path):
        src = tmp_path / "linux"
        src.mkdir()

        result = resolve_source("v6.13", url=None, source=str(src))

        assert result == src
        mock_run.assert_called_once_with(
            ["git", "-C", str(src), "checkout", "v6.13"],
            check=True,
        )

    @patch("linux_ql.build.subprocess.run")
    def test_url_downloads_and_extracts(self, mock_run, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        # tar tf returns a directory listing
        mock_run.return_value.stdout = "linux-6.13/\nlinux-6.13/Makefile\n"
        mock_run.return_value.returncode = 0

        url = "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.13.tar.xz"
        result = resolve_source("v6.13", url=url, source=None)

        calls = mock_run.call_args_list
        # First call: curl download
        assert calls[0] == call(
            ["curl", "-L", "--fail", "-o", str(tmp_path / ".downloads" / "linux-6.13.tar.xz"), url],
            check=True,
        )
        # Second call: tar extract
        assert calls[1] == call(
            ["tar", "xf", str(tmp_path / ".downloads" / "linux-6.13.tar.xz"), "-C", str(tmp_path)],
            check=True,
        )
        # Third call: tar tf to detect directory
        assert calls[2].args[0] == ["tar", "tf", str(tmp_path / ".downloads" / "linux-6.13.tar.xz")]
        assert result == tmp_path / "linux-6.13"

    @patch("linux_ql.build.subprocess.run")
    def test_url_uses_cache(self, mock_run, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        # Pre-create cached tarball
        downloads = tmp_path / ".downloads"
        downloads.mkdir()
        (downloads / "linux-6.13.tar.xz").touch()

        mock_run.return_value.stdout = "linux-6.13/\n"
        mock_run.return_value.returncode = 0

        url = "https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.13.tar.xz"
        resolve_source("v6.13", url=url, source=None)

        # Should skip curl, only tar xf + tar tf
        assert len(mock_run.call_args_list) == 2
        assert mock_run.call_args_list[0].args[0][0] == "tar"


class TestConfigureKernel:
    @patch("linux_ql.build.subprocess.run")
    def test_config_target(self, mock_run, tmp_path):
        src = tmp_path / "src"
        build = tmp_path / "build"

        configure_kernel(src, build, "x86_64", "", "defconfig", None)

        calls = mock_run.call_args_list
        # First call: make defconfig
        assert "defconfig" in calls[0].args[0]
        assert "CROSS_COMPILE=" not in " ".join(calls[0].args[0])
        # Second call: make prepare
        assert "prepare" in calls[1].args[0]

    @patch("linux_ql.build.subprocess.run")
    @patch("linux_ql.build.shutil.copy2")
    def test_config_file(self, mock_copy, mock_run, tmp_path):
        src = tmp_path / "src"
        build = tmp_path / "build"

        configure_kernel(src, build, "x86_64", "", "defconfig", "/path/.config")

        mock_copy.assert_called_once_with("/path/.config", build / ".config")
        calls = mock_run.call_args_list
        assert "olddefconfig" in calls[0].args[0]
        assert "prepare" in calls[1].args[0]

    @patch("linux_ql.build.subprocess.run")
    def test_cross_compile_arg_included(self, mock_run, tmp_path):
        src = tmp_path / "src"
        build = tmp_path / "build"

        configure_kernel(src, build, "arm64", "aarch64-linux-gnu-", "defconfig", None)

        make_args = mock_run.call_args_list[0].args[0]
        assert "CROSS_COMPILE=aarch64-linux-gnu-" in make_args


class TestCreateDatabase:
    @patch("linux_ql.build.subprocess.run")
    def test_runs_codeql_create(self, mock_run, tmp_path):
        src = tmp_path / "src"
        build = tmp_path / "build"
        output = tmp_path / "db"

        create_database(src, build, "x86_64", "", output)

        args = mock_run.call_args.args[0]
        assert args[0] == "codeql"
        assert args[1] == "database"
        assert args[2] == "create"
        assert str(output) in args

    @patch("linux_ql.build.subprocess.run")
    def test_includes_cross_compile_in_make_cmd(self, mock_run, tmp_path):
        src = tmp_path / "src"
        build = tmp_path / "build"
        output = tmp_path / "db"

        create_database(src, build, "arm64", "aarch64-linux-gnu-", output)

        args = mock_run.call_args.args[0]
        command_arg = next(a for a in args if a.startswith("--command="))
        assert "CROSS_COMPILE=aarch64-linux-gnu-" in command_arg

    @patch("linux_ql.build.subprocess.run")
    def test_returns_output_path(self, mock_run, tmp_path):
        src, build, db = tmp_path / "src", tmp_path / "build", tmp_path / "db"
        result = create_database(src, build, "x86_64", "", db)
        assert result == tmp_path / "db"
