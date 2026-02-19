ARG TUXMAKE_IMAGE=tuxmake/x86_64_gcc-13:latest
FROM ${TUXMAKE_IMAGE} AS toolchain

# TuxMake images are Debian-based and already include:
#   build-essential, bc, bison, flex, libssl-dev, libelf-dev,
#   the target cross-compiler, and kernel build deps.
# We only add what's needed for tarball/git operations.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates xz-utils git \
  && rm -rf /var/lib/apt/lists/*

FROM toolchain AS codeql

ARG CODEQL_VERSION=2.24.1

# CodeQL only ships x86_64 Linux binaries (codeql-linux64.zip).
# On arm64 Docker hosts this runs under QEMU/Rosetta emulation.
RUN curl -fsSL \
    "https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip" \
    -o /tmp/codeql.zip \
  && apt-get update && apt-get install -y --no-install-recommends unzip \
  && unzip -q /tmp/codeql.zip -d /opt \
  && rm /tmp/codeql.zip \
  && apt-get purge -y unzip && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/codeql:${PATH}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /workspace
COPY pyproject.toml uv.lock /workspace/
COPY src/ /workspace/src/
COPY queries/ /workspace/queries/

RUN uv sync --frozen
RUN uv run codeql pack install /workspace/queries/

ENTRYPOINT ["uv", "run", "linux-ql", "build"]
