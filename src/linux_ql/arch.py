"""Architecture map and cross-compiler validation."""

import shutil

import click

ARCH_MAP: dict[str, str] = {
    "x86_64": "",
    "arm64": "aarch64-linux-gnu-",
    "arm": "arm-linux-gnueabihf-",
    "riscv": "riscv64-linux-gnu-",
    "mips": "mips-linux-gnu-",
    "powerpc": "powerpc64-linux-gnu-",
    "s390": "s390x-linux-gnu-",
}

SUPPORTED_ARCHES = list(ARCH_MAP.keys())

DEFAULT_TOOLCHAIN = "gcc-13"


def validate_arch(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Click callback that rejects unsupported architectures."""
    if value not in ARCH_MAP:
        supported = ", ".join(SUPPORTED_ARCHES)
        raise click.BadParameter(f"Unsupported: {value}. Supported: {supported}")
    return value


def check_cross_compiler(arch: str) -> None:
    """Verify the cross-compiler toolchain is installed."""
    prefix = ARCH_MAP[arch]
    if not prefix:
        return
    gcc = f"{prefix}gcc"
    if shutil.which(gcc):
        return
    pkg = prefix.rstrip("-")
    raise click.ClickException(
        f"Cross-compiler {gcc} not found.\n\n"
        f"Install on Debian/Ubuntu:\n"
        f"  sudo apt install gcc-{pkg}\n\n"
        f"Install on Fedora:\n"
        f"  sudo dnf install gcc-{pkg}\n\n"
        f"Or use: linux-ql docker"
    )
