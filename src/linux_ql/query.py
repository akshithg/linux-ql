"""Query suite resolution, CodeQL analysis, and CSV export."""

import subprocess
from pathlib import Path

import click


def queries_dir() -> Path:
    """Resolve the queries/ directory relative to the repo root.

    Walks up from this file's location to find the queries/ directory.
    """
    current = Path(__file__).resolve().parent
    # Walk up: src/linux_ql/ -> src/ -> repo root
    for _ in range(5):
        candidate = current / "queries"
        if candidate.is_dir():
            return candidate
        current = current.parent
    raise click.ClickException("Cannot locate queries/ directory.")


def install_pack(qdir: Path) -> None:
    """Install CodeQL pack dependencies."""
    click.echo("==> Installing pack dependencies...")
    subprocess.run(["codeql", "pack", "install", str(qdir)], check=True)


def run_analysis(
    database: Path,
    suite: str,
    output_dir: Path,
    threads: int,
) -> Path:
    """Run codeql database analyze with the given suite.

    Returns the path to the generated SARIF file.
    """
    qdir = queries_dir()
    suite_file = qdir / "suites" / f"{suite}.qls"
    if not suite_file.exists():
        raise click.ClickException(
            f"Unknown suite: {suite}. Available: all, heap, structures, security"
        )

    install_pack(qdir)

    output_dir.mkdir(parents=True, exist_ok=True)
    db_name = Path(database).stem
    sarif_out = output_dir / f"{db_name}-{suite}.sarif"

    click.echo(f"==> Running {suite} suite against {database}...")
    click.echo(f"    Threads: {threads}")
    click.echo(f"    Output:  {sarif_out}")

    subprocess.run(
        [
            "codeql",
            "database",
            "analyze",
            str(database),
            "--format=sarif-latest",
            f"--output={sarif_out}",
            f"--threads={threads}",
            "--",
            str(suite_file),
        ],
        check=True,
    )

    click.echo(f"==> SARIF results: {sarif_out}")
    return sarif_out


def export_csv(database: Path, output_dir: Path) -> list[Path]:
    """Export BQRS results to CSV files.

    Returns list of generated CSV paths.
    """
    click.echo("==> Exporting CSV...")
    bqrs_dir = database / "results" / "linux-ql" / "kernel-queries"

    if not bqrs_dir.is_dir():
        click.echo("    No BQRS files found — CSV export skipped.")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_files: list[Path] = []

    for bqrs in sorted(bqrs_dir.rglob("*.bqrs")):
        csv_name = bqrs.stem + ".csv"
        csv_path = output_dir / csv_name
        subprocess.run(
            [
                "codeql",
                "bqrs",
                "decode",
                str(bqrs),
                "--format=csv",
                f"--output={csv_path}",
            ],
            check=True,
        )
        click.echo(f"    {csv_path}")
        csv_files.append(csv_path)

    return csv_files
