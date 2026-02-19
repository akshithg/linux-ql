"""Tests for Docker image management and container execution."""

from unittest.mock import MagicMock, patch

from linux_ql.docker import ensure_image, run_in_docker


class TestEnsureImage:
    @patch("linux_ql.docker.subprocess.run")
    def test_skips_build_when_image_exists(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0)

        name = ensure_image("x86_64", "gcc-13", tmp_path)

        assert name == "linux-ql-x86_64"
        mock_run.assert_called_once()
        assert mock_run.call_args.args[0] == [
            "docker",
            "image",
            "inspect",
            "linux-ql-x86_64",
        ]

    @patch("linux_ql.docker.subprocess.run")
    def test_builds_when_image_missing(self, mock_run, tmp_path):
        inspect_result = MagicMock(returncode=1)
        mock_run.side_effect = [inspect_result, MagicMock()]

        name = ensure_image("arm64", "gcc-13", tmp_path)

        assert name == "linux-ql-arm64"
        assert mock_run.call_count == 2
        build_args = mock_run.call_args_list[1].args[0]
        assert build_args == [
            "docker",
            "build",
            "--platform",
            "linux/amd64",
            "--build-arg",
            "TUXMAKE_IMAGE=tuxmake/arm64_gcc-13:latest",
            "-t",
            "linux-ql-arm64",
            str(tmp_path),
        ]

    @patch("linux_ql.docker.subprocess.run")
    def test_uses_custom_toolchain(self, mock_run, tmp_path):
        inspect_result = MagicMock(returncode=1)
        mock_run.side_effect = [inspect_result, MagicMock()]

        name = ensure_image("riscv", "gcc-14", tmp_path)

        assert name == "linux-ql-riscv"
        build_args = mock_run.call_args_list[1].args[0]
        assert "TUXMAKE_IMAGE=tuxmake/riscv_gcc-14:latest" in build_args


class TestRunInDocker:
    @patch("linux_ql.docker.ensure_image", return_value="linux-ql-x86_64")
    @patch("linux_ql.docker.subprocess.run")
    def test_constructs_correct_args(self, mock_run, mock_ensure):
        run_in_docker(
            "x86_64",
            "gcc-13",
            ("-v", "v6.13", "-a", "arm64"),
            context_dir=MagicMock(),
        )

        args = mock_run.call_args.args[0]
        assert args[0] == "docker"
        assert args[1] == "run"
        assert "--rm" in args
        assert "--platform" in args
        assert "linux/amd64" in args
        assert "linux-ql-x86_64" in args
        assert "v6.13" in args

    @patch("linux_ql.docker.ensure_image", return_value="linux-ql-arm64")
    @patch("linux_ql.docker.subprocess.run")
    def test_mounts_source_when_provided(self, mock_run, mock_ensure):
        run_in_docker(
            "arm64",
            "gcc-13",
            (),
            source="/home/user/linux",
            context_dir=MagicMock(),
        )

        args = mock_run.call_args.args[0]
        idx = args.index("/home/user/linux:/kernel:ro")
        assert args[idx - 1] == "-v"
        assert "-S" in args
        assert "/kernel" in args

    @patch("linux_ql.docker.ensure_image", return_value="linux-ql-x86_64")
    @patch("linux_ql.docker.subprocess.run")
    def test_no_source_mount_when_omitted(self, mock_run, mock_ensure):
        run_in_docker("x86_64", "gcc-13", (), context_dir=MagicMock())

        args = mock_run.call_args.args[0]
        assert "/kernel:ro" not in " ".join(args)
