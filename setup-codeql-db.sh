#!/usr/bin/env bash
set -euo pipefail

# env
# LINUXSRC: path to the linux kernel source
# codeql is installed

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

# input
# --kernel-version / -v: kernel version to build
# --config / -c: kernel config to use

# usage
function usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -v, --kernel-version <version>  Kernel version to build (default: research-v5.10)"
    echo "  -c, --config <config>           Kernel config to use (default: defconfig)"
    exit 1
}

# defaults
VERSION="research-v5.10"
CONFIG="defconfig"

# parse input
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
    -v | --kernel-version)
        VERSION="$2"
        shift
        shift
        ;;
    -c | --config)
        CONFIG="$2"
        shift
        shift
        ;;
    *)
        usage
        ;;
    esac
done
BUILD_DIR="$PWD/linux-$VERSION"

function prepare_kernel {
    echo "Preparing kernel"
    git -C "$LINUXSRC" checkout "$VERSION"
    make -C $LINUXSRC O=$BUILD_DIR $CONFIG
    make -C "$LINUXSRC" O="$BUILD_DIR" prepare
}

function build_with_codeql {
    echo "Building kernel with CodeQL"
    CODEQL_DB="linux-$VERSION-codeql.db"
    codeql database create $CODEQL_DB --language=cpp --source-root=$LINUXSRC --command="make -C $LINUXSRC O=$BUILD_DIR -j$(nproc)"
}

prepare_kernel
build_with_codeql
