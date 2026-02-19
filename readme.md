# linux-ql

CodeQL static analysis toolkit for the Linux kernel. Includes a curated set
of security-focused queries for heap exploitation research, struct layout
analysis, init-section bugs, and taint tracking.

## Prerequisites

- [CodeQL CLI](https://github.com/github/codeql-cli-binaries) on `PATH`
- [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Linux kernel source (local checkout via `--source`, or a tarball via `--url`)
- For cross-compilation: target architecture's GCC toolchain (or use Docker)

## Install

```bash
uv sync
```

## Quick start

```bash
# Build a CodeQL database (x86_64, defconfig)
uv run linux-ql build -S /path/to/linux -v v6.13

# Build for arm64
uv run linux-ql build -S /path/to/linux -v v6.13 -a arm64

# Build from a tarball
uv run linux-ql build -u https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.13.tar.xz

# Run all queries
uv run linux-ql query -d linux-v6.13-x86_64-codeql.db

# Run only heap queries with CSV export
uv run linux-ql query -d linux-v6.13-x86_64-codeql.db -s heap --csv
```

## Supported architectures

| Architecture | `--arch` value | Cross-compiler prefix |
|---|---|---|
| x86_64 | `x86_64` | (native) |
| ARM64/AArch64 | `arm64` | `aarch64-linux-gnu-` |
| ARM | `arm` | `arm-linux-gnueabihf-` |
| RISC-V | `riscv` | `riscv64-linux-gnu-` |
| MIPS | `mips` | `mips-linux-gnu-` |
| PowerPC | `powerpc` | `powerpc64-linux-gnu-` |
| s390 | `s390` | `s390x-linux-gnu-` |

## Docker (macOS / no cross-compilers)

Each architecture gets its own lean Docker image built from
[TuxMake](https://tuxmake.org/)'s per-arch base (`tuxmake/{arch}_gcc-13`).
The first run per architecture triggers a `docker build`.

```bash
# Build for arm64 (builds linux-ql-arm64 image on first run)
uv run linux-ql docker -a arm64 -S /path/to/linux -- -v v6.13

# Build for riscv from a tarball
uv run linux-ql docker -a riscv -- -u https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.13.tar.xz

# Default: x86_64
uv run linux-ql docker -S /path/to/linux -- -v v6.13

# Custom toolchain
uv run linux-ql docker -a arm64 --toolchain gcc-14 -S /path/to/linux -- -v v6.13
```

## Makefile

A Makefile is provided for common workflows:

```bash
make help                              # List all targets
make setup                             # Install dependencies
make check                             # Lint + format check + test
make db SOURCE=/path/to/linux          # Build CodeQL database
make db URL=https://cdn.kernel.org/... # Build from tarball
make db-docker SOURCE=/path/to/linux   # Build via Docker (per-arch)
make db-docker SOURCE=/p ARCH=arm64    # Docker build for arm64
make docker-build ARCH=arm64           # Build Docker image only
make query DB=linux-v6.13-x86_64-codeql.db SUITE=heap
make query-csv DB=linux-v6.13-x86_64-codeql.db
make clean                             # Remove build artifacts
```

## Query suites

| Suite | Description | Tag filter |
|---|---|---|
| `all` | Every query in the pack | — |
| `heap` | Heap exploitation analysis | `heap` |
| `structures` | Struct layout & config analysis | `structures` |
| `security` | All security-relevant queries | `security` |

## Query catalog

### Heap (`queries/heap/`)

| Query | Source | Description |
|---|---|---|
| `interesting_objects.ql` | Google | kmalloc'd structs with size, flags, flexible arrays |
| `kmallocd_structs.ql` | mebeim | kmalloc allocations mapped to slab caches |
| `kfreed_structs.ql` | mebeim | kfree'd structs with slab info |
| `kfreed_structs_with_func_ptrs.ql` | mebeim | Freed structs containing function pointers |

### Structures (`queries/structures/`)

| Query | Source | Description |
|---|---|---|
| `all_struct_sizes.ql` | flounderK | All non-zero struct sizes |
| `all_struct_fields.ql` | flounderK | Complete field layout with offsets |
| `ifdef_config.ql` | Original | `#ifdef CONFIG_*` block mapping |

### Init (`queries/init/`)

| Query | Source | Description |
|---|---|---|
| `bad_init_calls.ql` | mebeim | Non-init functions calling `__init` functions |

### Taint (`queries/taint/`)

| Query | Source | Description |
|---|---|---|
| `size_t_to_int.ql` | Original | `size_t` → `int` truncation in pointer math |

## Project structure

```
linux-ql/
├── pyproject.toml               # uv project config
├── src/linux_ql/                # Python CLI
│   ├── cli.py                   # click group: build, query, docker
│   ├── arch.py                  # Architecture map + validation
│   ├── build.py                 # Kernel source + CodeQL DB creation
│   ├── query.py                 # Query execution + CSV export
│   └── docker.py                # Docker wrapper
├── queries/
│   ├── codeql-pack.yml          # Pack: linux-ql/kernel-queries 0.1.0
│   ├── lib/                     # Shared CodeQL libraries
│   ├── heap/                    # Heap exploitation queries
│   ├── structures/              # Struct layout queries
│   ├── init/                    # Init-section bug queries
│   ├── taint/                   # Taint tracking queries
│   └── suites/                  # Query suite definitions
├── Dockerfile                   # Per-arch TuxMake base + CodeQL
├── ATTRIBUTION.md               # Source/license for vendored queries
├── CLAUDE.md                    # Project instructions for Claude Code
└── readme.md                    # This file
```

## Additional query packs

```bash
# Trail of Bits queries (install once)
codeql pack download trailofbits/cpp-queries

# Run against your database
codeql database analyze linux-v6.13-x86_64-codeql.db \
  --format=sarif-latest --output=tob.sarif -- trailofbits/cpp-queries
```

## Attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) for source, license, and author info
for each vendored query.
