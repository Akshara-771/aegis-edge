#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/firmware/app/build-tflm"
ELF="$BUILD_DIR/zephyr/zephyr.elf"
RENODE_SCRIPT="$PROJECT_ROOT/tests/renode/aegis.resc"

echo "======================================"
echo "       AEGIS EDGE RENODE TEST"
echo "======================================"

echo "[1/2] Checking firmware..."

if [ ! -f "$ELF" ]; then
    echo "ERROR: Firmware ELF not found:"
    echo "$ELF"
    exit 1
fi

echo "Firmware: OK"
echo
echo "[2/2] Starting Renode..."

renode "$RENODE_SCRIPT"
