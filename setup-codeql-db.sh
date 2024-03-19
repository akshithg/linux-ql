#!/usr/bin/env bash
set -euo pipefail

# assert codeql is installed
command -v codeql >/dev/null 2>&1 || {
    echo >&2 "CodeQL is not installed.  Aborting."
    exit 1
}

# assert LINUXSRC is set
if [ -z ${LINUXSRC+x} ]; then
    echo >&2 "LINUXSRC is not set.  Aborting."
    exit 1
fi

VERSION="research-v5.10"
CONFIG="defconfig"
BUILD_DIR="$PWD/linux"

function prepare_kernel {
    echo "Preparing kernel"
    git -C "$LINUXSRC" checkout "$VERSION"
    make -C $LINUXSRC O=$BUILD_DIR $CONFIG
    make -C "$LINUXSRC" O="$BUILD_DIR" prepare
}

function build_with_codeql {
    echo "Building kernel with CodeQL"
    codeql database create linux-codeql.db --language=cpp --source-root=$LINUXSRC --command="make -C $LINUXSRC O=$BUILD_DIR -j$(nproc)"
}

prepare_kernel
build_with_codeql
