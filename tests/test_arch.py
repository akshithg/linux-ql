"""Tests for architecture validation and cross-compiler checks."""

from unittest.mock import MagicMock

import click
import pytest

from linux_ql.arch import ARCH_MAP, SUPPORTED_ARCHES, check_cross_compiler, validate_arch


class TestArchMap:
    def test_contains_all_seven_architectures(self):
        expected = {"x86_64", "arm64", "arm", "riscv", "mips", "powerpc", "s390"}
        assert set(ARCH_MAP.keys()) == expected

    def test_x86_64_has_empty_prefix(self):
        assert ARCH_MAP["x86_64"] == ""

    def test_supported_arches_matches_keys(self):
        assert list(ARCH_MAP.keys()) == SUPPORTED_ARCHES


class TestValidateArch:
    def test_returns_valid_arch(self):
        ctx = MagicMock(spec=click.Context)
        param = MagicMock(spec=click.Parameter)
        assert validate_arch(ctx, param, "arm64") == "arm64"

    def test_raises_bad_parameter_for_invalid_arch(self):
        ctx = MagicMock(spec=click.Context)
        param = MagicMock(spec=click.Parameter)
        with pytest.raises(click.BadParameter, match="Unsupported: sparc"):
            validate_arch(ctx, param, "sparc")


class TestCheckCrossCompiler:
    def test_noop_for_x86_64(self):
        # Should not raise — x86_64 has empty prefix, no compiler check needed
        check_cross_compiler("x86_64")

    def test_passes_when_compiler_found(self, monkeypatch):
        fake_path = "/usr/bin/aarch64-linux-gnu-gcc"
        monkeypatch.setattr("linux_ql.arch.shutil.which", lambda _: fake_path)
        check_cross_compiler("arm64")

    def test_raises_when_compiler_missing(self, monkeypatch):
        monkeypatch.setattr("linux_ql.arch.shutil.which", lambda _: None)
        with pytest.raises(click.ClickException, match="aarch64-linux-gnu-gcc not found"):
            check_cross_compiler("arm64")

    def test_error_message_includes_install_hint(self, monkeypatch):
        monkeypatch.setattr("linux_ql.arch.shutil.which", lambda _: None)
        with pytest.raises(click.ClickException, match="sudo apt install"):
            check_cross_compiler("arm64")
