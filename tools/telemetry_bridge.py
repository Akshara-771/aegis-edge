#!/usr/bin/env python3

import json
import os
import sys
import time

import requests


BACKEND_URL = "http://127.0.0.1:8000/telemetry"
UART_LOG = "/tmp/aegis_uart.log"


def parse_telemetry(line):
    line = line.strip()

    if not line.startswith("CSV,"):
        return None

    parts = line.split(",")

    if len(parts) != 8:
        return None

    (
    _,
    timestamp,
    temperature,
    voltage,
    rpm,
    fault,
    ml_prediction,
    rule_prediction,
    ) = parts

    try:
       return {
    "timestamp": int(timestamp),
    "temperature": float(temperature),
    "voltage": float(voltage),
    "rpm": int(rpm),
    "fault": fault,
    "ml_prediction": ml_prediction,
    "rule_prediction": rule_prediction,
    }

    except ValueError:
        return None


def send_telemetry(telemetry):
    try:
        response = requests.post(
            BACKEND_URL,
            json=telemetry,
            timeout=2,
        )

        response.raise_for_status()

        print(
            f"Sent telemetry: "
            f"{telemetry['timestamp']} ms | "
            f"{telemetry['fault']}",
            flush=True,
        )

    except requests.RequestException as error:
        print(
            f"Failed to send telemetry: {error}",
            file=sys.stderr,
            flush=True,
        )


def follow_file(path):
    """
    Follow a growing file and handle file replacement/rotation,
    similar to `tail -F`.
    """

    file = None
    inode = None

    while True:
        try:
            stat = os.stat(path)

            # File doesn't exist yet.
            if file is None:
                file = open(path, "r")
                file.seek(0, os.SEEK_END)
                inode = stat.st_ino

                print(
                    f"Opened UART log: {path}",
                    flush=True,
                )

            # File was replaced/rotated.
            elif stat.st_ino != inode:
                print(
                    "UART log changed, reopening...",
                    flush=True,
                )

                file.close()

                file = open(path, "r")
                file.seek(0, os.SEEK_END)
                inode = stat.st_ino

            line = file.readline()

            if line:
                yield line
            else:
                time.sleep(0.1)

        except FileNotFoundError:
            if file is not None:
                file.close()
                file = None
                inode = None

            print(
                f"Waiting for UART log: {path}",
                flush=True,
            )

            time.sleep(1)

def main():
    print("Aegis Edge Telemetry Bridge", flush=True)
    print(f"Watching: {UART_LOG}", flush=True)
    print(f"Backend:  {BACKEND_URL}", flush=True)

    for line in follow_file(UART_LOG):
        telemetry = parse_telemetry(line)

        if telemetry is not None:
            send_telemetry(telemetry)


if __name__ == "__main__":
    main()
