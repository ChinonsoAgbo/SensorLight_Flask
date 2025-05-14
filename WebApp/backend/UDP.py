import socket
import threading
import csv
import time
from datetime import datetime
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

# UDP server settings
UDP_IP = "0.0.0.0"
UDP_PORT = 1884

data_buffer = []
lock = threading.Lock()
last_save_time = time.time()
SAVE_INTERVAL = 60  # seconds
connected_clients: List[WebSocket] = []  # For WebSocket clients

# FastAPI Setup for WebSocket
app = FastAPI()

# Function to generate CSV filename with timestamp
def get_filename():
    return f"imu_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Save data to CSV every 1 minute
def save_csv_periodically():
    global data_buffer, last_save_time
    while True:
        time.sleep(SAVE_INTERVAL)  # wait 1 minute
        with lock:
            if data_buffer:
                filename = get_filename()
                print(f"[INFO] Saving {len(data_buffer)} entries to {filename}")
                with open(filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Acc_X", "Acc_Y", "Acc_Z", "Rot_Z", "Millis"])
                    writer.writerows(data_buffer)
                    data_buffer = []
                last_save_time = time.time()

# Start the background saving thread
threading.Thread(target=save_csv_periodically, daemon=True).start()

# Create and bind UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(1.0)  # Makes Ctrl+C responsive
print(f"[INFO] Listening for UDP data on port {UDP_PORT}...")

# WebSocket connection handler
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print("✅ WebSocket client connected")
    try:
        while True:
            await websocket.receive_text()  # optionally handle input
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("❌ WebSocket client disconnected")

# Process received UDP data
def process_udp_data():
    global data_buffer
    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
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

                    for ws in connected_clients:
                        try:
                            ws.send_text(json.dumps(imu_data))
                        except:
                            continue

                    with lock:
                        data_buffer.append([acc_x, acc_y, acc_z, rot_z, timestamp])
                    print(f"[DATA] {imu_data}")
                else:
                    print(f"[WARN] Malformed data received: {decoded}")

            except socket.timeout:
                continue  # Just ignore and keep listening

    except KeyboardInterrupt:
        print("[INFO] Shutting down UDP server")
        sock.close()

# Start the UDP data receiving in a background thread
threading.Thread(target=process_udp_data, daemon=True).start()

