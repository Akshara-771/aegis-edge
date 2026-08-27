import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Aegis Edge Backend")

clients = set()

# Telemetry history for the current Renode run.
# The dashboard can restore this history after a refresh.
telemetry_history = []

# Prevent unbounded memory growth during very long runs.
MAX_HISTORY = 5000

# Used to detect when a new Renode run has started.
last_timestamp = None


@app.get("/")
async def root():
    return {
        "name": "Aegis Edge Backend",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "clients": len(clients),
        "history": len(telemetry_history),
    }


@app.post("/telemetry")
async def receive_telemetry(telemetry: dict):
    global last_timestamp

    timestamp = telemetry.get("timestamp")

    # Detect a fresh Renode run.
    # Firmware timestamp should restart from a small value.
    if (
        timestamp is not None
        and last_timestamp is not None
        and timestamp < last_timestamp
    ):
        telemetry_history.clear()

    telemetry_history.append(telemetry)

    if len(telemetry_history) > MAX_HISTORY:
        del telemetry_history[:-MAX_HISTORY]

    last_timestamp = timestamp

    await broadcast_telemetry(telemetry)

    return {
        "status": "received",
        "telemetry": telemetry,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        # Send existing telemetry history first.
        await websocket.send_text(
            json.dumps(
                {
                    "type": "history",
                    "data": telemetry_history,
                }
            )
        )

        # Then keep the connection alive.
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        clients.discard(websocket)

    except Exception:
        clients.discard(websocket)


async def broadcast_telemetry(telemetry):
    message = json.dumps(telemetry)

    disconnected = set()

    for client in clients:
        try:
            await client.send_text(message)
        except Exception:
            disconnected.add(client)

    for client in disconnected:
        clients.discard(client)
