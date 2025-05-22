import socket
import csv
import asyncio
import json
import signal
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import uvicorn

# === Configuration ===
UDP_IP = "192.168.0.100"
UDP_PORT = 1885
SAVE_INTERVAL = 60  # seconds

# === Globals ===
data_buffer = []
connected_clients: List[WebSocket] = []
shutdown_event = asyncio.Event()

app = FastAPI()


# === Utility Functions ===
def get_filename():
    return f"imu_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


# === Async CSV Saver ===
async def save_csv_periodically():
    while not shutdown_event.is_set():
        await asyncio.sleep(SAVE_INTERVAL)
        if data_buffer:
            filename = get_filename()
            print(f"[INFO] Saving {len(data_buffer)} entries to {filename}")
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Acc_X", "Acc_Y", "Acc_Z", "Rot_Z", "Millis"])
                writer.writerows(data_buffer[:])
            data_buffer.clear()


# === Async UDP Server ===
async def udp_server():
    loop = asyncio.get_event_loop()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(False)
        print(f"[INFO] Listening for UDP data on {UDP_IP}:{UDP_PORT}")

        while not shutdown_event.is_set():
            try:
                data, addr = await loop.sock_recvfrom(sock, 1024)
                decoded = data.decode("utf-8")
                fields = decoded.split(',')
                if len(fields) == 5:
                    acc_x = float(fields[0])
                    acc_y = float(fields[1])
                    acc_z = float(fields[2])
                    rot_z = float(fields[3])
                    timestamp = int(fields[4])
                    imu_data = {
                        "acceleration": {"x": acc_x, "y": acc_y, "z": acc_z},
                        "rotation": {"z": rot_z},
                        "timestampMillis": timestamp
                    }

                    # Send to WebSocket clients
                    for ws in connected_clients.copy():
                        try:
                            await ws.send_text(json.dumps(imu_data))
                        except:
                            connected_clients.remove(ws)

                    data_buffer.append([acc_x, acc_y, acc_z, rot_z, timestamp])
                    print(f"[DATA] {imu_data}")
                else:
                    print(f"[WARN] Malformed data received: {decoded}")
            except Exception as e:
                print(f"[ERROR] {e}")


# === WebSocket Endpoint ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("✅ WebSocket client connected")
    try:
        while True:
            await websocket.receive_text()  # optional
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print("❌ WebSocket client disconnected")


# === Shutdown Handling ===
def setup_signal_handlers():
    loop = asyncio.get_event_loop()

    def _shutdown():
        print("[INFO] Shutting down...")
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _shutdown)


# === Main ===
async def main():
    setup_signal_handlers()
    await asyncio.gather(
        udp_server(),
        save_csv_periodically(),
    )


if __name__ == "__main__":
    # Run FastAPI in background and async tasks
    config = uvicorn.Config("app2:app", host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
    server = uvicorn.Server(config)

    async def start():
        # Run both the FastAPI server and background tasks concurrently
        await asyncio.gather(
            main(),
            server.serve()
        )

    asyncio.run(start())
