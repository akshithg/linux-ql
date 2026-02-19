"""Kernel source resolution, configuration, and CodeQL database creation."""

import os
import shutil
import subprocess
from pathlib import Path

import click


def check_tool(name: str, install_hint: str) -> None:
    """Verify a required tool is on PATH."""
    if not shutil.which(name):
        raise click.ClickException(f"{name} is not installed. {install_hint}")


def resolve_source(
    version: str,
    url: str | None,
    source: str | None,
) -> Path:
    """Obtain kernel source from a tarball URL or local git checkout.

    Returns the path to the kernel source directory.
    """
    if url:
        click.echo("==> Downloading kernel tarball...")
        tarball_name = url.rsplit("/", maxsplit=1)[-1]
        download_dir = Path.cwd() / ".downloads"
        download_dir.mkdir(exist_ok=True)
        tarball_path = download_dir / tarball_name

        if not tarball_path.exists():
            subprocess.run(
                ["curl", "-L", "--fail", "-o", str(tarball_path), url],
                check=True,
            )
        else:
            click.echo(f"    Using cached {tarball_path}")

        click.echo("==> Extracting tarball...")
        subprocess.run(
            ["tar", "xf", str(tarball_path), "-C", str(Path.cwd())],
            check=True,
        )

        # Detect extracted directory name (e.g. linux-6.13)
        result = subprocess.run(
            ["tar", "tf", str(tarball_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        top_dir = result.stdout.split("\n", maxsplit=1)[0].split("/")[0]
        src_dir = Path.cwd() / top_dir
        click.echo(f"    Source directory: {src_dir}")
        return src_dir

    if not source:
        raise click.ClickException("Use --source or --url to specify kernel source.")

    src_path = Path(source)
    if not src_path.is_dir():
        raise click.ClickException(f"Source directory not found: {source}")

    click.echo(f"==> Checking out {version}...")
    subprocess.run(
        ["git", "-C", str(src_path), "checkout", version],
        check=True,
    )
    return src_path


def configure_kernel(
    src_dir: Path,
    build_dir: Path,
    arch: str,
    cross_compile: str,
    config: str,
    config_file: str | None,
) -> None:
    """Configure the kernel build."""
    make_args = [
        "make",
        "-C",
        str(src_dir),
        f"O={build_dir}",
        f"ARCH={arch}",
    ]
    if cross_compile:
        make_args.append(f"CROSS_COMPILE={cross_compile}")

    click.echo(f"==> Configuring kernel (arch={arch})...")

    if config_file:
        build_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config_file, build_dir / ".config")
        subprocess.run([*make_args, "olddefconfig"], check=True)
    else:
        subprocess.run([*make_args, config], check=True)

    subprocess.run([*make_args, "prepare"], check=True)


def create_database(
    src_dir: Path,
    build_dir: Path,
    arch: str,
    cross_compile: str,
    output: Path,
) -> Path:
    """Run codeql database create with kernel build as the traced command."""
    nproc = os.cpu_count() or 4

    make_cmd = f"make -C {src_dir} O={build_dir} ARCH={arch}"
    if cross_compile:
        make_cmd += f" CROSS_COMPILE={cross_compile}"
    make_cmd += f" -j{nproc}"

    click.echo("==> Building kernel with CodeQL tracing...")
    click.echo(f"    Database: {output}")

    subprocess.run(
        [
            "codeql",
            "database",
            "create",
            str(output),
            "--language=cpp",
            f"--source-root={src_dir}",
            f"--command={make_cmd}",
        ],
        check=True,
    )

    click.echo(f"==> Done. Database: {output}")
    return output
