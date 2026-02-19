"""Docker image build and container run."""

import subprocess
from pathlib import Path

import click

# CodeQL only ships x86_64 Linux binaries, so we always build
# and run images as linux/amd64 (Rosetta handles emulation on
# arm64 Docker hosts like Apple Silicon).
_PLATFORM = "linux/amd64"


def ensure_image(arch: str, toolchain: str, context_dir: Path) -> str:
    """Build the per-arch Docker image if it doesn't already exist."""
    image_name = f"linux-ql-{arch}"
    tuxmake_image = f"tuxmake/{arch}_{toolchain}:latest"

    result = subprocess.run(
        ["docker", "image", "inspect", image_name],
        capture_output=True,
    )
    if result.returncode == 0:
        return image_name

    click.echo(f"==> Building Docker image '{image_name}' from {tuxmake_image}...")
    subprocess.run(
        [
            "docker",
            "build",
            "--platform",
            _PLATFORM,
            "--build-arg",
            f"TUXMAKE_IMAGE={tuxmake_image}",
            "-t",
            image_name,
            str(context_dir),
        ],
        check=True,
    )
    return image_name


def run_in_docker(
    arch: str,
    toolchain: str,
    forward_args: tuple[str, ...],
    *,
    source: str | None = None,
    context_dir: Path,
) -> None:
    """Run the linux-ql build command inside a Docker container."""
    image_name = ensure_image(arch, toolchain, context_dir)

    docker_args = [
        "docker",
        "run",
        "--rm",
        "--platform",
        _PLATFORM,
        "-v",
        f"{Path.cwd()}:/output",
        "-w",
        "/output",
    ]

    if source:
        docker_args.extend(
            [
                "-v",
                f"{source}:/kernel:ro",
            ]
        )
        forward_args = ("-S", "/kernel", *forward_args)

    click.echo("==> Running in Docker...")
    subprocess.run(
        [*docker_args, image_name, *forward_args],
        check=True,
    )
