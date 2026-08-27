#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/firmware/app/build-tflm"
ELF="$BUILD_DIR/zephyr/zephyr.elf"
RENODE_SCRIPT="$PROJECT_ROOT/tests/renode/aegis.resc"
UART_LOG="/tmp/aegis_uart.log"

echo "======================================"
echo "       AEGIS EDGE RENODE TEST"
echo "======================================"

echo "[1/3] Checking firmware..."

if [ ! -f "$ELF" ]; then
    echo "ERROR: Firmware ELF not found:"
    echo "$ELF"
    exit 1
fi

echo "Firmware: OK"
echo

echo "[2/3] Clearing UART log..."

: > "$UART_LOG"

echo "UART log: $UART_LOG"
echo

echo "[3/3] Starting Renode..."

renode "$RENODE_SCRIPT"
