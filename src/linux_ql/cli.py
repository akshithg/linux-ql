"""Click CLI entry point for linux-ql."""

import os
from pathlib import Path

import click

from linux_ql.arch import ARCH_MAP, DEFAULT_TOOLCHAIN, check_cross_compiler, validate_arch
from linux_ql.build import check_tool, configure_kernel, create_database, resolve_source
from linux_ql.docker import run_in_docker
from linux_ql.query import export_csv, run_analysis


@click.group()
def main() -> None:
    """CodeQL static analysis toolkit for the Linux kernel."""


@main.command()
@click.option("-v", "--version", "tag", default="v6.13", help="Git tag to checkout.")
@click.option("-u", "--url", default=None, help="Kernel tarball URL.")
@click.option(
    "-a",
    "--arch",
    default="x86_64",
    callback=validate_arch,
    expose_value=True,
    is_eager=False,
    help=f"Target architecture ({', '.join(ARCH_MAP)}).",
)
@click.option(
    "-S",
    "--source",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Path to local kernel source tree.",
)
@click.option("-c", "--config", default="defconfig", help="Make config target.")
@click.option(
    "-f",
    "--config-file",
    default=None,
    type=click.Path(exists=True),
    help="Path to a .config file (runs olddefconfig).",
)
@click.option("-o", "--output", default=None, type=click.Path(), help="Output database path.")
def build(
    tag: str,
    url: str | None,
    source: str | None,
    arch: str,
    config: str,
    config_file: str | None,
    output: str | None,
) -> None:
    """Build a CodeQL database from a Linux kernel source tree."""
    check_tool("codeql", "Install from https://github.com/github/codeql-cli-binaries")
    check_cross_compiler(arch)

    src_dir = resolve_source(tag, url, source)

    cross_compile = ARCH_MAP[arch]
    build_dir = Path.cwd() / f"linux-{tag}-{arch}"

    configure_kernel(src_dir, build_dir, arch, cross_compile, config, config_file)

    db_path = Path(output) if output else Path(f"linux-{tag}-{arch}-codeql.db")
    create_database(src_dir, build_dir, arch, cross_compile, db_path)


@main.command()
@click.option(
    "-d",
    "--database",
    required=True,
    type=click.Path(exists=True),
    help="Path to CodeQL database.",
)
@click.option(
    "-s",
    "--suite",
    default="all",
    type=click.Choice(["all", "heap", "structures", "security"]),
    help="Query suite to run.",
)
@click.option("-o", "--output-dir", default="results", help="Output directory.")
@click.option(
    "-t",
    "--threads",
    default=os.cpu_count() or 4,
    type=int,
    help="Number of analysis threads.",
)
@click.option("--csv", "do_csv", is_flag=True, help="Also export results as CSV.")
def query(
    database: str,
    suite: str,
    output_dir: str,
    threads: int,
    do_csv: bool,
) -> None:
    """Run CodeQL queries against a Linux kernel database."""
    check_tool("codeql", "Install from https://github.com/github/codeql-cli-binaries")

    db_path = Path(database)
    out_path = Path(output_dir)

    run_analysis(db_path, suite, out_path, threads)

    if do_csv:
        export_csv(db_path, out_path)

    click.echo("==> Done.")


@main.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.option(
    "-S",
    "--source",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Path to local kernel source tree (mounted into container).",
)
@click.option(
    "-a",
    "--arch",
    default="x86_64",
    callback=validate_arch,
    expose_value=True,
    is_eager=False,
    help=f"Target architecture ({', '.join(ARCH_MAP)}).",
)
@click.option(
    "--toolchain",
    default=DEFAULT_TOOLCHAIN,
    help="GCC toolchain version (e.g. gcc-13).",
)
@click.argument("build_args", nargs=-1, type=click.UNPROCESSED)
def docker(
    source: str | None,
    arch: str,
    toolchain: str,
    build_args: tuple[str, ...],
) -> None:
    """Build a CodeQL database inside Docker.

    Each architecture gets its own lean image built from TuxMake's
    per-arch base (tuxmake/{arch}_{toolchain}). All extra arguments
    after -- are forwarded to the build command inside the container.
    """
    check_tool("docker", "Install from https://docs.docker.com/get-docker/")

    project_root = Path(__file__).resolve().parent.parent.parent
    run_in_docker(arch, toolchain, build_args, source=source, context_dir=project_root)
