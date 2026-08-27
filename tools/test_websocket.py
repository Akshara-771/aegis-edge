import asyncio
import websockets


async def main():
    uri = "ws://127.0.0.1:8000/ws"

    async with websockets.connect(uri) as websocket:
        print("Connected to Aegis Edge WebSocket")
        print("Waiting for telemetry...")

        while True:
            message = await websocket.recv()
            print(message)


if __name__ == "__main__":
    asyncio.run(main())
