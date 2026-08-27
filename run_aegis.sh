#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
UART_LOG="/tmp/aegis_uart.log"

RENODE_SCRIPT="$PROJECT_ROOT/tests/renode/aegis.resc"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

ZEPHYR_VENV="$HOME/zephyr-venv"
ML_VENV="$PROJECT_ROOT/ml-venv"

PIDS=()

cleanup() {
    echo
    echo "======================================"
    echo "       STOPPING AEGIS EDGE"
    echo "======================================"

    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done

    wait 2>/dev/null || true

    echo "Aegis Edge stopped."
}

trap cleanup INT TERM EXIT


echo "======================================"
echo "          AEGIS EDGE"
echo "======================================"
echo


# --------------------------------------------------
# 1. Check required files
# --------------------------------------------------

echo "[1/5] Checking environment..."

if [ ! -f "$RENODE_SCRIPT" ]; then
    echo "ERROR: Renode script not found:"
    echo "$RENODE_SCRIPT"
    exit 1
fi

if [ ! -d "$ML_VENV" ]; then
    echo "ERROR: ML virtual environment not found:"
    echo "$ML_VENV"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "ERROR: Frontend dependencies not installed."
    echo "Run:"
    echo "  cd frontend && npm install"
    exit 1
fi

echo "Environment: OK"
echo


# --------------------------------------------------
# 2. Clear UART log
# --------------------------------------------------

echo "[2/5] Clearing UART log..."

: > "$UART_LOG"

echo "UART log: $UART_LOG"
echo


# --------------------------------------------------
# 3. Start FastAPI backend
# --------------------------------------------------

echo "[3/5] Starting FastAPI backend..."

cd "$PROJECT_ROOT"

source "$ML_VENV/bin/activate"

uvicorn tools.backend:app \
    --host 127.0.0.1 \
    --port 8000 &

BACKEND_PID=$!
PIDS+=("$BACKEND_PID")

echo "Backend PID: $BACKEND_PID"
echo "Backend: http://127.0.0.1:8000"
echo


# --------------------------------------------------
# 4. Start telemetry bridge + Renode
# --------------------------------------------------

echo "[4/5] Starting telemetry + Renode..."

python3 tools/telemetry_bridge.py &
TELEMETRY_PID=$!
PIDS+=("$TELEMETRY_PID")

echo "Telemetry bridge PID: $TELEMETRY_PID"

renode "$RENODE_SCRIPT" &
RENODE_PID=$!
PIDS+=("$RENODE_PID")

echo "Renode PID: $RENODE_PID"
echo


# --------------------------------------------------
# 5. Start frontend
# --------------------------------------------------

echo "[5/5] Starting frontend..."

cd "$FRONTEND_DIR"

npm run dev -- --host 127.0.0.1 &
FRONTEND_PID=$!
PIDS+=("$FRONTEND_PID")

echo "Frontend PID: $FRONTEND_PID"
echo


echo "======================================"
echo "       AEGIS EDGE IS RUNNING"
echo "======================================"
echo
echo "Dashboard: http://127.0.0.1:5173"
echo "Backend:   http://127.0.0.1:8000"
echo "UART log:  $UART_LOG"
echo
echo "Press Ctrl+C to stop everything."
echo

wait
