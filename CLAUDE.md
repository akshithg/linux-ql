# Linux CodeQL Experiments

CodeQL static analysis queries for the Linux kernel.

## Prerequisites

- `codeql` CLI installed and on PATH
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Local Linux kernel source (pass via `--source`) or a tarball URL (pass via `--url`)

## Setup

```bash
uv sync
```

## Commands

```bash
# Build CodeQL database (default: kernel v6.13, x86_64, defconfig)
uv run linux-ql build -S /path/to/linux
uv run linux-ql build -S /path/to/linux -v <tag> -a <arch> -c <config>
uv run linux-ql build -u <tarball-url> -a arm64

# Run query suites
uv run linux-ql query -d <database> -s all
uv run linux-ql query -d <database> -s heap --csv

# Docker build (macOS / no cross-compilers)
uv run linux-ql docker -a arm64 -S /path/to/linux -- -v v6.13
uv run linux-ql docker -a riscv --toolchain gcc-14 -S /path/to/linux -- -v v6.13

# Run standard CodeQL queries
codeql database analyze <database> --format=sarif-latest --output=results.sarif -- codeql/cpp-queries

# Run Trail of Bits queries (install first: codeql pack download trailofbits/cpp-queries)
codeql database analyze <database> --format=sarif-latest --output=tob.sarif -- trailofbits/cpp-queries

# Makefile shortcuts
make check                             # lint + format check + test
make db SOURCE=/path/to/linux          # build CodeQL database
make query DB=<database> SUITE=heap    # run queries

# CI: monthly database builds (also manual via workflow_dispatch)
# See .github/workflows/build-db.yml
gh workflow run build-db.yml
gh workflow run build-db.yml -f kernel_version=v6.19 -f arch=arm64

# Local workflow validation (act must be installed separately)
# Use for quick iteration on shell logic and matrix computation;
# not a substitute for real GitHub runners (missing tools, no artifacts).
act -W .github/workflows/build-db.yml --matrix arch:x86_64 --matrix kernel:v6.19
```

## Structure

- `src/linux_ql/` — Python CLI (`click`-based): build, query, docker subcommands
- `Dockerfile` / `docker` subcommand — Per-arch TuxMake-based build environment
- `queries/codeql-pack.yml` — Pack definition: `linux-ql/kernel-queries` 0.1.0
- `queries/lib/` — Shared libraries (KernelSlab, KernelFunc, KernelAlloc)
- `queries/heap/` — Heap exploitation queries (kmalloc, kfree, func ptrs)
- `queries/structures/` — Struct layout and config queries
- `queries/init/` — Init-section cross-call detection
- `queries/taint/` — Taint tracking (size_t truncation)
- `queries/suites/` — Query suite definitions (all, heap, structures, security)

## Gotchas

- Database files (`*.db`) and kernel build dirs (`linux-*`) are gitignored
- The DB filename includes version and arch: `linux-<version>-<arch>-codeql.db`
- `linux-ql build` runs `make -j$(nproc)` — ensure enough RAM
- CodeQL database creation is slow (~30 min+ depending on config and hardware)
- Cross-compilation requires the target toolchain (or use Docker)
- Query pack is at `queries/` root — use `codeql pack install queries/` to resolve deps
